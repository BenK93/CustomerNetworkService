from rest_framework import permissions, status, viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from customers.api.serializers.customersSerializers import CustomerCreateSerializer, CustomerRetrieveSerializer
from customers.models import Customer


# to creator boundary
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'email'
    # Source: https://stackoverflow.com/q/55714961
    lookup_value_regex = r'[^/]+'

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerCreateSerializer
        if self.action == 'retrieve':
            return CustomerRetrieveSerializer
        return CustomerCreateSerializer

    def create(self, request, *args, **kwargs):
        customer = Customer.objects.filter(email=request.data['email'])
        if customer:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            response = serializer.data
            del response['password']
            return Response(response, status=status.HTTP_201_CREATED)


# getter boundary
class CustomerRetrieveByEmail(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRetrieveSerializer
    lookup_field = 'email'


class CustomerLogin(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRetrieveSerializer
    lookup_field = 'email'

    def retrieve(self, request, *args, **kwargs):
        password = request.query_params.get('password', None)
        if not password:
            response = {"details": "no password were given"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        if password != instance.password:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
