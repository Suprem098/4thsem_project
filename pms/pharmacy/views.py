from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.forms import inlineformset_factory
from .models import Medicine, Supplier, Customer, Order, OrderItem, Appointment, Doctor, SupplierRequest, Prescription, PrescriptionItem, DoctorSchedule
from .forms import MedicineForm, SupplierForm, CustomerForm, OrderForm, OrderItemForm, UserRegistrationForm, AppointmentForm, DoctorForm, SupplierRequestForm, StaffRegistrationForm, PrescriptionForm, PrescriptionItemForm, DoctorScheduleForm

@login_required
def dashboard(request):
    # Redirect doctors to their own dashboard
    if hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')

    # Redirect customers to their own dashboard
    if not request.user.is_staff:
        return render(request, 'pharmacy/customer_dashboard.html')

    medicine_count = Medicine.objects.count()
    supplier_count = Supplier.objects.count()
    customer_count = Customer.objects.count()
    order_count = Order.objects.count()
    
    # Alert for medicines expiring in the next 30 days
    expiring_medicines = Medicine.objects.filter(expiry_date__lte=timezone.now().date() + timedelta(days=30), expiry_date__gte=timezone.now().date())
    
    # Alert for medicines with low stock (e.g., less than 10)
    low_stock_medicines = Medicine.objects.filter(quantity__lte=10)

    # Pending Approvals / Admin Actions
    pending_orders_count = Order.objects.filter(status='Pending').count()
    pending_requests_count = SupplierRequest.objects.filter(status='Pending').count()
    pending_prescriptions_count = Prescription.objects.filter(status='Pending').count()
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()

    # Analytics (Today's Snapshot)
    today = timezone.now().date()
    todays_revenue = Order.objects.filter(order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    todays_orders_count = Order.objects.filter(order_date__date=today).count()

    # Chart Data (Last 7 Days)
    seven_days_ago = today - timedelta(days=6)
    sales_data = Order.objects.filter(order_date__date__gte=seven_days_ago)\
        .annotate(date=TruncDate('order_date'))\
        .values('date')\
        .annotate(revenue=Sum('total_amount'))\
        .order_by('date')
    
    sales_dict = {item['date']: item['revenue'] for item in sales_data}
    chart_labels = []
    chart_data = []
    
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        chart_labels.append(day.strftime('%b %d'))
        chart_data.append(float(sales_dict.get(day, 0)))

    # Activity Logs (Recent Orders)
    recent_orders = Order.objects.select_related('customer').order_by('-order_date')[:5]

    context = {
        'medicine_count': medicine_count,
        'supplier_count': supplier_count,
        'customer_count': customer_count,
        'order_count': order_count,
        'expiring_medicines': expiring_medicines,
        'low_stock_medicines': low_stock_medicines,
        'pending_orders_count': pending_orders_count,
        'pending_requests_count': pending_requests_count,
        'pending_prescriptions_count': pending_prescriptions_count,
        'pending_appointments_count': pending_appointments_count,
        'todays_revenue': todays_revenue,
        'todays_orders_count': todays_orders_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'recent_orders': recent_orders,
    }
    return render(request, 'pharmacy/dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, 'doctor'):
        return redirect('dashboard')
    
    doctor = request.user.doctor
    today = timezone.now().date()
    
    # Appointments for today and upcoming
    todays_appointments = Appointment.objects.filter(doctor=doctor, date__date=today).order_by('date')
    upcoming_appointments = Appointment.objects.filter(doctor=doctor, date__date__gt=today).order_by('date')
    
    context = {
        'doctor': doctor,
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'pharmacy/doctor_dashboard.html', context)

@login_required
def medicine_list(request):
    query = request.GET.get('q')
    if query:
        medicines = Medicine.objects.filter(name__icontains=query)
    else:
        medicines = Medicine.objects.all()
    return render(request, 'pharmacy/medicine_list.html', {'medicines': medicines})

@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Add Medicine'})

@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Edit Medicine'})

@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        return redirect('medicine_list')
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': medicine, 'title': 'Medicine'})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'pharmacy/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': supplier, 'title': 'Supplier'})

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'pharmacy/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Edit Customer'})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': customer, 'title': 'Customer'})

