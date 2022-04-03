from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from customers.api.helpers.paginatiions import CustomPagination
from customers.api.serializers.customersSerializers import CustomerCreateSerializer, CustomerFriendsSerializer, \
    CustomerRetrieveFriendsSerializer, CustomerRetrieveSerializer, CustomerUpdateSerializer
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
        page, size, sort_by, sort_order = int(request.query_params.get('page', 0)), int(
                request.query_params.get('size', 1)), \
                                          request.query_params.get('sortBy', 'email'), request.query_params.get(
                'sortOrder', 'ASC')
        if sort_by == 'name':
            sort_fields = ['name__first', 'name__last']
        elif sort_by == "roles":
            # Note: This doesn't make sense. roles is a collection so ordering based on it is
            sort_fields = ['roles__title']
        else:
            sort_fields = [sort_by]
        if sort_order == 'DESC':
            for i in range(len(sort_fields)):
                sort_fields[i] = f'-{sort_fields[i]}'

        queryset = self.get_queryset().order_by(*sort_fields)
        if request.query_params.get('criteriaType', '') == 'byEmailDomain':
            queryset = queryset.filter(email__endswith=request.query_params['criteriaValue'])
        elif request.query_params.get('criteriaType', '') == 'byBirthYear':
            queryset = queryset.filter(birthdate__year=request.query_params['criteriaValue'])
        print(queryset.query)
        customers = map(lambda customer: self.get_serializer(customer).data,
                        queryset[page * size: (page + 1) * size])
        # sorted_customers = sorted(customers, key=lambda x: x[sort_by], reverse=sort_order == 'DESC')
        # paginated_customers = sorted_customers[page * size: (page + 1) * size]
        # paginated_customers = list(customers)
        return Response(customers, status=status.HTTP_200_OK)


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
        print(instance, type(instance))
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
