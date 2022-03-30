from django.contrib import admin
from rest_framework import routers
from django.urls import include, path

from customers.api.views.customerView import CustomerViewSet, CustomerRetrieveByEmail, CustomerLogin

router = routers.DefaultRouter()

router.register(r'customers', CustomerViewSet, basename='customers')


urlpatterns = [
    # path('', include(router.urls), name="customers"),
    # path('customers/', CustomerViewSet.as_view({'post':'create'}), name='create'),
    path('customers/<str:email>', CustomerViewSet.as_view({'get': 'retrieve'}), name='get'),
    path('customers/byEmail/<str:email>', CustomerRetrieveByEmail.as_view(), name='findByEmail'),
    path('customers/login/<str:email>', CustomerLogin.as_view(), name='login'),
    # path('snippets/<int:pk>/', snippet_detail, name='snippet-detail'),
    # path('snippets/<int:pk>/highlight/', snippet_highlight, name='snippet-highlight'),
    # path('users/', user_list, name='user-list'),
    # path('users/<int:pk>/', user_detail, name='user-detail')
    # path('<pk>/', UserViewSet.as_view()),
]