@login_required
def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.all().order_by('-order_date')
    else:
        if hasattr(request.user, 'customer'):
            orders = Order.objects.filter(customer=request.user.customer).order_by('-order_date')
        else:
            orders = Order.objects.none()
    return render(request, 'pharmacy/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Create Order'})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if not request.user.is_staff:
        if hasattr(request.user, 'customer') and order.customer != request.user.customer:
            return redirect('dashboard')

    items = order.items.all()
    form = None

    if request.user.is_staff:
        if request.method == 'POST':
            form = OrderItemForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                if item.medicine.quantity >= item.quantity:
                    item.order = order
                    item.medicine.quantity -= item.quantity
                    item.medicine.save()
                    item.save()
                    order.total_amount += item.medicine.price * item.quantity
                    order.save()
                    return redirect('order_detail', pk=order.pk)
                else:
                    form.add_error('quantity', 'Not enough stock available.')
        else:
            form = OrderItemForm()
            
    return render(request, 'pharmacy/order_detail.html', {'order': order, 'items': items, 'form': form})

@login_required
def order_invoice(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, 'pharmacy/invoice.html', {'order': order, 'items': items})

@login_required
def order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)
    
    # Security check: Customers can only cancel their own orders
    if not request.user.is_staff:
        if not hasattr(request.user, 'customer') or order.customer != request.user.customer:
            return redirect('order_list')
        if status != 'Cancelled':
            return redirect('order_list')

    # Only allow changing status if it is currently Pending
    if order.status == 'Pending':
        if status == 'Cancelled':
            # Restore stock for all items in the order
            for item in order.items.all():
                item.medicine.quantity += item.quantity
                item.medicine.save()
        order.status = status
        order.save()
    return redirect('order_list')

@login_required
def order_item_delete(request, order_pk, item_pk):
    order = get_object_or_404(Order, pk=order_pk)
    item = get_object_or_404(OrderItem, pk=item_pk, order=order)
    if request.method == 'POST':
        # Restore stock
        item.medicine.quantity += item.quantity
        item.medicine.save()
        # Update order total
        order.total_amount -= item.medicine.price * item.quantity
        order.save()
        item.delete()
        return redirect('order_detail', pk=order.pk)
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': item, 'title': 'Order Item'})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            
            if role == 'Customer':
                user.is_active = True
                user.save()
                Customer.objects.create(user=user, name=user.username, email=user.email, phone='')
                login(request, user)
                return redirect('dashboard')
            elif role == 'Doctor':
                user.is_active = False
                user.save()
                specialization = form.cleaned_data.get('specialization')
                Doctor.objects.create(
                    user=user, 
                    name=user.username, 
                    email=user.email, 
                    phone='',
                    specialization=specialization
                )
                messages.success(request, 'Account created. Please wait for admin approval.')
                return redirect('login')
            elif role == 'Staff':
                user.is_active = False
                user.is_staff = True
                user.save()
                messages.success(request, 'Account created. Please wait for admin approval.')
                return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'pharmacy/register.html', {'form': form, 'title': 'Create an Account'})

@login_required
def customer_medicine_list(request):
    query = request.GET.get('q')
    if query:
        medicines = Medicine.objects.filter(name__icontains=query)
    else:
        medicines = Medicine.objects.all()
    is_doctor = hasattr(request.user, 'doctor')
    return render(request, 'pharmacy/customer_medicine_list.html', {'medicines': medicines, 'is_doctor': is_doctor})

