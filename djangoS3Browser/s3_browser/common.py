from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated, APIException
from .operations import OperationsMixin
from .utils import import_callable


class OperationView(OperationsMixin, APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def set_user_bucket(self):
        """
        Set user bucket based on settings variable
        set USE_SEPARATE_USER_BUCKET= True in settings.py to customize a function
        otherwise set to false and the user bucket will be the same as the AWS_STORAGE_BUCKET_NAME
        """
        if getattr(settings, "USE_SEPARATE_USER_BUCKET", False):
            set_bucket_func = import_callable(settings.SET_USER_BUCKET_FUNC)
            self.bucket_name = set_bucket_func(
                self.request.user, self.request.query_params.get("bucket")
            )
        else:
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
