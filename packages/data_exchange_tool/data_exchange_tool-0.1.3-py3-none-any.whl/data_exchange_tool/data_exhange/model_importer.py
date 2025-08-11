import csv
import polars as pl

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from data_exchange_tool.exceptions import RowProcessingException


class GenericModelImporterPolars:
    def __init__(
        self,
        model: "ContentType",
        serializer_class,
        lookup_fields,
        lookup_fields_mapping=None,
        import_column_mapping=None,
        request=None,
    ):
        self.model = model.model_class()
        self.serializer_class = serializer_class
        self.lookup_fields = lookup_fields or []
        self.lookup_fields_mapping = lookup_fields_mapping or {}
        self.import_column_mapping = import_column_mapping or {}
        self.request = request
        self.row_errors_list = []

    def _determine_csv_delimiter(self, file):
        file.seek(0)
        sample = file.read(1024)
        if isinstance(sample, bytes):
            sample = sample.decode("utf-8")
        file.seek(0)
        sniffer = csv.Sniffer()
        return sniffer.sniff(sample).delimiter

    def _read_file(self, file):
        file_name = file.name.lower()
        try:
            if file_name.endswith(".csv"):
                delimiter = self._determine_csv_delimiter(file)
                return pl.read_csv(file, separator=delimiter)
            elif file_name.endswith((".xlsx", ".xls")):
                return pl.read_excel(file)
            else:
                raise ValueError("Unsupported file type")
        except Exception as e:
            raise ValueError(f"Error leyendo fichero: {e}")

    def _include_extra_df_data(self, df: pl.DataFrame) -> pl.DataFrame:
        return df

    def _include_extra_data(self, data: list) -> list:
        return data

    def _determine_serializer(self, instance, row):
        kwargs = {"context": {"request": self.request}} if self.request else {}
        if instance:
            return self.serializer_class(instance, data=row, **kwargs)
        return self.serializer_class(data=row, **kwargs)

    def get_instance(self, row: dict):
        try:
            if self.lookup_fields_mapping:
                filter_kwargs = {
                    self.lookup_fields_mapping.get(f, f): row.get(f)
                    for f in self.lookup_fields
                }
            else:
                filter_kwargs = {f: row.get(f) for f in self.lookup_fields}
            return self.model.objects.get(**filter_kwargs)
        except (ObjectDoesNotExist, KeyError):
            return None

    def _append_error_to_list(self, row_number, row, serializer):
        row_ref = [f"{f}: {row.get(f)}" for f in self.lookup_fields]
        self.row_errors_list.append(
            {
                "row_number": row_number,
                "data": row_ref,
                "errors": serializer.errors,
            }
        )

    def _format_errors(self) -> list:
        formatted = []
        for err in self.row_errors_list:
            formatted.append(
                {
                    "row_number": err["row_number"],
                    "reference": err["data"],
                    "errors": {
                        fld: [str(d) for d in det] for fld, det in err["errors"].items()
                    },
                }
            )
        return formatted

    def generate_preview(self, df: pl.DataFrame) -> tuple:
        if self.import_column_mapping:
            df = df.rename(self.import_column_mapping)
        df = self._include_extra_df_data(df)
        records = df.to_dicts()
        records = self._include_extra_data(records)
        preview = []
        preview_stats = {
            "created": 0,
            "updated": 0,
            "error": 0,
            "deleted": 0,
            "skipped": 0,
            "total_rows": len(records),
        }
        for idx, row in enumerate(records, start=2):
            inst = self.get_instance(row)
            serializer = self._determine_serializer(inst, row)

            if not serializer.is_valid():
                action = "error"
                message = serializer.errors
                preview_stats["error"] += 1
            elif inst:
                changes = {}
                for field, new_value in serializer.validated_data.items():
                    old_value = getattr(inst, field, None)
                    if old_value != new_value:
                        changes[field] = {"old": old_value, "new": new_value}
                        row[field] = (
                            f"<s style='color:red'>{old_value}</s> → <b>{new_value}</b>"
                        )

                if changes:
                    preview_stats["updated"] += 1
                    action = "updated"
                    message = changes
                else:
                    action = "skipped"
                    message = "Sin cambios detectados"
                    preview_stats["skipped"] += 1
            else:
                action = "created"
                preview_stats["created"] += 1
                message = ""

            preview.append({**row, "import_action": action, "import_message": message})

        return preview, preview_stats

    def _after_create_actions(self, instance, serializer):
        pass

    def _after_update_actions(self, instance, serializer):
        pass

    def _after_save_actions(self, existing_instance, instance, serializer):
        if existing_instance:
            self._after_update_actions(instance, serializer)
        else:
            self._after_create_actions(instance, serializer)

    def _process_data(self, df: pl.DataFrame) -> list:
        self.row_errors_list = []
        if self.import_column_mapping:
            df = df.rename(self.import_column_mapping)
        df = self._include_extra_df_data(df)
        records = df.to_dicts()
        records = self._include_extra_data(records)
        processed = []
        with transaction.atomic():
            for idx, row in enumerate(records, start=2):
                inst = self.get_instance(row)
                serializer = self._determine_serializer(inst, row)
                if not serializer.is_valid():
                    self._append_error_to_list(idx, row, serializer)
                    continue
                obj = serializer.save()
                self._after_save_actions(inst, obj, serializer)
                processed.append(serializer.data)
            if self.row_errors_list:
                raise RowProcessingException(self._format_errors())
        return processed
