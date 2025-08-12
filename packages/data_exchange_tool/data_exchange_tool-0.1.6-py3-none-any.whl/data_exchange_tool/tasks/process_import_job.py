import traceback
from io import BytesIO

import polars as pl
from django.conf import settings
from django.utils import timezone

from celery import shared_task
from data_exchange_tool.data_exchange.model_importer import (
    GenericModelImporterPolars,
)
from data_exchange_tool.utils import get_serializer


@shared_task(
    name="data_exchange.process_import_job_task",
    queue=getattr(settings, "DATA_EXCHANGE_IMPORT_QUEUE", "data_exchange_shared_queue"),
)
def process_import_job_task(job_id: int = None, job_instance: "ImportJob" = None):
    from data_exchange_tool.models.import_job import ImportJob, ImportJobStatus

    job = job_instance or ImportJob.objects.get(pk=job_id)

    try:
        import_status = ImportJobStatus.IMPORT_IN_PROGRESS
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
            importer = GenericModelImporterPolars(
                model=job.import_content_type,
                serializer_class=serializer_class,
                lookup_fields=serializer_class.Meta.lookup_fields,
                lookup_fields_mapping=serializer_class.Meta.lookup_fields_mapping,
            )
            importer._process_data(df)
            import_status = ImportJobStatus.IMPORT_SUCCEEDED
    except Exception as e:
        import_status = ImportJobStatus.IMPORT_FAILED
        status_message = traceback.format_exc()

    job.import_status = import_status
    job.status_message = status_message

    job.finished_at = timezone.now()
    job.save()
