from django.contrib import admin
from .models import Client, Car, Repair


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'company_name', 'phone', 'contact_person', 'address')
    search_fields = ('company_name', 'contact_person')
    list_filter = ('company_name',)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('car_id', 'car_model', 'new_car_price', 'client')
    list_filter = ('car_model',)
    search_fields = ('car_model', 'client__company_name')


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ('repair_id', 'start_date', 'car', 'repair_type', 'hour_rate', 'discount', 'hours_needed', 'total_cost', 'cost_with_discount')
    list_filter = ('repair_type', 'start_date')
    search_fields = ('car__car_model', 'car__client__company_name')
    date_hierarchy = 'start_date'
    
    def total_cost(self, obj):
        return f"{obj.total_cost:.2f} грн"
    total_cost.short_description = 'Вартість'
    
    def cost_with_discount(self, obj):
        return f"{obj.cost_with_discount:.2f} грн"
    cost_with_discount.short_description = 'Зі знижкою'
