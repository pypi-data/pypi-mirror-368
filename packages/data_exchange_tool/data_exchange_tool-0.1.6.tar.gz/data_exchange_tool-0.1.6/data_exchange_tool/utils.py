import io

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.loader import render_to_string
from django.utils.module_loading import import_string


def convert_list_to_file_like_object(data_list, file_name, **template_extra_kwargs):
    if not data_list:
        raise ValueError("Empty data list")

    headers = list(data_list[0].keys())
    html_str = render_to_string(
        "import_preview_template.html",
        {
            "headers": headers,
            "data": data_list,
            **template_extra_kwargs,
        },
    )

    encoded = html_str.encode("utf-8")
    file_io = io.BytesIO(encoded)
    file_io.seek(0)

    return InMemoryUploadedFile(
        file=file_io,
        field_name=None,
        name=file_name,
        content_type="text/html",
        size=len(encoded),
        charset="utf-8",
    )


def get_serializer(serializer_path):
    return import_string(serializer_path)
