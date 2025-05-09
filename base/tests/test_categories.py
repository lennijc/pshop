from rest_framework.test import APIClient
from rest_framework import status
import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestCreateCategory:
    def test_if_user_is_anonymous_returns_401(self):
        client = APIClient()
        response = client.post('/api/category/', {'title':'a','href':'b'}, format="json")
        print('content of the respone is: ', response.content)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_returns_403(self):
        client = APIClient()
        client.force_authenticate(user={})
        response = client.post('/api/category/', {'title':'a','href':'b'}, format="json")
        print('content of the respone is: ', response.content)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/api/category/', {'title':'a','href':''}, format="json")
        print('content of the respone is: ', response.content)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
    
    # def test_if_data_is_valid_returns_201(self):
    #     client = APIClient()
    #     client.force_authenticate(user={})
    #     response = client.post('/api/category/', {'title':'a','href':''}, format="json")
    #     print('content of the respone is: ', response.content)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST
    #     assert response.data['title'] is not None
