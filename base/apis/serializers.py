from rest_framework import serializers
from ..models import theme,category
from django.contrib.auth import get_user_model
from rest_framework.serializers import PrimaryKeyRelatedField

User=get_user_model()


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"
    
    

        
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
    
class allcategorySerializer(serializers.ModelSerializer):
    sub_menu=categoryModelSerializer(source="category_set",many=True,read_only=True)
    class Meta:
        model=category
        fields="__all__"
        
class CategoryIDField(PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        # During deserialization, convert the ID to the actual category instance
        return self.queryset.get(id=data)

    def to_representation(self, value):
        # During serialization, return just the ID
        print(value.title)
        return value
    
class ThemeModelSerializer(serializers.ModelSerializer):
    category_detail=allcategorySerializer(source="category",read_only=True)
    class Meta:
        model = theme
        fields = '__all__'


