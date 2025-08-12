import hashlib
import os
from datetime import datetime
from uuid import uuid4

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from data_exchange_tool.storage import ModelDataExchangeS3Storage


class ImportJobStatus:
    CREATED = "CREATED"

    PREVIEW_IN_PROGRESS = "PREVIEW_IN_PROGRESS"
    PREVIEW_FAILED = "PREVIEW_FAILED"
    PREVIEW_SUCCEEDED = "PREVIEW_SUCCEEDED"

    IMPORT_IN_PROGRESS = "IMPORT_IN_PROGRESS"
    IMPORT_SUCCEEDED = "IMPORT_SUCCEEDED"
    IMPORT_FAILED = "IMPORT_FAILED"

    CANCELLED = "CANCELLED"

    CHOICES = (
        (CREATED, _("CREATED")),
        (PREVIEW_IN_PROGRESS, _("PREVIEW_IN_PROGRESS")),
        (PREVIEW_FAILED, _("PREVIEW_FAILED")),
        (PREVIEW_SUCCEEDED, _("PREVIEW_SUCCEEDED")),
        (IMPORT_IN_PROGRESS, _("IMPORT_IN_PROGRESS")),
        (IMPORT_FAILED, _("IMPORT_FAILED")),
        (IMPORT_SUCCEEDED, _("IMPORT_SUCCEEDED")),
        (CANCELLED, _("CANCELLED")),
    )
    FINAL_STATES = (IMPORT_FAILED, IMPORT_SUCCEEDED, CANCELLED)
    PREVIEW_ALLOWED_STATES = (
        CREATED,
        PREVIEW_FAILED,
    )
    IMPORTABLE_STATES = (PREVIEW_SUCCEEDED,)


class ImportJobMeta(models.base.ModelBase):
    target_model = None
    import_serializer_class = None
    model_exchange_tool_model = True

    def __new__(cls, name, bases, attrs, **kwargs):
        meta = attrs.get("Meta", None)

        target_model = None
        serializer_class = None
        import_column_mapping = None

        if meta:
            target_model = cls.__extract_meta_attr(meta, "target_model")
            serializer_class = cls.__extract_meta_attr(meta, "serializer_class")
            import_column_mapping = cls.__extract_meta_attr(
                meta, "import_column_mapping"
            )

        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)

        cls.__validate_meta_attr(new_cls, "target_model", target_model)
        cls.__validate_meta_attr(new_cls, "serializer_class", serializer_class)
        cls.__validate_meta_attr(
            new_cls, "import_column_mapping", import_column_mapping
        )

        new_cls.target_model = target_model
        new_cls.serializer_class = serializer_class
        new_cls.import_column_mapping = import_column_mapping
        new_cls.model_exchange_tool_model = True

        return new_cls

    @staticmethod
    def __validate_meta_attr(new_cls, attr_name, attr):
        if getattr(new_cls._meta, "model_exchange_tool_model", False) and attr is None:
            raise TypeError(f"{new_cls.__name__}.Meta must define `{attr_name}`")

    @staticmethod
    def __extract_meta_attr(meta, attribute_name):
        if hasattr(meta, attribute_name):
            attribute = getattr(meta, attribute_name)
            delattr(meta, attribute_name)
            return attribute
        return None


def custom_file_name(instance, filename):
    """
    Keep the original filename and add the full datetime before the extension.
    Example: pdfs/document_2025-07-31T14-30-59.pdf
    """
    name, ext = os.path.splitext(filename)
    now_iso = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    return f"{name}_{now_iso}{ext}"


class ImportJob(models.Model, metaclass=ImportJobMeta):
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    update_timestamp = models.DateTimeField(auto_now=True)
    import_status = models.CharField(
        max_length=32,
        choices=ImportJobStatus.CHOICES,
        default=ImportJobStatus.CREATED,
    )

    uploaded_file = models.FileField(
        verbose_name=_("Uploaded file"),
        blank=True,
        null=True,
        storage=ModelDataExchangeS3Storage(base_dir="uploaded_files"),
        upload_to=custom_file_name,
    )
    file_hash = models.CharField(max_length=255, blank=True, null=True)

    async_task_id = models.CharField(
        verbose_name=_("Task ID"),
        max_length=255,
        blank=True,
        null=True,
    )

    initiated_by = models.CharField(
        verbose_name=_("Initiated by"),
        max_length=255,
        blank=True,
        null=True,
    )

    changes_preview_file = models.FileField(
        verbose_name=_("Preview changes file"),
        blank=True,
        null=True,
        storage=ModelDataExchangeS3Storage(base_dir="preview_files"),
        upload_to=custom_file_name,
    )

    total_rows = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Total rows"),
    )
    inserted_rows = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Inserted rows"),
    )
    updated_rows = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Updated rows"),
    )
    error_rows = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Error rows"),
    )

    import_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
    )
    import_serializer_class_name = models.CharField(
        verbose_name=_("Import serializer class name"),
        max_length=255,
        blank=True,
        null=True,
        editable=False,
    )

    status_message = models.TextField()

    class Meta:
        ordering = ["-initiated_by"]

    @property
    def slug(self):
        now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        return f"import_job/job_id/{self.id}/{now}"

    def save(self, *args, **kwargs):
        if not self.import_content_type:
            self.import_content_type = ContentType.objects.get_for_model(
                self.target_model,
            )
        if not self.import_serializer_class_name:
            self.import_serializer_class_name = self.serializer_class

        file_hash = self._determine_hash()

        if self.uploaded_file and (not self.file_hash or self.file_hash != file_hash):
            self.file_hash = file_hash
        return super().save(*args, **kwargs)

    def _determine_hash(self):
        self.uploaded_file.seek(0)
        file_hash = hashlib.sha256(self.uploaded_file.read()).hexdigest()
        self.uploaded_file.seek(0)
        return file_hash

    def preview_job(self):
        from data_exchange_tool.tasks import preview_import_task

        custom_task_id = f"data_exchange_preview_job_{self.id}__{uuid4()}"
        preview_import_task.apply_async(
            kwargs={"job_id": self.id},
            task_id=custom_task_id,
        )
        self.async_task_id = custom_task_id
        self.import_status = ImportJobStatus.PREVIEW_IN_PROGRESS
        self.save()

    def confirm_import(self):
        from data_exchange_tool.tasks import process_import_job_task
        custom_task_id = f"data_exchange_confirm_import_job_{self.id}__{uuid4()}"

        process_import_job_task.apply_async(
            kwargs={"job_id": self.id},
            task_id=custom_task_id,
        )
        self.async_task_id = custom_task_id
        self.import_status = ImportJobStatus.IMPORT_IN_PROGRESS
        self.save()
