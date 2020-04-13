
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate

from . import models as core_models


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.Settings
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.Image
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.Album
        fields = '__all__'

    def isFirstAlbum(self, album):
        if album is None:
            return True

        return core_models.Album.objects.filter(
            ~Q(id=album.pk)
        ).count() == 0

    def create(self, validated_data):

        title = validated_data['title']
        description = validated_data.get('description', '')

        if core_models.Album.objects.filter(
            title__iexact=title
        ).count() > 0:
            raise serializers.ValidationError(
                ["An album with such title exist"])
        albumObject = core_models.Album(
            title=title,
            description=description
        )
        albumObject.save()

        isFirstAlbum = self.isFirstAlbum(albumObject)
        if isFirstAlbum:
            albumObject.is_default = True
            albumObject.save()

        return albumObject

    def to_representation(self, instance):
        albumImages = core_models.Image.objects.filter(
            album=instance
        )
        imageData = ImageSerializer(albumImages, many=True).data
        return {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "is_default": instance.is_default,
            "images": imageData,
        }


class LoginSerializer(serializers.Serializer):
    # We are not creating a model hence reason why
    # we did not use the ModelSerializer
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user and user.is_active:
            return user
        else:
            raise serializers.ValidationError("Incorrect Credentials")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            validated_data['email'],
            validated_data['password'],
        )

        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'email')

    def to_representation(self, instance):

        return {
            'id': instance.id,
            'email': instance.email
        }
