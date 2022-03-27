from rest_framework import permissions, status, viewsets

from customers.models import Customer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    pass
