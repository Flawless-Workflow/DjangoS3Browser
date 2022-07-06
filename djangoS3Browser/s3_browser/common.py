from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated, APIException
from .operations import OperationsMixin


class OperationView(OperationsMixin, APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def set_user_bucket(self):
        if getattr(settings, "USE_SEPARATE_USER_BUCKET", False):
            user = self.request.user
            if not user.is_authenticated:
                raise NotAuthenticated()

            if user.groups.filter(name="school").exists():
                self.bucket_name = user.school.bucket_name
                return
            elif user.is_staff:
                bucket_name = self.request.query_params.get("bucket", None)
                if bucket_name is not None:
                    self.bucket_name = bucket_name
                    return
            raise APIException(code=404, detail=_("Set Bucket name"))