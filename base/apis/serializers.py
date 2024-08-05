from rest_framework import serializers
from ..models import theme,category
from django.contrib.auth import get_user_model

User=get_user_model()


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"
    
    
class ThemeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = theme
        fields = '__all__'
        
class categoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=category
        fields= '__all__'
        
class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'name', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)  # Remove confirm_password from validated_data
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Use set_password to hash the password
        user.save()
        return user
    
