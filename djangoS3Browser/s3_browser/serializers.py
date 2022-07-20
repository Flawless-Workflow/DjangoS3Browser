from rest_framework import serializers


class FileSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=255)
    url = serializers.URLField()
    text = serializers.CharField(max_length=255)
    file_type = serializers.CharField(max_length=255, source="type")

class UploadFileSerializer(serializers.Serializer):
    files = serializers.FileField()
    loc = serializers.CharField()

class BucketSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

class CreateFolderSerializer(serializers.Serializer):
    loc = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)

class FileRenameSerializer(serializers.Serializer):
    loc = serializers.CharField()
    old_name = serializers.CharField(max_length=255)
    new_name = serializers.CharField(max_length=255)


class FileDeleteSerializer(serializers.Serializer):
    file_list = serializers.ListField(child=serializers.CharField())

class PasteFileSerializer(serializers.Serializer):
    loc = serializers.CharField(max_length=255)
    file_list = serializers.ListField(child=serializers.CharField())