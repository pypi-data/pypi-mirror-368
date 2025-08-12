import traceback
import polars as pl

from io import BytesIO
from django.conf import settings

from celery import shared_task
from data_exchange_tool.data_exchange.model_importer import (
    GenericModelImporterPolars,
)
from data_exchange_tool.utils import convert_list_to_file_like_object, get_serializer


@shared_task(
    name="data_exchange.preview_import_task",
    queue=getattr(
        settings, "DATA_EXCHANGE_PREVIEW_QUEUE", "data_exchange_shared_queue"
    ),
)
def preview_import_task(job_id: int = None, job_instance: "ImportJob" = None):
    from data_exchange_tool.models.import_job import ImportJob, ImportJobStatus

    job = job_instance or ImportJob.objects.get(pk=job_id)

    try:
        status_message = ""

        with job.uploaded_file.open("rb") as f:
            file_data = BytesIO(f.read())
            extra_kwargs = {}
            serializer_class = get_serializer(job.import_serializer_class_name)
            if serializer_class.Meta.utf8_fields:
                extra_kwargs["dtypes"] = {}
                for field in serializer_class.Meta.utf8_fields:
                    extra_kwargs["dtypes"].update({field: pl.Utf8})

            df = pl.read_csv(
                file_data,
                **extra_kwargs,
            )

            lookup_fields = serializer_class.Meta.lookup_fields

            combined_key = df.select(
                pl.concat_str(lookup_fields, separator="|")
            ).to_series()

            duplicated_mask = combined_key.is_duplicated()

            if duplicated_mask.any():
                duplicates = df.select(lookup_fields).filter(duplicated_mask).unique()

                import_status = ImportJobStatus.PREVIEW_FAILED
                status_message = (
                    f"Duplicated rows found based on {lookup_fields}:\n{duplicates}"
                )
            else:
                importer = GenericModelImporterPolars(
                    model=job.import_content_type,
                    serializer_class=serializer_class,
                    lookup_fields=lookup_fields,
                    lookup_fields_mapping=serializer_class.Meta.lookup_fields_mapping,
                )
                preview_data, preview_stats = importer.generate_preview(df)
                preview_file = convert_list_to_file_like_object(
                    data_list=preview_data,
                    file_name=f"preview_job_{job.id}.html",
                    template_extra_kwargs=preview_stats,
                )
                job.changes_preview_file = preview_file

                job.error_rows = preview_stats["error"]
                job.total_rows = preview_stats["total_rows"]
                job.deleted_rows = preview_stats["deleted"]
                job.inserted_rows = preview_stats["created"]
                job.updated_rows = preview_stats["updated"]

                import_status = ImportJobStatus.PREVIEW_SUCCEEDED

                if job.error_rows and job.error_rows > 0:
                    import_status = ImportJobStatus.PREVIEW_FAILED
                    status_message = "Errors on file. Check preview file for details."
    except Exception as e:
        import_status = ImportJobStatus.PREVIEW_FAILED
        status_message = traceback.format_exc()

    job.import_status = import_status
    job.status_message = status_message

    job.save()
