from rest_framework import serializers
from ..models import theme,category,comment,Article,contact,reservation,Question,Off
from django.contrib.auth import get_user_model
from rest_framework.serializers import PrimaryKeyRelatedField
from django.db.models import Avg
from django.contrib.auth.password_validation import validate_password

User=get_user_model()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)   
    def validate_new_password(self,value):
        validate_password(value)
        return value
    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("new password and its confirmation didn't match")
        return data
    
class changeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["email","phone","first_name","last_name","name"]
        
    

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        exclude=["password"]
    
class categoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=category
        fields= '__all__'
        
class contactserializer(serializers.ModelSerializer):
    class Meta:
        model=contact
        fields="__all__"
        
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
class ThemeModelSerializer(serializers.ModelSerializer):
    category_detail=allcategorySerializer(source="category",read_only=True)
    average_score=serializers.SerializerMethodField()
    class Meta:
        model = theme
        fields = '__all__'
    def get_average_score(self,obj):
        return obj.comments.aggregate(Avg('score'))['score__avg']

class allArticleSerializer(serializers.ModelSerializer):
    category_detail=allcategorySerializer(source="category",read_only=True)
    # average_score=serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = '__all__'
    # def get_average_score(self,obj):
    #     return obj.comments.aggregate(Avg('score'))['score__avg']

class base_comment_serializer(serializers.ModelSerializer):
    class Meta:
        model = comment
        fields = "__all__"

class commentSerializer(serializers.ModelSerializer):
    creator=userSerializer(read_only=True)
    class Meta:
        model=comment
        fields="__all__"
        
class allCommentSerializer(serializers.ModelSerializer):
    creator=userSerializer(read_only=True)
    theme=serializers.SlugRelatedField(slug_field="name",read_only=True)
    #answer content is the reverse of maincommentID because mainCommentID is refering to the question or mainComment
    #but answer content is refering to the answer or the reply comment to the mainComment
    answerContent=commentSerializer(source="replies",many=True,read_only=True)
    class Meta:
        model=comment
        fields="__all__"
        
class reservationSerializer(serializers.ModelSerializer):
    class Meta:
        model=reservation
        fields="__all__"
        
class normQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields="__all__"

class offSerializer(serializers.ModelSerializer):
    class Meta:
        model=Off
        fields="__all__"
        

        




