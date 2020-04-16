
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
from .consumerActions import updateDefaultAlbum, updateGalleryTimer

from asgiref.sync import async_to_sync


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

    # Notify connected clients
    async_to_sync(updateDefaultAlbum)(newAlbumPK)

    return Response(data=albumData)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
def IncreaseSpeedAPI(request):

    settingsObject = getOrCreateSettingsObject()

    if(settingsObject.max_show_seconds >= 15):
        return Response(data={"error": "Slide speed can not be increased further."}, status=HTTPStatus.BAD_REQUEST)

    settingsObject.max_show_seconds = settingsObject.max_show_seconds + 1
    settingsObject.save()

    async_to_sync(updateGalleryTimer)(settingsObject.max_show_seconds)

    settingsData = SettingsSerializer(settingsObject, many=False).data

    return Response(data=settingsData)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
def DecreaseSpeedAPI(request):

    settingsObject = getOrCreateSettingsObject()
    if(settingsObject.max_show_seconds - 1 <= 0):
        return Response(data="Slide speed can not be decreased", status=HTTPStatus.BAD_REQUEST)

    settingsObject.max_show_seconds = settingsObject.max_show_seconds - 1
    settingsObject.save()

    async_to_sync(updateGalleryTimer)(settingsObject.max_show_seconds)

    settingsData = SettingsSerializer(settingsObject, many=False).data

    return Response(data=settingsData)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
def SleepClientAPI(request):

    raise ValueError("Not Yet Implemeted")

    # return Response()


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated, ))
def ChanageImageTiming(request):

    newSeconds = request.data.get("seconds", None)
    if newSeconds == None or newSeconds < 1 or newSeconds > 15:
        return Response(data=["Slide speed (seconds) is required and must not be more than 15 and less than 1"], status=status.HTTP_400_BAD_REQUEST)

    settingsObject = getOrCreateSettingsObject()
    settingsObject.max_show_seconds = newSeconds
    settingsObject.save()

    async_to_sync(updateGalleryTimer)(newSeconds)

    settingsData = SettingsSerializer(settingsObject, many=False).data

    return Response(data=settingsData)


@api_view(['GET'])
def GetDefaultAlbum(request):
    albumsObjects = core_models.Album.objects.get(is_default=True)
    albumsData = AlbumSerializer(albumsObjects).data

    settingsObject = getOrCreateSettingsObject()
    albumsData['viewTimeout'] = settingsObject.max_show_seconds * 1000

    return Response(data=albumsData)


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

        album = core_models.Album.objects.get(pk=request.data.get('album'))
        insertResponse = self.create(request, *args, **kwargs)

        if(album.is_default):
            # Notify connected clients
            async_to_sync(updateDefaultAlbum)(request.data.get('album'))

        return insertResponse

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
        albumPK = kwargs['pk']
        album = core_models.Album.objects.get(pk=albumPK)

        title = request.data.get('title')
        description = request.data.get('description')
        is_default = request.data.get('is_default', album.is_default)

        album.title = title
        album.description = description
        album.is_default = is_default
        album.save()

        if(album.is_default):
            # Notify connected clients
            async_to_sync(updateDefaultAlbum)(albumPK)

        return Response()

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

        try:
            imageObject = core_models.Image.objects.get(pk=kwargs['pk'])
            imageObject.imageFile.delete()
            album = core_models.Album.objects.get(pk=imageObject.album.pk)

            if(album.is_default):
                # Notify connected clients
                async_to_sync(updateDefaultAlbum)(album.pk)
        except (core_models.Album.DoesNotExist, core_models.Image.DoesNotExist):
            pass

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
