from __future__ import annotations

from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from customers.api.helpers.paginatiions import CustomPagination
from customers.api.serializers.customersSerializers import CustomerCreateSerializer, CustomerRetrieveSerializer, \
    CustomerUpdateSerializer, CustomerFriendsSerializer, CustomerRetrieveFriendsSerializer
from customers.models import Customer, Role


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
        if self.action == 'retrieve' or self.action == 'list':
            return CustomerRetrieveSerializer
        if self.action == 'update':
            return CustomerUpdateSerializer
        return CustomerCreateSerializer

    def create(self, request, *args, **kwargs):
        customer = Customer.objects.filter(email=request.data['email'])
        if customer:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            data = request.data
            if data['roles']:
                for role in data['roles']:
                    if role == "":
                        return Response(status=status.HTTP_400_BAD_REQUEST)
            data['roles'] = _convert_roles_to_object(data['roles'])
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            response = serializer.data
            del response['password']
            return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        data.pop('email', None)
        data['roles'] = _convert_roles_to_object(data['roles'])
        super().update(request, args, kwargs)
        return Response(status=status.HTTP_200_OK)


class CustomerFriendshipView(UpdateAPIView, RetrieveAPIView, GenericViewSet):
    queryset = Customer.objects.all()
    pagination_class = CustomPagination
    serializer_class = CustomerFriendsSerializer
    lookup_field = 'email'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerRetrieveFriendsSerializer
        return CustomerFriendsSerializer

    def update(self, request, *args, **kwargs):
        email = request.data.pop('email', None)
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        if instance.email == email:
            return Response(status=status.HTTP_418_IM_A_TEAPOT)
        customer = Customer.objects.get(email=email)
        customer.friends.add(instance)
        instance.friends.add(customer)
        instance.save()
        customer.save()
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        page, size = int(request.query_params.get('page', 0)), int(request.query_params.get('size', 1))
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        friends = serializer.data['friends']
        paginated_friends = friends[page * size: page * size + size]
        return Response(paginated_friends, status=status.HTTP_200_OK)


# getter boundary
class CustomersSearchView(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRetrieveSerializer

    def retrieve(self, request, *args, **kwargs):
        page, size, sortBy, sortOrder = int(request.query_params.get('page', 0)) , int(request.query_params.get('size', 1)), \
                request.query_params.get('sortBy', 'email'), request.query_params.get('sortOrder', 'ASC')
        data = []
        for customer in self.get_queryset().values():
            serializer = self.get_serializer(data=customer)
            print(customer)
            serializer.is_valid(raise_exception=True)
            print(serializer.data)
            data.append(serializer.data)
        print(data)
        serializer = self.get_serializer(data=list(self.get_queryset().values()), many=True)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)



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


@api_view(['DELETE'])
def deleteAllCustomers(request):
    Customer.objects.all().delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def _convert_roles_to_object(roles_array: list[str]) -> list[dict[str, str]]:
    """
    Converts the roles array we get in the json to objects array where every object represents a role.
    """
    return [{"title": value} for value in roles_array]
