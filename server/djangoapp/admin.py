from django.contrib import admin
from .models import CarMake, CarModel


# Register CarMake model
@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'country')  # fields to display in admin list
    search_fields = ('name',)  # enable search by name

# Register CarModel model
@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year', 'dealer_id')  # fields to display
    list_filter = ('type', 'year', 'car_make')  # filter sidebar
    search_fields = ('name', 'car_make__name')  # search by model or make name

# CarModelInline class

# CarModelAdmin class

# CarMakeAdmin class with CarModelInline

# Register models here
