from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from .models import Appointment , Feedback


class CustomUserCreationForm (UserCreationForm):
    """Форма регистрации пользователя"""
    first_name = forms.CharField(max_length=30 , required=True , label="Имя")
    last_name = forms.CharField(max_length=30 , required=True , label="Фамилия")
    email = forms.EmailField(required=True , label="Email")

    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'email' , 'password1' ,
                  'password2']


class AppointmentForm(forms.ModelForm):
    """Форма записи на прием"""
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Дата и время приема'
    )

    class Meta:
        model = Appointment
        fields = ['doctor' , 'service' , 'appointment_date' , 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }

    def __init__(self , *args , **kwargs):
        super().__init__(*args , **kwargs)
        self.fields['doctor'].queryset = self.fields['doctor'].queryset.filter(is_active=True)
        self.fields['service'].queryset = self.fields['service'].queryset.filter(is_active=True)
        
        # Устанавливаем минимальную дату (сегодня, следующий час) для поля appointment_date
        now = timezone.now()
        # Округляем до следующего часа
        min_datetime = now.replace(minute=0, second=0, microsecond=0)
        # Если есть минуты или секунды, добавляем час
        if now.minute > 0 or now.second > 0:
            from datetime import timedelta
            min_datetime = min_datetime + timedelta(hours=1)
        min_datetime_str = min_datetime.strftime('%Y-%m-%dT%H:%M')
        self.fields['appointment_date'].widget.attrs['min'] = min_datetime_str
        
        # Добавляем классы Bootstrap к полям формы
        for field_name, field in self.fields.items():
            if field_name != 'appointment_date':  # appointment_date уже настроен
                if not field.widget.attrs.get('class'):
                    field.widget.attrs['class'] = 'form-control'
                elif 'form-control' not in field.widget.attrs.get('class', ''):
                    field.widget.attrs['class'] += ' form-control'


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи"""

    class Meta:
        model = Feedback
        fields = ['name' , 'phone' , 'email' , 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4 , 'placeholder': 'Ваше сообщение...'}) , }
