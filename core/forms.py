from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from .models import Appointment , Doctor , Feedback , PatientProblem , Service


class DateDMYInput(forms.DateInput):
    input_type = 'text'

    def __init__(self , *args , **kwargs):
        kwargs.setdefault('format' , '%d/%m/%Y')
        attrs = kwargs.pop('attrs' , {})
        attrs.setdefault('class' , 'form-control appointment-date-input')
        attrs.setdefault('placeholder' , '31/05/2026')
        attrs.setdefault('maxlength' , '10')
        attrs.setdefault('inputmode' , 'numeric')
        attrs.setdefault('autocomplete' , 'off')
        kwargs['attrs'] = attrs
        super().__init__(*args , **kwargs)


class Time24Input(forms.TimeInput):
    input_type = 'text'

    def __init__(self , *args , **kwargs):
        kwargs.setdefault('format' , '%H:%M')
        attrs = kwargs.pop('attrs' , {})
        attrs.setdefault('class' , 'form-control')
        attrs.setdefault('placeholder' , '15:00')
        attrs.setdefault('pattern' , '([01]?[0-9]|2[0-3]):[0-5][0-9]')
        attrs.setdefault('inputmode' , 'numeric')
        kwargs['attrs'] = attrs
        super().__init__(*args , **kwargs)


class CustomUserCreationForm (UserCreationForm):
    """Форма регистрации пользователя"""
    first_name = forms.CharField(max_length=30 , required=True , label="Имя")
    last_name = forms.CharField(max_length=30 , required=True , label="Фамилия")
    email = forms.EmailField(required=True , label="Email")
    phone = forms.CharField(max_length=20 , required=True , label="Телефон")
    birth_date = forms.DateField(required=True , label="Дата рождения" , widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'email' , 'phone' , 'birth_date' , 'password1' ,
                  'password2']


class AppointmentForm(forms.ModelForm):
    """Форма записи на прием"""

    class Meta:
        model = Appointment
        fields = ['doctor' , 'patient_problem' , 'service' , 'appointment_date' , 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3}) , }

    def __init__(self , *args , **kwargs):
        super().__init__(*args , **kwargs)
        self.fields['doctor'].queryset = self.fields['doctor'].queryset.filter(is_active=True)
        self.fields['patient_problem'].queryset = PatientProblem.objects.none()
        self.fields['patient_problem'].required = True
        self.fields['patient_problem'].label = 'Проблема обращения'
        self.fields['patient_problem'].help_text = 'Выберите врача, затем укажите проблему, с которой обращаетесь.'
        self.fields['service'].queryset = Service.objects.none()
        self.fields['service'].required = True
        self.fields['service'].help_text = 'После выбора врача доступны его услуги.'

        appointment_widget = forms.SplitDateTimeWidget(
            date_attrs={} ,
            time_attrs={'class': 'form-control' , 'placeholder': '15:00' ,
                        'pattern': '([01]?[0-9]|2[0-3]):[0-5][0-9]' , 'inputmode': 'numeric'} ,
        )
        appointment_widget.widgets[0] = DateDMYInput(
            attrs=appointment_widget.widgets[0].attrs ,
            format='%d/%m/%Y' ,
        )
        appointment_widget.widgets[1] = Time24Input(
            attrs=appointment_widget.widgets[1].attrs ,
            format='%H:%M' ,
        )

        appointment_field = self.fields.pop('appointment_date')
        self.fields['appointment_date'] = forms.SplitDateTimeField(
            label=appointment_field.label ,
            required=appointment_field.required ,
            help_text='Дату указывайте в формате ДД/ММ/ГГГГ, время — в 24-часовом формате, например 31/05/2026 15:00.' ,
            widget=appointment_widget ,
            input_date_formats=['%d/%m/%Y' , '%d.%m.%Y'] ,
            input_time_formats=['%H:%M' , '%H:%M:%S'] ,
        )

        if self.instance.pk and self.instance.appointment_date:
            local_dt = timezone.localtime(self.instance.appointment_date)
            self.fields['appointment_date'].initial = local_dt.replace(tzinfo=None)

        self.order_fields(['doctor' , 'patient_problem' , 'service' , 'appointment_date' , 'notes'])
        self._configure_doctor_dependent_fields()

    def _get_selected_doctor(self):
        doctor_id = self.data.get('doctor') or self.initial.get('doctor')
        if not doctor_id and self.instance.pk and self.instance.doctor_id:
            return self.instance.doctor
        if not doctor_id:
            return None
        if isinstance(doctor_id , Doctor):
            return doctor_id
        return Doctor.objects.filter(pk=doctor_id , is_active=True).first()

    def _configure_doctor_dependent_fields(self):
        doctor = self._get_selected_doctor()
        if not doctor:
            return

        problems = PatientProblem.objects.filter(doctor=doctor , is_active=True)
        self.fields['patient_problem'].queryset = problems
        self.fields['service'].queryset = doctor.services.filter(is_active=True)

        if self.instance.pk and self.instance.patient_problem_id:
            self.fields['patient_problem'].initial = self.instance.patient_problem_id

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        patient_problem = cleaned_data.get('patient_problem')
        service = cleaned_data.get('service')

        if doctor and patient_problem and patient_problem.doctor_id != doctor.pk:
            self.add_error('patient_problem' , 'Выберите проблему выбранного врача.')

        if doctor and service and not doctor.services.filter(pk=service.pk).exists():
            self.add_error('service' , 'Выберите услугу выбранного врача.')

        return cleaned_data

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']
        if timezone.is_naive(appointment_date):
            appointment_date = timezone.make_aware(
                appointment_date ,
                timezone.get_current_timezone() ,
            )

        if not self.instance.pk and appointment_date <= timezone.localtime():
            raise forms.ValidationError('Выберите дату и время в будущем.')

        return appointment_date


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи"""

    class Meta:
        model = Feedback
        fields = ['name' , 'phone' , 'email' , 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4 , 'placeholder': 'Ваше сообщение...'}) , }


class DoctorAdminForm(forms.ModelForm):
    full_name = forms.CharField(
        label='ФИО' ,
        max_length=255 ,
        help_text='Фамилия, имя и отчество через пробел.' ,
    )

    class Meta:
        model = Doctor
        exclude = ['user']

    def __init__(self , *args , **kwargs):
        super().__init__(*args , **kwargs)
        if self.instance.pk and self.instance.user_id:
            self.fields['full_name'].initial = self.instance.user.get_full_name().strip()

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name'].strip()
        if not full_name:
            raise forms.ValidationError('Укажите ФИО врача.')
        return full_name

    def save(self , commit=True):
        doctor = super().save(commit=False)
        full_name = self.cleaned_data['full_name']
        last_name , first_name = self._split_full_name(full_name)

        if doctor.user_id:
            user = doctor.user
        else:
            user = User(
                username=self._unique_username(full_name) ,
                is_staff=False ,
                is_active=True ,
            )
            user.set_unusable_password()

        user.last_name = last_name
        user.first_name = first_name
        user.save()
        doctor.user = user

        if commit:
            doctor.save()
            self.save_m2m()
        return doctor

    @staticmethod
    def _split_full_name(full_name):
        parts = full_name.split()
        if not parts:
            return '' , ''
        last_name = parts[0]
        first_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        return last_name , first_name

    @staticmethod
    def _unique_username(full_name):
        base = slugify(full_name , allow_unicode=True) or 'doctor'
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}-{counter}'
            counter += 1
        return username
