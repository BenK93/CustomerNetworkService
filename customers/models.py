from django.db import models
from multiselectfield import MultiSelectField
# Create your models here.

ROLES = ((1, 'goldCustomer'),
         (2, 'platinumClub'),
         (3, 'primeService'),)


class Name(models.Model):
    first = models.CharField(max_length=255, blank=False)
    last = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f'{self.first} {self.last}'


class Customer(models.Model):
    email = models.CharField(max_length=255)
    name = models.ForeignKey(
        Name, on_delete=models.CASCADE, blank=False, default=None)
    birthdate = models.DateField(default=None)
    role = MultiSelectField(choices=ROLES, default=1)

    def __str__(self):
        return f'{self.name}'
