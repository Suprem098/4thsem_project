from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='pharmacy/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Medicines
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/invoice/', views.order_invoice, name='order_invoice'),
    path('orders/<int:pk>/status/<str:status>/', views.order_status, name='order_status'),
    path('orders/<int:order_pk>/items/<int:item_pk>/delete/', views.order_item_delete, name='order_item_delete'),

    # Registration
    path('register/', views.register, name='register'),

    # Customer Features
    path('shop/', views.customer_medicine_list, name='customer_medicine_list'),
    path('shop/buy/<int:pk>/', views.buy_medicine, name='buy_medicine'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:pk>/approve/', views.appointment_approve, name='appointment_approve'),
    path('appointments/<int:pk>/reject/', views.appointment_reject, name='appointment_reject'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Doctor Schedules
    path('doctors/schedules/', views.doctor_schedule_list, name='doctor_schedule_list'),
    path('doctors/schedules/add/', views.doctor_schedule_create, name='doctor_schedule_create'),
    path('doctors/schedules/<int:pk>/delete/', views.doctor_schedule_delete, name='doctor_schedule_delete'),

    # Supplier Requests
    path('requests/', views.supplier_request_list, name='supplier_request_list'),
    path('requests/add/', views.supplier_request_create, name='supplier_request_create'),
    path('requests/<int:pk>/status/<str:status>/', views.supplier_request_status, name='supplier_request_status'),

    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),

    # Reports
    path('reports/sales/', views.sales_report, name='sales_report'),

    # Prescriptions
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/add/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:pk>/action/<str:action>/', views.prescription_action, name='prescription_action'),

    # User Approval
    path('users/pending/', views.pending_users_list, name='pending_users_list'),
    path('users/<int:pk>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:pk>/reject/', views.reject_user, name='reject_user'),
]
