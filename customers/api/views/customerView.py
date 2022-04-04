from __future__ import annotations

from typing import Dict, List

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

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
        if self.action == 'retrieve' or self.action == 'list':
            return CustomerRetrieveSerializer
        if self.action == 'update':
            return CustomerUpdateSerializer
        return CustomerCreateSerializer

    def update(self, request, *args, **kwargs):
        data = request.data
        data.pop('email', None)
        data['roles'] = _convert_roles_to_object(data['roles'])
        super().update(request, args, kwargs)
        return Response(status=status.HTTP_200_OK)


class CustomerFriendshipView(UpdateAPIView, RetrieveAPIView, GenericViewSet):
    queryset = Customer.objects.all()
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
        page, size, sort_by, sort_order = (int(request.query_params.get('page', 0)),
                                           int(request.query_params.get('size', 1)),
                                           request.query_params.get('sortBy', 'email'),
                                           request.query_params.get('sortOrder', 'ASC'))

        # Handle sort by arguments
        if sort_by not in ('email', 'name', 'birthdate'):
            return Response(f'Invalid value for field sortBy ({sort_by})', status=status.HTTP_400_BAD_REQUEST)

        if sort_by == 'name':
            sort_fields = ['name__first', 'name__last']
        else:
            sort_fields = [sort_by]

        # Handle sort order arguments
        if sort_order not in ('ASC', 'DESC'):
            return Response(f'Invalid value for field sortOrder ({sort_order})', status=status.HTTP_400_BAD_REQUEST)

        if sort_order == 'DESC':
            sort_fields = map(lambda field: f'-{field}', sort_fields)

        queryset = self.get_queryset().order_by(*sort_fields)
        # Handle filter argument
        if request.query_params.get('criteriaType', '') == 'byEmailDomain':
            queryset = queryset.filter(email__endswith=request.query_params['criteriaValue'])
        elif request.query_params.get('criteriaType', '') == 'byBirthYear':
            queryset = queryset.filter(birthdate__year=request.query_params['criteriaValue'])
        elif request.query_params.get('criteriaType', '') == 'byRole':
            queryset = queryset.filter(roles__title=request.query_params['criteriaValue'])

        customers = map(lambda customer: self.get_serializer(customer).data,
                        queryset[page * size: (page + 1) * size])

        return Response(customers, status=status.HTTP_200_OK)


class CustomersSecondLevelFriendsView(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRetrieveFriendsSerializer
    lookup_field = 'email'
    # Source: https://stackoverflow.com/q/55714961
    lookup_value_regex = r'[^/]+'

    def retrieve(self, request, *args, **kwargs):
        page, size = (int(request.query_params.get('page', 0)),
                      int(request.query_params.get('size', 1)))

        customer = self.get_object()
        first_level_friends = self.get_serializer(customer).data['friends']

        second_level_friends = list()
        queryset = self.get_queryset()
        for first_level_friend in first_level_friends:
            x = self.get_serializer(queryset.filter(email=first_level_friend['email']).first()).data['friends']
            second_level_friends.extend(map(dict, x))

        return Response(delete_duplicates_terrible(second_level_friends)[page * size: (page + 1) * size],
                        status=status.HTTP_200_OK)


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


def delete_duplicates_terrible(list_of_dicts: List[Dict]) -> List[Dict]:
    return_me = list()
    added_emails = set()
    for obj in list_of_dicts:
        if obj['email'] not in added_emails:
            return_me.append(obj)
            added_emails.add(obj['email'])
    return return_me


@api_view(['DELETE', 'POST', 'GET'])
def create_delete_customers(request: Request):
    if request.method == 'POST':
        data = request.data
        # Make sure all the roles are valid.
        if 'roles' in data and any(role is None or len(role) == 0 for role in data['roles']):
            return Response('Empty roles are not allowed', status=status.HTTP_400_BAD_REQUEST)

        # Check if the mail already exists.
        if Customer.objects.filter(email=data['email']):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data['roles'] = _convert_roles_to_object(data['roles'])
        serializer = CustomerCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = serializer.data
        del response['password']
        return Response(response, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        customers = map(lambda customer: CustomerRetrieveSerializer(customer).data,
                        Customer.objects.all())
        return Response(customers)

    # If the method was DELETE
    Customer.objects.all().delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def _convert_roles_to_object(roles_array: list[str]) -> list[dict[str, str]]:
    """
    Converts the roles strings array to an objects array, where every object represents a role.
    """
    return [{"title": value} for value in roles_array]
