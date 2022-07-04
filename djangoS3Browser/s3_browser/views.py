import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status

from .operations import OperationsMixin
from .serializers import *
from .common import OperationView

"fetch the directories within the selected folder"


class GetFolderItemsAPIView(OperationView):
    allowed_methods = ["get"]

    @extend_schema(
        responses={200: FileSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="main_folder",
                type=OpenApiTypes.STR,
                description=(
                    "The main folder to get the items from. " "Always starts with '-'."
                ),
                location=OpenApiParameter.PATH,
            )
        ],
    )
    def get(self, request, main_folder, sort_a_z):
        """
        Get folder items
        """
        data = self.get_folder_with_items(main_folder, sort_a_z)
        serializer = FileSerializer(data, many=True)

        return Response(serializer.data)


class UploadFileAPIView(OperationView):
    allowed_methods = ["post"]
    parser_class = (FileUploadParser,)

    @extend_schema(
        responses={200: UploadFileSerializer},
        request=UploadFileSerializer(many=False),
    )
    def post(self, request):
        """
        Upload file
        """
        serializer = UploadFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        loc = serializer.validated_data.get("loc")
        self.upload_file(loc, file)
        return Response(serializer.data)


class ListBucketsAPIView(OperationView):
    allowed_methods = ["get"]

    @extend_schema(
        responses={200: BucketSerializer(many=True)},
    )
    def get(self, request):
        """
        List buckets
        """
        data = self.get_all_buckets()
        serializer = BucketSerializer(data, many=True)

        return Response(serializer.data)


class CreateFolderAPIView(OperationView):
    allowed_methods = ["post"]

    @extend_schema(
        responses={200: CreateFolderSerializer},
        request=CreateFolderSerializer(many=False),
    )
    def post(self, request):
        """
        Create folder
        """
        serializer = CreateFolderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loc = serializer.validated_data.get("loc")
        name = serializer.validated_data.get("name")
        self.create_folder_item(location=loc, folder_name=name)
        return Response(serializer.data)


class DownloadFileAPIView(OperationView):
    """
    Download file from S3 using file key
    """

    allowed_methods = ["get"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="file_key", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY
            )
        ],
    )
    def get(self, request):
        file_key = request.GET.get("file_key")
        result = self.download_file(file_key)
        response = HttpResponse(result["Body"].read())
        response["Content-Type"] = result["ContentType"]
        response["Content-Length"] = result["ContentLength"]
        response["Content-Disposition"] = "attachment; filename=" + file_key
        response["Accept-Ranges"] = "bytes"
        return response


class RenameFileAPIView(OperationView):
    """
    Rename file from S3 using file key
    """

    allowed_methods = ["post"]

    @extend_schema(request=FileRenameSerializer)
    def post(self, request):
        serializer = FileRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loc = serializer.validated_data.get("loc")
        file = serializer.validated_data.get("old_name")
        new_name = serializer.validated_data.get("new_name")
        file_name = self.rename(loc, file, new_name)
        return Response(status=status.HTTP_200_OK)


class PasteFileAPIView(OperationView):
    allowed_methods = ["post"]

    @extend_schema(request=PasteFileSerializer)
    def post(self, request):
        serializer = PasteFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loc = serializer.validated_data.get("loc")
        file_list = serializer.validated_data.get("file_list")
        self.paste(loc, file_list)
        return Response(status=status.HTTP_200_OK)


class MoveFileAPIView(OperationView):
    allowed_methods = ["put"]

    def put(self, request):
        serializer = PasteFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loc = serializer.validated_data.get("loc")
        file_list = serializer.validated_data.get("file_list")
        self.move(loc, file_list)
        return Response(status=status.HTTP_200_OK)


class DeleteFileAPIView(OperationView):
    allowed_methods = ["delete"]

    def delete(self, request):
        serializer = FileDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_list = serializer.validated_data.get("file_list")
        super().delete(file_list)
        return Response(status=status.HTTP_204_NO_CONTENT)
