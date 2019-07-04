import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .operations import *

"fetch the directories within the selected folder"


def get_folder_items(request, main_folder, sort_a_z):
    json_string = get_folder_with_items(main_folder, sort_a_z)
    return HttpResponse(json.dumps(json_string), content_type="application/json")


@csrf_exempt
def upload(request):
    file = request.FILES.get('file')
    upload_file(request.POST['loc'], file)
    return HttpResponse(json.dumps(file.name), content_type="application/json", status=200)


@csrf_exempt
def create_folder(request):
    create_folder_item(request.POST['loc'], request.POST['folder_name'])
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def download(request):
    file = request.GET.get('file')
    result = download_file(file)
    response = HttpResponse(result['Body'].read())
    response['Content-Type'] = result['ContentType']
    response['Content-Length'] = result['ContentLength']
    response['Content-Disposition'] = 'attachment; filename=' + file
    response['Accept-Ranges'] = 'bytes'
    return response


@csrf_exempt
def rename_file(request):
    file_name = rename(request.POST['loc'], request.POST['file'], request.POST['new_name'])
    return HttpResponse(json.dumps(file_name), content_type="application/json", status=200)


@csrf_exempt
def paste_file(request):
    paste(request.POST['loc'], request.POST.getlist('file_list[]'))
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def move_file(request):
    move(request.POST['loc'], request.POST.getlist('file_list[]'))
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def delete_file(request):
    delete(request.POST.getlist('file_list[]'))
    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def get_item(request):
    file = request.GET.get('file')
    result = download_file(file)
    response = HttpResponse(result['Body'].read())

    return response


@csrf_exempt
def get_item_content(request):
    file = request.GET.get('file')
    result = download_file(file)
    status = 200
    try:
        content = result['Body'].read().decode('utf-8')
    except Exception as e:
        content = "Not text"
        status = 405

    return HttpResponse(json.dumps({
        "content": content
    }), content_type="application/json", status=status)


@csrf_exempt
def update_item_content(request):
    file: str = request.POST.get('file')
    content: str = request.POST.get('content')

    location = get_location(file)
    _file = get_file_name(file)
    tmp_name = _file + '.tmp'

    """
    Save file in case if uploading new content failed
    """
    rename(location, _file, tmp_name)

    try:
        upload_file_content(
            file, content
        )
    except Exception as e:
        # reverse file from tmp
        rename(location, tmp_name, _file)
        return HttpResponse(json.dumps("ERROR"), content_type="application/json", status=500)
    else:
        delete([tmp_name])

    return HttpResponse(json.dumps("OK"), content_type="application/json", status=200)


@csrf_exempt
def admin_index(request):
    return render(request, 'admin_index.html', {})
