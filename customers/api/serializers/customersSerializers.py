from rest_framework import serializers

from customers.models import Customer, Name


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name
        fields = ['first', 'last']


class CustomerRetrieveSerializer(serializers.ModelSerializer):
    name = NameSerializer(many=False)

    class Meta:
        model = Customer
        fields = ['email', 'name', 'birthdate', 'role']
        # lookup_field = 'email'

class CustomerCreateSerializer(serializers.ModelSerializer):
    name = NameSerializer(many=False)

    class Meta:
        model = Customer
        fields = ['email', 'password', 'name', 'birthdate', 'role']
        lookup_field = 'email'

    def create(self, validated_data):
        name_data = validated_data.pop('name')
        name = Name(
            first=name_data['first'],
            last=name_data['last']
        )
        name.save()
        customer = Customer.objects.create(name=name, **validated_data)
        return customer
