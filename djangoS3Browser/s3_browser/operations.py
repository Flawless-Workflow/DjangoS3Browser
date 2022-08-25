from typing import Optional, List, Dict

import boto3
import sys
import logging
from urllib.parse import urljoin

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .exceptions import FileException

logger = logging.getLogger(__name__)

"""
If variable defined, will be use custom endpoint, else will be used Amazon endpoints
"""
ENDPOINT_URL = getattr(settings, "AWS_ENDPOINT_URL", None)

s3 = boto3.resource(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=ENDPOINT_URL,
)
s3client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=ENDPOINT_URL,
)


class OperationsMixin:
    """
    Big Note: for [1:]
    -starts with the default "-" sign for the selected file location.
    """

    def __init__(
        self,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
        location_constraint=settings.AWS_REGION,
    ) -> None:
        self.bucket_name = bucket_name
        self.location_constraint = location_constraint

    @staticmethod
    def strip_str(s: str) -> Optional[str]:
        return s.replace("\n", "").replace("\t", "").strip(" ") if s else s

    @staticmethod
    def remove_start(s: str) -> str:
        """
        Clear string from start '-' symbol
        :param s:
        :return:
        """
        return s[1:] if s.startswith("-") else s

    @staticmethod
    def get_path(base, file):
        return urljoin(base, file)

    @staticmethod
    def get_location(s: str) -> str:
        """
        Get file directory path or return path
        :param s: str - path
        :return:
        """
        loc = s
        if "/" in s:
            loc = s.rsplit("/", 1)[0] if not s.endswith("/") else s

            if not loc.endswith("/"):
                loc += "/"
        else:
            loc = "-"

        return loc

    @staticmethod
    def get_file_name(self, s: str) -> Optional[str]:
        """
        Get file name from path
        :param s:
        :return:
        """
        if s.endswith("/"):
            raise ValueError("s is not file path")

        if "/" in s:
            return s.rsplit("/", 1)[1]
        else:
            return self.remove_start(s)

    def get_all_buckets(self) -> list:
        """
        Get all buckets from s3
        :return:
        """
        try:
            # all_buckets_s3 = s3.resource("s3")
            buckets = []
            for bucket in s3.buckets.all():
                buckets.append({"name": bucket.name})
            return buckets
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def create_bucket(self) -> str:
        try:
            response = s3.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": self.location_constraint
                },
            )
            return getattr(response, "name")
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=_("Unable to create bucket"))

    def get_folder_with_items(self, main_folder: str, sort_a_z: bool = False) -> List:
        """
        Get Folders + Files in current folder
        :param main_folder:
        :param sort_a_z:
        :return:
        """
        try:
            main_folder = self.strip_str(main_folder)
            sort_a_z = (
                True if sort_a_z == "true" else False
            )  # sorted method a to z/ z to a
            result = s3client.list_objects(
                Bucket=self.bucket_name,
                Prefix=main_folder[1:],
                Delimiter="/",
            )
            result_files = (
                self.get_files(main_folder, result.get("Contents"), sort_a_z)
                if result.get("Contents")
                else []
            )
            result_folders = (
                self.get_folders(main_folder, result.get("CommonPrefixes"), sort_a_z)
                if result.get("CommonPrefixes")
                else []
            )
            return result_folders + result_files  # return files and folders
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def get_files(
        self, main_folder: str, result: List, sort_a_z: bool = False
    ) -> List[Dict[str, str]]:
        """
        Get Files in current folder
        :param main_folder: str
        :param result: files list in S3 format ['CommonPrefixes']
        :param sort_a_z: bool sort files by name
        :return: List
        """
        try:
            files_list = []
            for obj in result:
                # main_folder[1:] exp; -folder1/folder2 => delete "-"
                if self.remove_start(main_folder) != obj.get(
                    "Key"
                ):  # if obj is not folder item
                    object_url = urljoin(
                        ENDPOINT_URL,
                        "{0}/{1}".format(self.bucket_name, obj.get("Key")),
                    )
                    # for template file icon
                    icon_list = [
                        "ai.png",
                        "audition.png",
                        "avi.png",
                        "bridge.png",
                        "css.png",
                        "csv.png",
                        "dbf.png",
                        "doc.png",
                        "dreamweaver.png",
                        "dwg.png",
                        "exe.png",
                        "file.png",
                        "fireworks.png",
                        "fla.png",
                        "flash.png",
                        "folder_icon.png",
                        "html.png",
                        "illustrator.png",
                        "indesign.png",
                        "iso.png",
                        "javascript.png",
                        "jpg.png",
                        "json-file.png",
                        "mp3.png",
                        "mp4.png",
                        "pdf.png",
                        "photoshop.png",
                        "png.png",
                        "ppt.png",
                        "prelude.png",
                        "premiere.png",
                        "psd.png",
                        "rtf.png",
                        "search.png",
                        "svg.png",
                        "txt.png",
                        "xls.png",
                        "xml.png",
                        "zip.png",
                        "zip-1.png",
                    ]
                    img_file_list = [
                        "ani",
                        "bmp",
                        "cal",
                        "fax",
                        "gif",
                        "img",
                        "jbg",
                        "jpg",
                        "jpe",
                        "mac",
                        "pbm",
                        "pcd",
                        "pcx",
                        "pct",
                        "pgm",
                        "png",
                        "jpeg",
                        "ppm",
                        "psd",
                        "ras",
                        "tag",
                        "tif",
                        "wmf",
                    ]
                    extension, icon = str(obj["Key"].split(".")[-1]).lower(), None
                    if extension in img_file_list:
                        icon = (
                            object_url
                            if extension in ["bmp", "jpg", "jpeg", "png", "gif"]
                            else "/static/images/jpg.png"
                        )
                    if not icon:
                        icon = (
                            "/static/images/" + extension + ".png"
                            if extension + ".png" in icon_list
                            else "/static/images/file.png"
                        )
                    item_type = (
                        "folder" if obj.get("Key")[-1] == "/" else "other"
                    )  # for show template
                    files_list.append(
                        {
                            "key": obj.get("Key"),
                            "url": object_url,
                            "icon": icon,
                            "text": obj.get("Key")[len(main_folder) - 1 :],
                            "type": item_type,
                        }
                    )
            return sorted(
                files_list, key=lambda k: str(k["key"]).lower(), reverse=not sort_a_z
            )
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def get_folders(
        self, main_folder: str, result: List, sort_a_z: bool = False
    ) -> List[Dict[str, str]]:
        """
        Get Folders list
        :param main_folder: str
        :param result: folders list in S3 format
        :param sort_a_z: bool - sort by name
        :return:
        """
        try:
            files_list = []
            for obj in result:
                icon = "/static/images/folder_icon.png"
                item_type = "folder"  # for show template
                url = obj.get("Prefix")
                files_list.append(
                    {
                        "key": obj.get("Prefix"),
                        "url": url,
                        "icon": icon,
                        "text": obj.get("Prefix")[len(main_folder) - 1 :],
                        "type": item_type,
                    }
                )
            return sorted(
                files_list, key=lambda k: str(k["key"]).lower(), reverse=not sort_a_z
            )
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def upload_file(self, location: str, files) -> None:
        """
        Upload <file> to s3 storage
        :param location: str
        :param file:
        :return:
        """
        try:
            location = self.strip_str(location)
            for file in files:
                s3client.put_object(
                    Bucket=self.bucket_name,
                    Key=urljoin(self.remove_start(location), file.name),
                    Body=file,
                )
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def upload_file_content(self, file_name: str, content: str) -> None:
        """
        Upload content to s3 storage
        :param file_name: str
        :param content: str
        :return:
        """
        try:
            file_name = self.remove_start(self.strip_str(file_name))
            body = content.encode()
            s3client.put_object(Bucket=self.bucket_name, Key=file_name, Body=body)
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def create_folder_item(self, location: str, folder_name: str) -> None:
        """
        Create folder in s3 storage
        :param location:
        :param folder_name:
        :return:
        """
        try:
            location = self.strip_str(location)
            folder_name = self.strip_str(folder_name)

            if folder_name[-1] != "/":
                folder_name += "/"
            s3client.put_object(
                Bucket=self.bucket_name,
                Key=urljoin(self.remove_start(location), folder_name),
                ACL="public-read",
            )
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def download_file(self, file: str):
        """
        Download file from s3 storage
        :param file: str - path in s3 storage
        :return: S3 Object
        """
        try:
            file = self.remove_start(self.strip_str(file))
            response = s3client.get_object(Bucket=self.bucket_name, Key=file)
            return response
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def rename(self, location: str, file: str, new_name: str) -> str:
        """
        Change file name via copy old file to file with new_name and delete(old_file)
        :param location:
        :param file:
        :param new_name:
        :return: str - new file path in s3 storage
        """
        try:
            location = self.remove_start(self.strip_str(location))
            file = self.remove_start(self.strip_str(file))
            new_name = self.remove_start(self.strip_str(new_name))

            if file[-1] == "/" and new_name[-1] != "/":  # if file format exception
                new_name += "/"

            if file == new_name:
                """
                If rename canceled or name not changed
                """
                return urljoin(location, file)

            s3client.copy_object(
                Bucket=self.bucket_name,
                ACL="public-read",
                CopySource={
                    "Bucket": self.bucket_name,
                    "Key": urljoin(location, file),
                },
                Key=urljoin(location, new_name),
            )
            s3client.delete_object(
                Bucket=self.bucket_name,
                Key=urljoin(location, file),
            )
            return urljoin(location, new_name)
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def paste(self, location: str, file_list: List[str]):
        """
        Copy file_list to folder
        :param location: str
        :param file_list: List[str]
        :return:
        """
        try:
            for file in file_list:
                file = self.remove_start(self.strip_str(file))
                s3client.copy_object(
                    Bucket=self.bucket_name,
                    ACL="public-read",
                    CopySource={"Bucket": self.bucket_name, "Key": file},
                    Key=urljoin(self.remove_start(location), file.rsplit("/", 1)[-1]),
                )
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def move(self, location: str, file_list: List[str]):
        """
        Copy selected files to folder and delete old_files
        :param location:
        :param file_list:
        :return:
        """
        try:
            for file in file_list:
                file = self.remove_start(self.strip_str(file))

                if file.endswith("/"):
                    to_file = urljoin(
                        self.remove_start(location), file.rsplit("/", 2)[-2] + "/"
                    )
                else:
                    to_file = urljoin(
                        self.remove_start(location), file.rsplit("/", 1)[-1]
                    )

                if file == to_file:
                    """
                    Move self in self
                    """
                    continue

                s3client.copy_object(
                    Bucket=self.bucket_name,
                    ACL="public-read",
                    CopySource={"Bucket": self.bucket_name, "Key": file},
                    Key=to_file,
                )
                s3client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file,
                )
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)

    def delete(self, file_list: List[str]) -> None:
        """
        Delete files from s3 storage
        :param file_list:
        :return:
        """
        try:
            for file in file_list:
                file = self.remove_start(self.strip_str(file))
                s3.Bucket(self.bucket_name).objects.filter(Prefix=file).delete()
        except Exception as err:
            logger.debug(
                "Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            raise FileException(detail=err)
