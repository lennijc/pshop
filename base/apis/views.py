from rest_framework import viewsets
from ..models import theme,category,comment
from django.contrib.auth import get_user_model
from .serializers import ThemeModelSerializer,categoryModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignUpSerializer,userSerializer,allcategorySerializer,commentSerializer,allCommentSerializer
from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.decorators import action
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser,IsAuthenticated,IsAuthenticatedOrReadOnly,SAFE_METHODS



User = get_user_model()
class ThemeModelViewSet(viewsets.ModelViewSet):
    queryset = theme.objects.all()
    serializer_class = ThemeModelSerializer
    @action(detail=False, methods=['get'], url_path='(?P<href>[^/.]+)')
    def themes_by_category(self, request, href=None):
        #get the href of the category and return the corresponding themes.
        try:
            # category_instance=category.objects.get(href=href)
            # themes = theme.objects.filter(category=category_instance.id)
            themes=theme.objects.filter(category__href=href)
            theme_serializer=ThemeModelSerializer(themes,many=True)
            return Response(theme_serializer.data,status=status.HTTP_200_OK)
        except:
            return Response({"error":"something went wronge"},status=status.HTTP_400_BAD_REQUEST)
                
            
        
class categoryModelViewSet(viewsets.ModelViewSet):
    queryset=category.objects.all()
    serializer_class=allcategorySerializer
    
class SignUpAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(username=request.data.get("phone"))
        refresh = RefreshToken.for_user(user)
        return Response({
            'user_info': SignUpSerializer(user).data,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        })


class commentViewset(viewsets.ModelViewSet):
    queryset=comment.objects.all()
    permission_classes=[IsAuthenticatedOrReadOnly]
    def get_serializer_class(self):
        """Determine the serializer class based on the action."""
        if self.request.method in SAFE_METHODS:
            return allCommentSerializer
        else:
            return commentSerializer
        
    def create(self, request, *args, **kwargs):
        theme_href=request.data.pop("themeHref")
        theme_instance=get_object_or_404(theme,href=theme_href)
        request.data["theme"]=theme_instance.id
        return super().create(request,*args,**kwargs)
    
    @action(detail=True, methods=["post"],permission_classes=[IsAuthenticated])
    def answerComment(self, request, *args, **kwargs):
        mainCommentID = self.kwargs["pk"]
        mainCommentInstance = get_object_or_404(comment, pk=mainCommentID)
        mainCommentInstance.answer=1
        mainCommentInstance.save()
        # also we could add the new comment data to the request.data and pass the data to the self.create(request)
        #the answer has to inherit the course or article from the mainCommentInstance as this is an answer to that mainComment
        # try:
        answer_comment_data = {
                "mainCommentID": mainCommentID,
                "creator": request.user.id, 
                "body":request.data["body"],
                "theme":mainCommentInstance.theme_id,
                "answer": 1,
                "isAnswer": True,
                "score": 5,
            }
        serializer = self.get_serializer(data=answer_comment_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # except Exception as e:
        #     return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        
class getUserInfo(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=userSerializer
    def get_object(self):
        obj = get_object_or_404(User,id=self.request.user.id)
        return obj
        
class getRelatedTheme(ListAPIView):
    serializer_class=ThemeModelSerializer
    def get_queryset(self):
        theme_instance=get_object_or_404(theme,href=self.kwargs["href"])
        return theme.objects.filter(category=theme_instance.category)
        
        
    
