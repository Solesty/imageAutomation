
import secrets
import logging
import random
from datetime import timedelta
from django.utils import timezone
from http import HTTPStatus

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from knox.models import AuthToken
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .utils import getOrCreateSettingsObject
from .serializers import (AlbumSerializer, ImageSerializer, SettingsSerializer,
                          LoginSerializer, RegisterSerializer, UserSerializer)
from . import models as core_models

from .consumers import ChatConsumer


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


async def updateDefaultAlbum(albumPK):
    channel_layer = get_channel_layer()
    group_name = "album_view"
    content = {
        # This "type" passes through to the front-end to facilitate
        # our Redux events.
        "type": "UPDATE_DEFAULT_ALBUM",
        "payload": {"album_id": albumPK},
    }

    await channel_layer.group_send(group_name, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": "notify",
        "content": content,
    })


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def ChangeDefaultAlbum(request, newAlbumPK):

    try:
        albumObject = core_models.Album.objects.get(
            pk=newAlbumPK
        )
    except core_models.Album.DoesNotExist:
        return Response(data=["Album not found"], status=status.HTTP_404_NOT_FOUND)

    # Change all album from being default
    core_models.Album.objects.all().update(is_default=False)
    albumObject.is_default = True
    albumObject.save()
    albumData = AlbumSerializer(albumObject).data

    # TODO: since the default image as being changed,
    # fire a signal to refresh the UI and pick up the new
    # settings.
    # Tip: You can keep another table called Notifications
    # or Changes that gets a value incremented and updated.
    # The UI will be constantly looking at this table to
    # know if there is any new changes. Once it finds that
    # the value has been chanaged from what it has, it refreshes
    # the UI automatically

    async_to_sync(updateDefaultAlbum)(newAlbumPK)

    return Response(data=albumData)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
def SleepClientAPI(request):

    raise ValueError("Not Yet Implemeted")

    # return Response()


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
def ChanageImageTiming(request):

    newSeconds = request.data.get("seconds", None)
    if newSeconds == None:
        return Response(data=["seconds is required"], status=status.HTTP_400_BAD_REQUEST)

    settingsObject = getOrCreateSettingsObject()
    settingsObject.max_show_seconds = newSeconds
    settingsObject.save()

    # TODO: Perform UI update logic

    settingsData = SettingsSerializer(settingsObject, many=False).data

    return Response(data=settingsData)


class ImageAPI(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        imageObjects = core_models.Image.objects.all().order_by('-dateCreated')
        imageData = ImageSerializer(imageObjects, many=True).data
        return Response(data=imageData)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        return core_models.Album.objects.all()


class OneAlbumAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer
    queryset = core_models.Album
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    # def get(self, request, *args, **kwargs):
    #     return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):

        # TODO Delete all the images of this album from the filesystem
        return self.destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        albumPK = kwargs['pk']

        try:
            albumObject = core_models.Album.objects.get(pk=albumPK)
        except core_models.Album.DoesNotExist:
            return Response(data="Album does not exist", status=status.HTTP_404_NOT_FOUND)

        albumData = AlbumSerializer(albumObject, many=False).data

        return Response(data=albumData)


class OneImageAPI(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer
    queryset = core_models.Image
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        imageObject = core_models.Image.objects.get(pk=kwargs['pk'])
        imageObject.imageFile.delete()
        return self.destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        imagePK = kwargs['pk']

        try:
            imageObject = core_models.Image.objects.get(pk=imagePK)
        except core_models.Image.DoesNotExist:
            return Response(data="Image does not exist", status=status.HTTP_404_NOT_FOUND)

        imageData = ImageSerializer(imageObject, many=False).data

        return Response(data=imageData)


class AlbumAPI(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response(status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        albumsObjects = core_models.Album.objects.all()
        albumsData = AlbumSerializer(albumsObjects, many=True).data
        return Response(data=albumsData)


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        unused_instance, token = AuthToken.objects.create(user)
        return Response({
            # serialized user
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            # You can set time here check package
            "token": token})


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        unused_instance, token = AuthToken.objects.create(user)
        return Response({
            # serialized user
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            # You can set time here check package
            "token": token})
