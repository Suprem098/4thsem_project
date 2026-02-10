from django.contrib import admin
from .models import Medicine, Supplier, Customer, Order, OrderItem, SupplierRequest

admin.site.register(Medicine)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(SupplierRequest)