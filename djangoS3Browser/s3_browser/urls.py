"""s3_browser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, re_path
from djangoS3Browser.s3_browser import settings
from djangoS3Browser.s3_browser import views

urlpatterns = [
    re_path(
        r"folder-items/(?P<main_folder>.+)/(?P<sort_a_z>.+)/",
        views.GetFolderItemsAPIView.as_view(),
        name="folder-items",
    ),
    
    path('upload/', views.UploadFileAPIView.as_view(), name='upload'),
    path('buckets/', views.ListBucketsAPIView.as_view(), name='buckets-list'),
    path('folder/', views.CreateFolderAPIView.as_view(), name='folder-create'),

    path("download/", views.DownloadFileAPIView.as_view(), name='download'),

    path("rename/", views.RenameFileAPIView.as_view(), name='rename_file'),
    path("paste/", views.PasteFileAPIView.as_view(), name='paste_file'),
    path('move/', views.MoveFileAPIView.as_view(), name='move_file'),
    path('delete/', views.DeleteFileAPIView.as_view(), name='delete_file'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
