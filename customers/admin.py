
from django.contrib import admin

from customers.models import Customer, Name

# Register your models here.
admin.site.register(Name)
admin.site.register(Customer)
