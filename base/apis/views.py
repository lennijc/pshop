from rest_framework import viewsets
from ..models import theme,category,comment,Article,Question,contact,Off
from django.contrib.auth import get_user_model
from .serializers import ThemeModelSerializer,categoryModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (SignUpSerializer,userSerializer,allcategorySerializer,
                          commentSerializer,allCommentSerializer,allArticleSerializer,
                          contactserializer,reservationSerializer,reservation as Reservation,normQuestionSerializer,
                          ChangePasswordSerializer,changeProfileSerializer,offSerializer,base_comment_serializer,noStatusReservationSerializer,readReservationSerializer)
from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.decorators import action
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser,IsAuthenticated,IsAuthenticatedOrReadOnly,SAFE_METHODS,AllowAny
from .permissions import isAdminOrReadonly
from django.db.models import Avg
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from PIL import Image
import io
import tempfile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from PIL import Image
from ..tasks import send_email_task

User = get_user_model()
class ThemeModelViewSet(viewsets.ModelViewSet):
    queryset = theme.objects.all().prefetch_related("comments")
    serializer_class = ThemeModelSerializer
    permission_classes=[isAdminOrReadonly]
    parser_classes=[MultiPartParser,FormParser]
    @action(detail=False, methods=['get'], url_path='category/(?P<href>[^/.]+)',permission_classes=[AllowAny])
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
        
    @action(detail=True,methods=["get"],permission_classes=[AllowAny])
    def themeInfo(self,request,*args,**kwargs):
        theme_instance=get_object_or_404(theme,href=kwargs["pk"])         
        serializer = self.get_serializer(theme_instance)
        return Response(serializer.data,status=status.HTTP_200_OK)   
        
class categoryModelViewSet(viewsets.ModelViewSet):
    serializer_class=allcategorySerializer
    permission_classes=[isAdminOrReadonly]
    def get_queryset(self):
        return category.objects.filter(main_category=None)
    
    @action(detail=False,methods=["get"],permission_classes=[AllowAny])
    def getAllCategory(self,request,*args,**kwargs):
        categories = category.objects.all()         
        serializer = allcategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

#only for submenues    
class subCategoryModelViewSet(viewsets.ModelViewSet):
    serializer_class=allcategorySerializer
    permission_classes=[isAdminOrReadonly]
    parser_classes=[MultiPartParser,FormParser]
    def get_queryset(self):
        return category.objects.exclude(main_category=None)
    
    def create(self, request, *args, **kwargs):
        print("request.data is: " , request.data)
        if request.data.get("main_category") is None:
            return Response({"error":"main_category cannot be null"} , status=status.HTTP_400_BAD_REQUEST)   
        return super().create(request, *args, **kwargs)
    
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
            return base_comment_serializer
    #sending commnet via post request    
    # def create(self, request, *args, **kwargs):
    #     theme_href=request.data.pop("themeHref")
    #     theme_instance=get_object_or_404(theme,href=theme_href)
    #     request.data["theme"]=theme_instance.id
    #     request.data["creator"]=request.user.id
    #     return super().create(request,*args,**kwargs)
    @action(detail=False, methods=["post"],url_path='post_comment/(?P<href>[^/.]+)',permission_classes=[IsAuthenticated])
    def post_comment(self,request,*args,**kwargs):
        print("print kwargs is : ", kwargs)
        theme_instance=get_object_or_404(theme,href=self.kwargs["href"])
        request.data["theme"]=theme_instance.id
        request.data["creator"]=request.user.id
        print(request.data)
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
    #get the comments in the theme info page base on the href of the theme being sent by client
    @action(detail=False,methods=["GET"],url_path='theme_comments/(?P<href>[^/.]+)')
    def theme_comments(self, request, *args, **kwargs):
        theme_instance = get_object_or_404(theme,href=kwargs["href"])
        comments = comment.objects.filter(theme=theme_instance.id , isAnswer = False)
        average_score = comments.aggregate(Avg("score"))["score__avg"]
        comments_serializer = allCommentSerializer(comments, many = True, context = {"average_score" : average_score})
        return Response(comments_serializer.data,status=status.HTTP_200_OK)
    
    @action(methods=['put'], detail=True)
    def accept_reject_comment(self, request, *args, **kwargs):
        """
        Toggle the 'answer' field of a comment.
        """
        try:
            comment = self.get_object()
            comment.answer = not comment.answer  # Toggle the answer field
            comment.save()
            serializer=commentSerializer(comment)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['put'], detail=True)
    def toggle_best_comment(self, request,*args,**kwargs):
        try:
            comment = self.get_object()
            comment.best_comment = not comment.best_comment  # Toggle the best_comment field
            comment.save()
            serializer=commentSerializer(comment)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
        
