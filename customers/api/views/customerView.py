from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from customers.api.serializers.customerSerializer import CustomerSerializer
from customers.models import Customer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.AllowAny, ]

    def create(self, request, *args, **kwargs):
        customer = Customer.objects.filter(email=request.data['email'])
        if customer:
            return Response({},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data,status=status.HTTP_201_CREATED)


class CustomerRetrieve(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'email'

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)
