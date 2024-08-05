from rest_framework import viewsets
from ..models import theme,category
from .serializers import ThemeModelSerializer,categoryModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignUpSerializer,userSerializer


class ThemeModelViewSet(viewsets.ModelViewSet):
    queryset = theme.objects.all()
    serializer_class = ThemeModelSerializer
    
class categoryModelViewSet(viewsets.ModelViewSet):
    queryset=category.objects.all()
    serializer_class=categoryModelSerializer
    
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
        