class getPopularThemes(ListAPIView):
    serializer_class=ThemeModelSerializer
    def get_queryset(self):
        return theme.objects.annotate(average_score=Avg("comments__score")).order_by("-average_score")
    
class getLastThemes(ListAPIView):
    serializer_class=ThemeModelSerializer
    def get_queryset(self):
        return theme.objects.all().order_by("-created_at","-updated_at")
    
class getRelatedSubMenus(ListAPIView):
    serializer_class=categoryModelSerializer
    def get_queryset(self):
        submenu_instance=get_object_or_404(category,href=self.kwargs["href"])
        return category.objects.filter(main_category=submenu_instance.main_category_id)
    
class searchApi(APIView):
    def get(self,request,query):
        theme_res=theme.objects.filter(
            name__icontains=query)|theme.objects.filter(
            description__icontains=query)|theme.objects.filter(
            href__icontains=query)
        article_res=Article.objects.filter(
            title__icontains=query)|Article.objects.filter(
            description__icontains=query)|Article.objects.filter(
            href__icontains=query)
        theme_serializer=ThemeModelSerializer(theme_res,many=True)
        article_serializer=allArticleSerializer(article_res,many=True)
        return Response({"themes":theme_serializer.data,"articles":article_serializer.data})
    
class articleViewset(viewsets.ModelViewSet):
    permission_classes=[isAdminOrReadonly]
    serializer_class=allArticleSerializer
    parser_classes=[MultiPartParser]
    def get_queryset(self):
        if self.request.user.is_staff == True:
            return Article.objects.all() #show draft articles only to admins
        
        return Article.objects.filter(publish=True)
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny], url_path='article_info/(?P<href>[^/.]+)')
    def article_info(self, request, *args, **kwargs):
        article_instance=get_object_or_404(Article,href=kwargs["href"], publish=True)         
        serializer = self.get_serializer(article_instance)
        return Response(serializer.data,status=status.HTTP_200_OK)  
    
    @action(detail=False,methods=["post"],permission_classes=[AllowAny])
    def publish_article(self,request,*args,**kwargs):
        print(request.data)
        serializer = allArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_url=upload_image(request.FILES.get("cover"))
        serializer.save(publish=True,cover=image_url["url"])
        return Response({"ok":"your article published successfully"},status=status.HTTP_200_OK) 
    
    @action(detail=False,methods=["post"],permission_classes=[AllowAny])
    def draft_article(self,request,*args,**kwargs):
        serializer = allArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_url=upload_image(request.FILES.get("cover"))
        serializer.save(publish=False,cover=image_url["url"])
        return Response({"ok":"your article drafted successfully"},status=status.HTTP_200_OK)

    @action(detail=True,methods=["put"],permission_classes=[IsAdminUser])
    def publish_draft_article(self,request,*args,**kwargs):
        article = Article.objects.get(id=kwargs["pk"])
        if article.publish:
            return Response({"error":"this article has been published already!"},status=status.HTTP_400_BAD_REQUEST)
        article.publish = True
        article.save()
        return Response({"ok":"your draft article published successfully"},status=status.HTTP_200_OK)

