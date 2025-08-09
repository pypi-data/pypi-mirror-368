from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.urls.base import reverse
from django.utils.html import format_html

from data_exchange_tool.admin.filters import (
    CreationTimestampFilter,
    UpdateTimestampFilter,
)
from data_exchange_tool.admin.messages import (
    ERROR_MODAL_MSG,
    STATUS_HTML_TAG,
    ALLOWED_PREVIEW_STATUS_MSG,
    ALLOWED_CONFIRM_STATUS_MSG,
    CONFIRM_WITH_ERRORS_MSG,
)
from data_exchange_tool.models.import_job import (
    ImportJob,
    ImportJobStatus,
)


class ImportJobAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class GenericImporterModelAdmin(ImportJobAdmin):
    readonly_fields = [
        "file_hash",
        "async_task_id",
        "changes_preview_file",
        "error_rows",
        "import_status",
        "initiated_by",
        "inserted_rows",
        "status_message",
        "total_rows",
        "updated_rows",
        "import_content_type",
        "import_serializer_class_name",
    ]
    list_display = [
        "id",
        "formatted_creation_timestamp",
        "formatted_update_timestamp",
        "download_uploaded_file",
        "initiated_by",
        "total_rows_qty",
        "inserted_rows_qty",
        "updated_rows_qty",
        "error_rows_qty",
        "status_tag",
        "status_message_popup",
        "download_changes_preview_file",
        "actions_column",
    ]
    list_filter = [
        CreationTimestampFilter,
        UpdateTimestampFilter,
        "import_status",
        "initiated_by",
    ]
    actions = []
    list_per_page = 15
    ordering = ["-creation_timestamp"]

    def preview_changes_single(self, request, object_id):
        obj = self.get_object(request, object_id)
        preview_allowed_states = ImportJobStatus.PREVIEW_ALLOWED_STATES
        error_message = self._check_jobs_already_in_progress(obj, request)

        if not error_message and obj.import_status not in preview_allowed_states:
            error_message = ALLOWED_PREVIEW_STATUS_MSG.format(
                obj.import_status, preview_allowed_states
            )
        if error_message:
            messages.error(request, error_message)
        else:
            obj.preview_job()
        return redirect(request.META.get("HTTP_REFERER", "/admin/"))

    def confirm_changes_single(self, request, object_id):
        obj = self.get_object(request, object_id)

        error_message = self._check_jobs_already_in_progress(obj, request)

        importable_states = ImportJobStatus.IMPORTABLE_STATES
        if (
            not error_message
            and obj.import_status == ImportJobStatus.PREVIEW_SUCCEEDED
            and obj.error_rows
            and obj.error_rows > 0
        ):
            error_message = CONFIRM_WITH_ERRORS_MSG
        elif not error_message and obj.import_status not in importable_states:
            error_message = ALLOWED_CONFIRM_STATUS_MSG.format(
                obj.import_status, importable_states
            )

        if error_message:
            messages.error(request, error_message)
        else:
            obj.confirm_import()

        return redirect(request.META.get("HTTP_REFERER", "/admin/"))

    def _check_jobs_already_in_progress(self, obj, request):
        same_type_in_progress = obj.__class__.objects.filter(
            import_content_type=obj.import_content_type,
            import_status__in=(
                ImportJobStatus.PREVIEW_IN_PROGRESS,
                ImportJobStatus.PREVIEW_FAILED,
                ImportJobStatus.PREVIEW_SUCCEEDED,
                ImportJobStatus.IMPORT_IN_PROGRESS,
            ),
        ).exclude(pk=obj.pk)
        error_message = None
        if same_type_in_progress.exists():
            error_message = (
                "Same type job in progress {}. Finish or cancel that job".format(
                    ", ".join([str(j.pk) for j in same_type_in_progress])
                )
            )
        return error_message

    def cancel_job_single(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj.import_status not in ImportJobStatus.CANCELLED:
            obj.import_status = ImportJobStatus.CANCELLED
            obj.save()
            messages.info(request, "Job cancelled successfully")
        return redirect(request.META.get("HTTP_REFERER", "/admin/"))

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if "uploaded_file" in fields:
            fields.remove("uploaded_file")
            fields.insert(0, "uploaded_file")
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly = self.readonly_fields
        if obj and obj.import_status not in (
            ImportJobStatus.CREATED,
            ImportJobStatus.PREVIEW_FAILED,
        ):
            readonly.append("uploaded_file")
        return set(readonly)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/preview-changes/",
                self.admin_site.admin_view(self.preview_changes_single),
                name="data_exchange_tool_importjob_preview_changes",
            ),
            path(
                "<int:object_id>/confirm-changes/",
                self.admin_site.admin_view(self.confirm_changes_single),
                name="data_exchange_tool_importjob_confirm_changes",
            ),
            path(
                "<int:object_id>/cancel-job/",
                self.admin_site.admin_view(self.cancel_job_single),
                name="data_exchange_tool_importjob_cancel_job_single",
            ),
        ]
        return custom_urls + urls

    @property
    def column_mapping(self):
        raise ValueError()

    def status_message_popup(self, obj):
        if not obj.status_message:
            return ""
        message_id = f"msg_{obj.id}"
        safe_message = (
            obj.status_message.replace('"', "&quot;") if obj.status_message else ""
        )
        return format_html(
            ERROR_MODAL_MSG,
            message_id,
            message_id,
            message_id,
            safe_message,
        )

    def status_tag(self, obj):
        color_map = {
            ImportJobStatus.CREATED: "gray",
            ImportJobStatus.CANCELLED: "rosybrown",
            ImportJobStatus.PREVIEW_IN_PROGRESS: "cadetblue",
            ImportJobStatus.PREVIEW_FAILED: "indianred",
            ImportJobStatus.PREVIEW_SUCCEEDED: "yellowgreen",
            ImportJobStatus.IMPORT_IN_PROGRESS: "blue",
            ImportJobStatus.IMPORT_SUCCEEDED: "green",
            ImportJobStatus.IMPORT_FAILED: "red",
        }
        color = color_map.get(obj.import_status, "black")
        return format_html(
            STATUS_HTML_TAG,
            color,
            obj.import_status.replace("_", " ").title(),
        )

    def total_rows_qty(self, obj):
        return obj.total_rows

    def inserted_rows_qty(self, obj):
        return obj.inserted_rows

    def updated_rows_qty(self, obj):
        return obj.updated_rows

    def error_rows_qty(self, obj):
        return obj.error_rows

    def formatted_creation_timestamp(self, obj):
        return obj.creation_timestamp.strftime("%Y/%m/%d %H:%M:%S")

    def formatted_update_timestamp(self, obj):
        return obj.update_timestamp.strftime("%Y/%m/%d %H:%M:%S")

    def actions_column(self, obj):
        preview_url = reverse(
            "admin:data_exchange_tool_importjob_preview_changes", args=[obj.pk]
        )
        confirm_url = reverse(
            "admin:data_exchange_tool_importjob_confirm_changes", args=[obj.pk]
        )
        cancel_url = reverse(
            "admin:data_exchange_tool_importjob_cancel_job_single", args=[obj.pk]
        )
        preview_button = ""
        if obj.import_status in ImportJobStatus.PREVIEW_ALLOWED_STATES:
            preview_button = (
                '<a class="button" style="background-color: yellowgreen" href="{}">Preview</a>&nbsp;'
            ).format(preview_url)
        confirm_button = ""
        if obj.import_status in ImportJobStatus.IMPORTABLE_STATES:
            confirm_button = (
                '<a class="button" style="background-color: green" href="{}" onclick="return confirm'
                "('¿Confirm job?')\">Confirm</a>&nbsp;"
            ).format(confirm_url)
        cancel_button = ""
        if obj.import_status not in ImportJobStatus.FINAL_STATES:
            cancel_button = (
                '<a class="button" style="background-color: rosybrown" href="{}" '
                'onclick="return confirm'
                "('¿Cancel Job?')\">Cancel</a>"
            ).format(cancel_url)

        return format_html(preview_button + confirm_button + cancel_button)

    def download_changes_preview_file(self, obj):
        if obj.changes_preview_file:
            return format_html(
                '<a href="{}" download>Download</a>', obj.changes_preview_file.url
            )
        return "-"

    def download_uploaded_file(self, obj):
        if obj.uploaded_file:
            return format_html(
                '<a href="{}" download>Download</a>', obj.uploaded_file.url
            )
        return "-"

    download_uploaded_file.short_description = "Uploaded File"
    download_changes_preview_file.short_description = "Preview File"
    total_rows_qty.short_description = "Total"
    inserted_rows_qty.short_description = "Create"
    updated_rows_qty.short_description = "Update"
    error_rows_qty.short_description = "Error"
    status_tag.short_description = "Status"
    status_message_popup.short_description = "Msg"
    formatted_creation_timestamp.short_description = "Created At"
    formatted_update_timestamp.short_description = "Updated At"

    def save_model(self, request, obj, form, change):
        if not obj.initiated_by:
            obj.initiated_by = request.user.email
        super().save_model(request, obj, form, change)


admin.site.register(ImportJob, GenericImporterModelAdmin)