@login_required
def buy_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if medicine.quantity >= quantity:
            # Ensure user has a customer profile
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={'name': request.user.username, 'email': request.user.email, 'phone': ''}
            )
            
            order = Order.objects.create(customer=customer, total_amount=medicine.price * quantity)
            OrderItem.objects.create(order=order, medicine=medicine, quantity=quantity)
            
            medicine.quantity -= quantity
            medicine.save()
            return redirect('order_detail', pk=order.pk)
        else:
            messages.error(request, 'Not enough stock available.')
    return render(request, 'pharmacy/purchase_form.html', {'medicine': medicine})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={'name': request.user.username, 'email': request.user.email, 'phone': ''}
            )
            appointment.customer = customer
            appointment.status = 'Pending'
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Please wait for approval.')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Book Appointment'})

@login_required
def appointment_list(request):
    if request.user.is_staff:
        appointments = Appointment.objects.all().order_by('-date')
    elif hasattr(request.user, 'doctor'):
        appointments = Appointment.objects.filter(doctor=request.user.doctor).order_by('-date')
    else:
        customer, created = Customer.objects.get_or_create(
            user=request.user,
            defaults={'name': request.user.username, 'email': request.user.email, 'phone': ''}
        )
        appointments = Appointment.objects.filter(customer=customer).order_by('-date')
    return render(request, 'pharmacy/appointment_list.html', {'appointments': appointments})

@login_required
def appointment_approve(request, pk):
    if not (request.user.is_staff or hasattr(request.user, 'doctor')):
        return redirect('dashboard')
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Approved'
    appointment.save()
    messages.success(request, 'Appointment approved.')
    return redirect('appointment_list')

@login_required
def appointment_reject(request, pk):
    if not (request.user.is_staff or hasattr(request.user, 'doctor')):
        return redirect('dashboard')
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Rejected'
    appointment.save()
    messages.success(request, 'Appointment rejected.')
    return redirect('appointment_list')

@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'pharmacy/doctor_list.html', {'doctors': doctors})

@login_required
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Add Doctor'})

@login_required
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Edit Doctor'})

@login_required
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        return redirect('doctor_list')
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': doctor, 'title': 'Doctor'})

@login_required
def doctor_schedule_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    schedules = DoctorSchedule.objects.all().order_by('doctor', 'day_of_week')
    return render(request, 'pharmacy/doctor_schedule_list.html', {'schedules': schedules})

@login_required
def doctor_schedule_create(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctor_schedule_list')
    else:
        form = DoctorScheduleForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Add Doctor Schedule'})

@login_required
def doctor_schedule_delete(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        return redirect('doctor_schedule_list')
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': schedule, 'title': 'Doctor Schedule'})

@login_required
def supplier_request_list(request):
    requests = SupplierRequest.objects.all().order_by('-created_at')
    return render(request, 'pharmacy/supplier_request_list.html', {'requests': requests})

@login_required
def supplier_request_create(request):
    if request.method == 'POST':
        form = SupplierRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_request_list')
    else:
        form = SupplierRequestForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Request Medicine from Supplier'})

@login_required
def supplier_request_status(request, pk, status):
    req = get_object_or_404(SupplierRequest, pk=pk)
    if status == 'Completed' and req.status != 'Completed':
        req.medicine.quantity += req.quantity
        req.medicine.save()
    req.status = status
    req.save()
    return redirect('supplier_request_list')

@login_required
def customer_profile(request):
    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={'name': request.user.username, 'email': request.user.email, 'phone': ''}
    )
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'pharmacy/customer_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('customer_profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'pharmacy/change_password.html', {'form': form})

@login_required
def staff_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    staff_members = User.objects.filter(is_staff=True)
    return render(request, 'pharmacy/staff_list.html', {'staff_members': staff_members})

