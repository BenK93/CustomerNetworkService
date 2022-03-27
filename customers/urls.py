from django.contrib import admin
from rest_framework import routers
from django.urls import include, path

from customers.api.views.customerView import CustomerViewSet

router = routers.DefaultRouter()

# router.register('', CustomerViewSet)


urlpatterns = [
    # path('', include(router.urls)),
    # path('<pk>/', UserViewSet.as_view()),
]
