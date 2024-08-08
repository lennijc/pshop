from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ThemeModelViewSet,SignUpAPIView,categoryModelViewSet,commentViewset,getUserInfo,getRelatedTheme
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'theme', ThemeModelViewSet)
router.register(r'category', categoryModelViewSet)
router.register(r'comment', commentViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),#login
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),#new refresh token
    path('signup/', SignUpAPIView.as_view(), name='signup'),#signup
    path('core/getme/', getUserInfo.as_view(), name='getme'),
    path('relatedTheme/<str:href>/', getRelatedTheme.as_view(), name='relatedtheme'),
]
