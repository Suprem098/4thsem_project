from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Medicine, Supplier, Customer, Order, OrderItem, Appointment, Doctor, SupplierRequest, Prescription, PrescriptionItem, DoctorSchedule

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'quantity', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialization', 'phone', 'email']

class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['doctor', 'day_of_week', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['medicine', 'quantity']

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=[('Customer', 'Customer'), ('Doctor', 'Doctor'), ('Staff', 'Staff')], widget=forms.Select(attrs={'id': 'id_role'}))
    specialization = forms.CharField(max_length=100, required=False, help_text='Required if role is Doctor.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        specialization = cleaned_data.get("specialization")

        if role == "Doctor" and not specialization:
            self.add_error('specialization', 'This field is required for doctors.')
        
        return cleaned_data

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'reason']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SupplierRequestForm(forms.ModelForm):
    class Meta:
        model = SupplierRequest
        fields = ['supplier', 'medicine', 'quantity']

class StaffRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'remarks']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = User.objects.filter(is_staff=False)

class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'dosage', 'frequency', 'duration']