def upload_image(file: InMemoryUploadedFile):
    # Validate the file
    if not isinstance(file, InMemoryUploadedFile):
        raise ValueError("Invalid file type")
    
    # Read the file in chunks
    image_data = io.BytesIO()
    for chunk in file.chunks():
        image_data.write(chunk)
    image_data.seek(0)  # Reset the file pointer

    # Verify it's an image
    try:
        with Image.open(image_data) as img:
            width, height = img.size
            mode = img.mode
    except Exception as e:
        raise ValueError(f"Failed to open image: {str(e)}")

    # Determine the file extension based on the MIME type
    mime_type, _ = file.content_type.split('/')
    if mime_type == 'image':
        extension = {'png': '.png', 'jpeg': '.jpg', 'gif': '.gif',"jfif":".jfif"}[_.lower()]
    else:
        raise ValueError("Unsupported image format")

    # Generate a unique filename
    filename = f"image_{id(file)}{extension}"

    # Save the image to storage
    try:
        # Use io.BytesIO as the file object
        path = default_storage.save(filename, io.BytesIO(image_data.getvalue()))
        
        # Open the image to verify it was saved correctly
        # img = Image.open(io.BytesIO(image_data.getvalue()))
        
        # # Resize the image if needed (optional)
        # max_width, max_height = 800, 600  # Adjust these values as needed
        # if img.width > max_width or img.height > max_height:
        #     img.thumbnail((max_width, max_height), Image.LANCZOS)
        #     img.save(path)
        
        return {"message": "Image uploaded successfully", "url": path}
    except Exception as e:
        # Clean up if something goes wrong
        if hasattr(default_storage, 'delete'):
            default_storage.delete(filename)
        elif hasattr(settings, 'DEFAULT_FILE_STORAGE') and callable(getattr(settings, 'DEFAULT_FILE_STORAGE')):
            storage_class = getattr(settings, 'DEFAULT_FILE_STORAGE')
            storage_instance = storage_class()
            storage_instance.delete(filename)
        else:
            print(f"Warning: Unable to find or instantiate default file storage.")
        
        raise Exception(f"Failed to upload image: {str(e)}")

    # @action(detail=False, methods=['get'], url_path='category/(?P<href>[^/.]+)',permission_classes=[AllowAny])
    # def themes_by_category(self, request, href=None):
    #     #get the href of the category and return the corresponding themes.
    #     try:
    #         # category_instance=category.objects.get(href=href)
    #         # themes = theme.objects.filter(category=category_instance.id)
    #         themes=theme.objects.filter(category__href=href)
    #         theme_serializer=ThemeModelSerializer(themes,many=True)
    #         return Response(theme_serializer.data,status=status.HTTP_200_OK)
    #     except:
    #         return Response({"error":"something went wronge"},status=status.HTTP_400_BAD_REQUEST)
    

            
class reservation_viewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=reservationSerializer
    queryset=Reservation.objects.all()
    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            print('we are in the get seriakzier class method with the method : ' , self.request.method)
            return readReservationSerializer
        return reservationSerializer
    
    @action(detail=False, methods=['post',"get"], url_path='reserve/(?P<theme_href>[^/.]+)',permission_classes=[IsAuthenticated])
    def process_step(self, request, theme_href=None):
        #getting the occurring reservation
        if request.method == "GET":
            reservation=get_object_or_404(Reservation, customer=request.user ,theme=get_object_or_404(theme,href=theme_href))
            serializer=self.get_serializer(reservation)
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        if request.method == "POST":
            if not request.data :
                return Response({"error":"reqeust body cannot be empty"},status=status.HTTP_400_BAD_REQUEST)
            # if list(request.data.keys())[0] not in ["color","date","address","location"]:
            request_data_list=list(request.data)
            if not any(word in request_data_list for word in ["color","date","address","location"] ):
                return Response({"error":"incorrect request body given"},status=status.HTTP_400_BAD_REQUEST)
            
            state=list(request.data.keys())[0]
            theme_instance=get_object_or_404(theme,href=theme_href)
            reservation, created = Reservation.objects.get_or_create(customer=request.user, theme=theme_instance)
            if state == 'color':
                print(request.data.get("color"))
                reservation.color=request.data.get("color")
                reservation.save()
                serializer=self.get_serializer(reservation)
                return Response({'color set': serializer.data }, status=status.HTTP_200_OK)
            
            elif state == 'date':
                date = request.data.get('date')
                if not reservation.color:
                    return Response({'error': 'color is required before date'}, status=status.HTTP_400_BAD_REQUEST)
                reservation.date=date
                reservation.save()
                serializer=self.get_serializer(reservation)
                return Response({'date set': serializer.data}, status=status.HTTP_200_OK)
            
            elif state == 'address' or state=="location":
                if not reservation.color or not reservation.date:
                    return Response({'error': 'color and date is required before address'}, status=status.HTTP_400_BAD_REQUEST)
                reservation.address=request.data.get("address")
                reservation.location=request.data.get("location")
                reservation.status="done"
                reservation.save()
                serializer=self.get_serializer(reservation)
                return Response({'address set': serializer.data}, status=status.HTTP_200_OK)
            
            else:
                return Response({'error': 'unknown state'}, status=status.HTTP_400_BAD_REQUEST)
            
