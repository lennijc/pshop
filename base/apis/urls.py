from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (
    ThemeModelViewSet,SignUpAPIView,categoryModelViewSet,commentViewset,
    getUserInfo,getRelatedTheme,getPopularThemes,getLastThemes,getRelatedSubMenus,searchApi,
    articleViewset,ContactUsView,reservation_viewset,normQuestionViewset,UserViewset,UpdateDiscountAPIView,answerContact,offViewset,
    subCategoryModelViewSet,contactViewSet    )
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'theme', ThemeModelViewSet)
router.register(r'category', categoryModelViewSet,basename="category")
router.register(r'sub_category', subCategoryModelViewSet,basename="sub_category")
router.register(r'comment', commentViewset)
router.register(r'article', articleViewset) 
router.register(r'reservation', reservation_viewset,basename="reservations") 
router.register(r'question', normQuestionViewset,basename="questions") 
router.register(r'user', UserViewset,basename="users") 
router.register(r'off', offViewset,basename="offs") 
router.register(r'Contact', contactViewSet,basename="contact") 

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),#login
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),#new refresh token
    path('signup/', SignUpAPIView.as_view(), name='signup'),#signup
    path('core/getme/', getUserInfo.as_view(), name='getme'),
    path('relatedTheme/<str:href>/', getRelatedTheme.as_view(), name='relatedtheme'),
    path('topThemes/', getPopularThemes.as_view(), name='popularThemes'),
    path('lastThemes/', getLastThemes.as_view(), name='lastThemes'),
    path('similarSubmenus/<str:href>/', getRelatedSubMenus.as_view(), name='relatedSubmenus'),
    path('search/<str:query>/', searchApi.as_view(), name='searchQuery'),
    path('contact/', ContactUsView.as_view(), name='contactUs'),
    path('discount/', UpdateDiscountAPIView.as_view(), name='updateDiscount'),
    path('contact/answer/', answerContact.as_view(), name='answerContact'),
]
