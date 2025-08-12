from rest_framework.exceptions import APIException


class RowProcessingException(APIException):
    status_code = 400
    default_detail = "Errors occurred while processing rows."
    default_code = "row_processing_error"

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