class normQuestionViewset(viewsets.ModelViewSet):
    queryset=Question.objects.all()
    serializer_class=normQuestionSerializer
    permission_classes=[isAdminOrReadonly]

class UserViewset(viewsets.ModelViewSet):
    serializer_class=userSerializer
    permission_classes=[IsAdminUser]
    queryset=User.objects.all()
    def get_object(self):
        if self.action == "change_profile" or self.action == "change_password":
            return User.objects.get(id=self.request.user.id)
        return super().get_object()
    
    def get_serializer_class(self, *args, **kwargs):
        if  self.action=="change_profile":
            return changeProfileSerializer
        return super().get_serializer_class()  
      
    @action(detail=False,methods=["put","patch"],permission_classes=[IsAuthenticated])
    def change_profile(self,requset):
        #the update method need the url pk but i dont want to have that so i manually added the pk here to be used
        #another option is to overwrite the get_object function 
        self.kwargs={"pk" : requset.user.id}
        if requset.method == "PATCH":
            self.update(requset,partial=True)
            user=User.objects.get(id=requset.user.id)
            return Response(self.serializer_class(user).data,status=status.HTTP_200_OK)
        self.update(requset)
        user=User.objects.get(id=requset.user.id)
        return Response(self.serializer_class(user).data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["put"],permission_classes=[IsAuthenticated])
    def change_password(self,request):
        serializer=ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # validate_old_password:
        user=request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            raise ValidationError({"error":"old password was entered incorrectly!"})
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"ok":"password changed successfully"},status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_reservations(self, request):
        reservations = Reservation.objects.filter(customer=request.user)
        serialized_reservations = noStatusReservationSerializer(reservations, many=True)
        return Response(serialized_reservations.data, status=status.HTTP_200_OK)
    
class UpdateDiscountAPIView(APIView):
    permission_classes=[IsAdminUser]
    def post(self, request, *args, **kwargs):
        try:
            discount_percentage=int(request.data["discount"])
            if discount_percentage>100 or discount_percentage<0:
                return Response({"error":"discount has to be between 0 to 100"},status=status.HTTP_400_BAD_REQUEST)
            # Update all courses with the new discount percentage
            theme.objects.update(discount=discount_percentage)
            
            return Response({"message": f"All themes updated with discount: {discount_percentage}%"}, status=status.HTTP_200_OK)
        except (ValueError,KeyError):
            return Response({"error": "Invalid discount percentage"}, status=status.HTTP_400_BAD_REQUEST)
        
class ContactUsView(APIView):
    def post(self, request, format=None):
        serializer = contactserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)       
class answerContact(APIView):
    def post(self, request):
        subject =  "answer to your application of ContactUs page " if request.data.get('subject') is None else  request.data.get('subject')
        message = request.data.get('message')
        contact_id = request.data.get('contactID')

        contact_instance = get_object_or_404(contact,id=contact_id)
        recipient_email=contact_instance.email
        contact_instance.answer=True
        # Trigger the async task
        try:
            send_email_task.delay(subject, message, recipient_email)
            return Response({"status": "Email is being sent"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e :
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

class contactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = contactserializer
    queryset = contact.objects.all()
    
class offViewset(viewsets.ModelViewSet):
    permission_classes=[IsAdminUser]
    serializer_class=offSerializer
    queryset=Off.objects.all()
    def create(self, request, *args, **kwargs):
        #we dont send the client the creator so we should set that here before passing it to the serialzier and getting error
        request.data["creator"]=request.user.id
        return super().create(request, *args, **kwargs)
    



    