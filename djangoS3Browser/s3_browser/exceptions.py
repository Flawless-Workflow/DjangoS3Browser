from rest_framework.exceptions import APIException

class FileException(APIException):
    code = 400
    detail = "File error"
