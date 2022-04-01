from typing import Mapping

from rest_framework import serializers

from customers.models import Customer, Name, Role


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name
        fields = ['first', 'last']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['title']


class CustomerRetrieveSerializer(serializers.ModelSerializer):
    name = NameSerializer(many=False)
    roles = RoleSerializer(many=True)

    class Meta:
        model = Customer
        fields = ['email', 'name', 'birthdate', 'roles']

    @property
    def data(self):
        temp_data = super().data
        # Cast the roles array to a strings array.
        temp_data['roles'] = [value['title'] for value in temp_data['roles']]
        return temp_data


class CustomerCreateSerializer(serializers.ModelSerializer):
    name = NameSerializer(many=False)
    roles = RoleSerializer(many=True)

    class Meta:
        model = Customer
        fields = ['email', 'password', 'name', 'birthdate', 'roles']
        lookup_field = 'email'

    def create(self, validated_data):
        name = _resolve_name(validated_data.pop('name'))
        roles = validated_data.pop('roles')

        customer = Customer.objects.create(name=name, **validated_data)
        _resolve_roles(customer, roles)
        customer.save()
        return customer

    @property
    def data(self):
        temp_data = super().data
        temp_data['roles'] = [value['title'] for value in temp_data['roles']]
        return temp_data


def _resolve_name(name_data: Mapping) -> Name:
    name = Name.objects.filter(**name_data).first()
    if not name:
        name = Name(
                first=name_data['first'],
                last=name_data['last']
        )
        name.save()
    return name


def _resolve_roles(customer: Customer, roles_data):
    for role in roles_data:
        role_obj = Role.objects.filter(**role).first()
        if not role_obj:
            role_obj = Role(**role)
            role_obj.save()
        customer.roles.add(role_obj)
