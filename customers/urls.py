from django.contrib import admin
from rest_framework import routers
from django.urls import include, path

from customers.api.views.customerView import CustomerViewSet, CustomerRetrieveByEmail, CustomerLogin, \
    deleteAllCustomers, CustomerFriendshipView, CustomersSearchView

router = routers.DefaultRouter(trailing_slash=True)

router.register(r'customers', CustomerViewSet, basename='customers')

urlpatterns = [
    path('', include(router.urls), name="customers"),

    path('customers', deleteAllCustomers, name='deleteAll'),
    path('customers/<str:email>/friends', CustomerFriendshipView.as_view({'get': 'retrieve', 'put': 'update'}), name='friends'),
    path('customers/search', CustomersSearchView.as_view(), name='search'),
    path('customers/byEmail/<str:email>', CustomerRetrieveByEmail.as_view(), name='findByEmail'),
    path('customers/login/<str:email>', CustomerLogin.as_view(), name='login'),
]
