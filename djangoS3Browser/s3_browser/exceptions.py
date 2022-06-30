from rest_framework.exceptions import APIException

class FileException(APIException):
    code = 500
    detail = "File error"
