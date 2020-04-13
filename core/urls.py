from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from . import api as core_api
from . import views

urlpatterns = [

    # View  
    path('chat/<str:room_name>/', views.room, name='room'),
    url('chat', views.index, name='index'),


    # API

    # Any where you see One prefixed indicates
    # PUT, DELETE, GET, PATCH methods

    # Others are either POST or GET

    path('auth', include('knox.urls')),
    path('auth/login', core_api.LoginAPI.as_view()),
    path('auth/register', core_api.RegisterAPI.as_view()),

    path('album', core_api.AlbumAPI.as_view()),
    path('album/<int:pk>', core_api.OneAlbumAPI.as_view()),
    path('image', core_api.ImageAPI.as_view()),
    path('image/<int:pk>', core_api.OneImageAPI.as_view()),

    path('album/change/default/<int:newAlbumPK>', core_api.ChangeDefaultAlbum),
    path('settings/image/maxseconds', core_api.ChanageImageTiming),
    path('settings/sleep', core_api.SleepClientAPI)
]
