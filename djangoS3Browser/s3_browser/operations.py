from typing import Optional

import boto3
import sys

from urllib.parse import urljoin

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.conf import settings

"""
If variable defined, will be use custom endpoint, else will be used Amazon endpoints
"""
ENDPOINT_URL = getattr(settings, 'AWS_ENDPOINT_URL', None)

s3 = boto3.resource(
    's3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=ENDPOINT_URL
)
s3client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=ENDPOINT_URL
)

bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
bucket_location = s3client.get_bucket_location(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
"""
Big Note: for [1:]
-starts with the default "-" sign for the selected file location.
"""

"fetch the directories within the selected folder"


def strip_str(s: str) -> Optional[str]:
    return s.replace('\n', '').replace('\t', '').strip(' ') if s else s


def get_folder_with_items(main_folder, sort_a_z):
    try:
        main_folder = strip_str(main_folder)
        sort_a_z = True if sort_a_z == "true" else False  # sorted method a to z/ z to a
        result = s3client.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=main_folder[1:], Delimiter="/")
        result_files = get_files(main_folder, result.get('Contents'), sort_a_z) if result.get('Contents') else []
        result_folders = get_folders(main_folder, result.get('CommonPrefixes'), sort_a_z) if result.get(
            'CommonPrefixes') else []
        return result_folders + result_files  # return files and folders
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def get_files(main_folder, result, sort_a_z):
    try:
        files_list = []
        for obj in result:
            # main_folder[1:] exp; -folder1/folder2 => delete "-"
            if main_folder[1:] != obj.get('Key'):  # if obj is not folder item
                object_url = urljoin(
                    ENDPOINT_URL,
                    "{0}/{1}".format(settings.AWS_STORAGE_BUCKET_NAME, obj.get('Key'))
                )
                # for template file icon
                icon_list = [
                    'ai.png', 'audition.png', 'avi.png', 'bridge.png', 'css.png', 'csv.png', 'dbf.png', 'doc.png',
                    'dreamweaver.png', 'dwg.png', 'exe.png', 'file.png', 'fireworks.png', 'fla.png', 'flash.png',
                    'folder_icon.png', 'html.png', 'illustrator.png', 'indesign.png', 'iso.png', 'javascript.png',
                    'jpg.png', 'json-file.png', 'mp3.png', 'mp4.png', 'pdf.png', 'photoshop.png', 'png.png',
                    'ppt.png', 'prelude.png', 'premiere.png', 'psd.png', 'rtf.png', 'search.png', 'svg.png',
                    'txt.png', 'xls.png', 'xml.png', 'zip.png', 'zip-1.png']
                img_file_list = ['ani', 'bmp', 'cal', 'fax', 'gif', 'img', 'jbg', 'jpg', 'jpe', 'mac', 'pbm',
                                 'pcd', 'pcx', 'pct', 'pgm', 'png', 'jpeg', 'ppm', 'psd', 'ras', 'tag', 'tif',
                                 'wmf']
                extension, icon = str(obj['Key'].split('.')[-1]).lower(), None
                if extension in img_file_list:
                    icon = object_url if extension in ['bmp', 'jpg', 'jpeg', 'png',
                                                       'gif'] else "/static/images/jpg.png"
                if not icon:
                    icon = "/static/images/" + extension + ".png" if extension + ".png" in icon_list else "/static/images/file.png"
                item_type = "folder" if obj.get('Key')[-1] == "/" else "other"  # for show template
                files_list.append(
                    {'key': obj.get('Key'), 'url': object_url, 'icon': icon,
                     'text': obj.get('Key')[len(main_folder) - 1:], 'type': item_type})
        return sorted(files_list, key=lambda k: str(k['key']).lower(), reverse=not sort_a_z)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def get_folders(main_folder, result, sort_a_z):
    try:
        files_list = []
        for obj in result:
            icon = "/static/images/folder_icon.png"
            item_type = "folder"  # for show template
            url = obj.get('Prefix')
            files_list.append(
                {'key': obj.get('Prefix'), 'url': url, 'icon': icon,
                 'text': obj.get('Prefix')[len(main_folder) - 1:], 'type': item_type})
        return sorted(files_list, key=lambda k: str(k['key']).lower(), reverse=not sort_a_z)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def upload_file(location: str, file):
    try:
        location = strip_str(location)
        s3client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=location[1:] + file.name, Body=file)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Upload Failed! ', e)


def upload_file_content(file_name: str, content: str):
    try:
        file_name = strip_str(file_name)[1:]
        body = content.encode()
        s3client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name, Body=body)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Upload Failed! ', e)


def create_folder_item(location: str, folder_name: str):
    try:
        location = strip_str(location)
        folder_name = strip_str(folder_name)

        if folder_name[-1] != "/":
            folder_name += "/"
        s3client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=location[1:] + folder_name,
                            ACL="public-read")
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Create Folder Failed! ', e)


def download_file(file: str):
    try:
        file = strip_str(file)[1:]
        response = s3client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file)
        return response
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Download Failed! ', e)


def rename(location: str, file: str, new_name: str):
    try:
        location = strip_str(location)
        file = strip_str(file)
        new_name = strip_str(new_name)

        if file[-1] == "/" and new_name[-1] != "/":  # if file format exception
            new_name += "/"

        if file == new_name:
            """
            If rename canceled or name not changed
            """
            return location[1:] + file

        s3client.copy_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, ACL="public-read",
                             CopySource={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': location[1:] + file},
                             Key=new_name)
        s3client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=location[1:] + file)
        return location[1:] + new_name
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Rename Failed! ', e)


def paste(location, file_list):
    try:
        for file in file_list:
            file = strip_str(file)[1:]
            s3client.copy_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, ACL="public-read",
                                 CopySource={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file},
                                 Key=location[1:] + file.rsplit('/', 1)[-1])
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Paste Failed! ', e)


def move(location, file_list):
    try:
        for file in file_list:
            file = strip_str(file)[1:]

            s3client.copy_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, ACL="public-read",
                                 CopySource={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file},
                                 Key=location[1:] + file.rsplit('/', 1)[-1])
            s3client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Move Failed! ', e)


def delete(file_list):
    try:
        for file in file_list:
            file = strip_str(file)[1:]
            s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).objects.filter(Prefix=file).delete()
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise Exception('Delete Failed! ', e)
