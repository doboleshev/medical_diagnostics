from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    ServiceListView,
    ServiceDetailView,
    UserRegisterView,
    AppointmentCreateView,
    AppointmentUpdateView
)


urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', ServiceListView.as_view(), name='services'),
    path('services/<slug:slug>/', ServiceDetailView.as_view(),
         name='service_detail'),
    path('contact/', views.contact, name='contact'),

    # Авторизация
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'),
         name='logout'),

    # Личный кабинет
    path('profile/', views.profile, name='profile'),
    path('appointment/create/', AppointmentCreateView.as_view(),
         name='appointment_create'),
    path('appointment/<int:pk>/edit/', AppointmentUpdateView.as_view(),
         name='appointment_edit'),
    path('appointment/<int:pk>/cancel/', views.appointment_cancel,
         name='appointment_cancel'),
    path('test-result/<int:pk>/', views.test_result_detail,
         name='test_result_detail'),

    # Обратная связь
    path('feedback/', views.contact, name='feedback_create'),
]
