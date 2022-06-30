from rest_framework import serializers


class FileSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=255)
    url = serializers.FileField()
    icon = serializers.FileField()
    text = serializers.CharField(max_length=255)
    file_type = serializers.CharField(max_length=255)
