from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(min_length=6)
    givenName = serializers.CharField(min_length=1)
    phone = serializers.CharField(min_length=7)
    name = serializers.CharField(required=False, allow_blank=True)


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    code = serializers.CharField(min_length=1)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6)


class RefreshTokenSerializer(serializers.Serializer):
    refreshToken = serializers.CharField()
    email = serializers.EmailField()


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
