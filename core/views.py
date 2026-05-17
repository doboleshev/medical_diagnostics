from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

from .appointment_options import build_doctor_appointment_options
from .models import (
    Service, Equipment, Doctor, PatientProblem, ContactInfo, PageContent,
    Appointment, TestResult, Feedback
)
from .forms import CustomUserCreationForm, AppointmentForm, FeedbackForm


def home(request):
    """Главная страница"""
    services = Service.objects.filter(is_active=True)[:6]
    doctors = Doctor.objects.filter(is_active=True)[:4]
    contact_info = ContactInfo.objects.filter(is_active=True)

    context = {
        'services': services,
        'doctors': doctors,
        'contact_info': contact_info,
    }
    return render(request, 'index.html', context)


class ServiceListView(ListView):
    """Список услуг"""
    model = Service
    template_name = 'services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_content'] = PageContent.objects.filter(
            page='services').first()
        return context


class ServiceDetailView(DetailView):
    """Детальная страница услуги"""
    model = Service
    template_name = 'service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class EquipmentListView(ListView):
    """Список оборудования"""
    model = Equipment
    template_name = 'equipment.html'
    context_object_name = 'equipment_items'

    def get_queryset(self):
        return Equipment.objects.filter(is_active=True).order_by('order', 'name')


class EquipmentDetailView(DetailView):
    """Страница оборудования"""
    model = Equipment
    template_name = 'equipment_detail.html'
    context_object_name = 'equipment'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Equipment.objects.filter(is_active=True)


class DoctorListView(ListView):
    """Список врачей"""
    model = Doctor
    template_name = 'doctors.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        return Doctor.objects.filter(is_active=True).select_related('user').order_by('order', 'user__last_name')


class DoctorDetailView(DetailView):
    """Страница врача"""
    model = Doctor
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('services')


def about(request):
    """Страница о компании"""
    doctors = Doctor.objects.filter(is_active=True)
    page_content = PageContent.objects.filter(page='about').first()

    context = {
        'doctors': doctors,
        'page_content': page_content,
    }
    return render(request, 'about.html', context)


def contact(request):
    """Страница контактов"""
    contact_info = ContactInfo.objects.filter(is_active=True).first()
    page_content = PageContent.objects.filter(page='contacts').first()

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('contact')
    else:
        form = FeedbackForm()

    context = {
        'contact_info': contact_info,
        'page_content': page_content,
        'form': form,
    }
    return render(request, 'contact.html', context)


class UserRegisterView(CreateView):
    """Регистрация пользователя"""
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно!')
        return response


@login_required
def profile(request):
    """Личный кабинет пользователя"""
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related(
        'doctor__user' ,
        'service' ,
        'patient_problem' ,
    ).order_by('-appointment_date')
    test_results = TestResult.objects.filter(
        appointment__patient=request.user).select_related('appointment')

    context = {
        'appointments': appointments,
        'test_results': test_results,
    }
    return render(request, 'registration/profile.html', context)


class AppointmentFormMixin:
    """Общий контекст для формы записи на прием"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctor_appointment_options'] = build_doctor_appointment_options()
        return context


class AppointmentCreateView(AppointmentFormMixin, LoginRequiredMixin, CreateView):
    """Создание записи на прием"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        form.instance.patient = self.request.user
        messages.success(
            self.request,
            'Запись на прием создана! Ожидайте подтверждения от администратора.'
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        initial = {'patient': self.request.user}
        doctor_id = self.request.GET.get('doctor')
        service_id = self.request.GET.get('service')
        problem_id = self.request.GET.get('problem')
        if doctor_id and Doctor.objects.filter(pk=doctor_id, is_active=True).exists():
            initial['doctor'] = doctor_id
        if service_id and Service.objects.filter(pk=service_id, is_active=True).exists():
            initial['service'] = service_id
        if problem_id and PatientProblem.objects.filter(pk=problem_id, is_active=True).exists():
            initial['patient_problem'] = problem_id
        kwargs['initial'] = initial
        return kwargs


class AppointmentUpdateView(AppointmentFormMixin, LoginRequiredMixin, UpdateView):
    """Редактирование записи на прием"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointment_form.html'
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Запись на прием обновлена!')
        return super().form_valid(form)


@login_required
def appointment_cancel(request, pk):
    """Отмена записи на прием"""
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Запись на прием отменена.')
        return redirect('profile')
    return render(
        request,
        'appointment_confirm_cancel.html',
        {'appointment': appointment}
    )


@login_required
def test_result_detail(request, pk):
    """Просмотр результатов диагностики"""
    test_result = get_object_or_404(
        TestResult, pk=pk, appointment__patient=request.user
    )
    return render(request, 'test_result_detail.html', {'test_result': test_result})
