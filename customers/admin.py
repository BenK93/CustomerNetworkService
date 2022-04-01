from django.contrib import admin

from customers.models import Customer, Name, Role

# Register your models here.
admin.site.register(Name)
admin.site.register(Role)
admin.site.register(Customer)
