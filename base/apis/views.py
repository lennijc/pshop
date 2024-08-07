from rest_framework import viewsets
from ..models import theme,category
from .serializers import ThemeModelSerializer,categoryModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignUpSerializer,userSerializer,allcategorySerializer
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action


class ThemeModelViewSet(viewsets.ModelViewSet):
    queryset = theme.objects.all()
    serializer_class = ThemeModelSerializer
    @action(detail=False, methods=['get'], url_path='(?P<href>[^/.]+)')
    def themes_by_category(self, request, href=None):
        print("href is : " , href)
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
        
    
