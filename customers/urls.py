from rest_framework import routers
from django.urls import include, path

from customers.api.views.customerView import CustomerViewSet, CustomerLogin, \
    CustomersSecondLevelFriendsView, create_delete_customers, CustomerFriendshipView, CustomersSearchView

router = routers.DefaultRouter(trailing_slash=True)

router.register(r'customers', CustomerViewSet, basename='customers')

urlpatterns = [
    path('customers/', create_delete_customers, name='deleteAll'),
    path('', include(router.urls), name="customers"),
    path('customers/<str:email>/friends', CustomerFriendshipView.as_view({'get': 'retrieve', 'put': 'update'}), name='friends'),
    path('customers/<str:email>/friends/secondLevel', CustomersSecondLevelFriendsView.as_view(), name='friends of friends'),
    path('customers/search', CustomersSearchView.as_view(), name='search'),
    path('customers/byEmail/<str:email>', CustomerViewSet.as_view({'get': 'retrieve'}), name='findByEmail'),
    path('customers/login/<str:email>', CustomerLogin.as_view(), name='login'),
]