@login_required
def staff_create(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_list')
    else:
        form = StaffRegistrationForm()
    return render(request, 'pharmacy/generic_form.html', {'form': form, 'title': 'Add Staff Member'})

@login_required
def staff_delete(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    staff_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if staff_user != request.user: # Prevent deleting yourself
            staff_user.delete()
        return redirect('staff_list')
    return render(request, 'pharmacy/generic_confirm_delete.html', {'object': staff_user, 'title': 'Staff Member'})

@login_required
def sales_report(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Date Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    orders = Order.objects.all()
    
    if start_date:
        orders = orders.filter(order_date__date__gte=start_date)
    if end_date:
        orders = orders.filter(order_date__date__lte=end_date)
    
    # Calculate totals based on filtered orders
    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    
    # Daily Sales Breakdown based on filtered orders
    daily_sales = orders.annotate(date=TruncDate('order_date')).values('date').annotate(
        daily_revenue=Sum('total_amount'),
        daily_orders=Count('id')
    ).order_by('-date')
    
    context = {
        'total_revenue': total_revenue, 
        'total_orders': total_orders, 
        'daily_sales': daily_sales,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'pharmacy/sales_report.html', context)

@login_required
def prescription_list(request):
    if request.user.is_staff:
        prescriptions = Prescription.objects.all().order_by('-date_created')
    else:
        # Patients see their own, Doctors see ones they created
        prescriptions = Prescription.objects.filter(patient=request.user) | Prescription.objects.filter(doctor=request.user)
        prescriptions = prescriptions.distinct().order_by('-date_created')
    return render(request, 'pharmacy/prescription_list.html', {'prescriptions': prescriptions})

@login_required
def prescription_create(request):
    # Assuming any staff or authenticated user (doctor) can create
    PrescriptionItemFormSet = inlineformset_factory(Prescription, PrescriptionItem, form=PrescriptionItemForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user
            prescription.save()
            formset.instance = prescription
            formset.save()
            messages.success(request, 'Prescription created successfully.')
            return redirect('prescription_list')
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()
    
    return render(request, 'pharmacy/prescription_form.html', {'form': form, 'formset': formset})

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    # Security check
    if not request.user.is_staff and request.user != prescription.patient and request.user != prescription.doctor:
        return redirect('dashboard')
    return render(request, 'pharmacy/prescription_detail.html', {'prescription': prescription})

@login_required
def prescription_action(request, pk, action):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    prescription = get_object_or_404(Prescription, pk=pk)
    
    if action == 'approve':
        # Check stock availability
        for item in prescription.items.all():
            if item.medicine.quantity < 1: # Assuming 1 unit per item for simplicity
                messages.error(request, f"Not enough stock for {item.medicine.name}")
                return redirect('prescription_detail', pk=pk)
        
        prescription.status = 'Approved'
        prescription.save()
        messages.success(request, 'Prescription approved.')
        
    elif action == 'reject':
        prescription.status = 'Rejected'
        prescription.save()
        messages.warning(request, 'Prescription rejected.')
        
    elif action == 'dispense':
        if prescription.status != 'Approved':
            messages.error(request, 'Prescription must be approved first.')
            return redirect('prescription_detail', pk=pk)
            
        # Create Order
        try:
            customer = prescription.patient.customer
        except Customer.DoesNotExist:
            messages.error(request, 'Patient does not have a customer profile.')
            return redirect('prescription_detail', pk=pk)
            
        order = Order.objects.create(customer=customer, total_amount=0)
        total = 0
        
        for item in prescription.items.all():
            # Dispense 1 unit per prescribed item (logic can be enhanced to support qty)
            qty = 1
            if item.medicine.quantity >= qty:
                OrderItem.objects.create(order=order, medicine=item.medicine, quantity=qty)
                item.medicine.quantity -= qty
                item.medicine.save()
                total += item.medicine.price * qty
        
        order.total_amount = total
        order.save()
        
        prescription.status = 'Dispensed'
        prescription.save()
        messages.success(request, 'Medicines dispensed and order created.')
        return redirect('order_detail', pk=order.pk)
        
    return redirect('prescription_detail', pk=pk)

@login_required
def pending_users_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    pending_users = User.objects.filter(is_active=False).order_by('-date_joined')
    return render(request, 'pharmacy/pending_users_list.html', {'pending_users': pending_users})

@login_required
def approve_user(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} approved successfully.')
    return redirect('pending_users_list')

@login_required
def reject_user(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, f'User {user.username} rejected.')
    return redirect('pending_users_list')
