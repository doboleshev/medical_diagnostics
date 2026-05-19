from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .forms import DoctorAdminForm
from .models import (
    Appointment,
    ContactInfo,
    Doctor,
    Equipment,
    Feedback,
    PageContent,
    PatientProblem,
    PatientProfile,
    Service,
    TestResult,
)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'order', 'is_active']


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'summary', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']


class PatientProblemInline(admin.TabularInline):
    model = PatientProblem
    extra = 1
    fields = ('title', 'order', 'is_active')


class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm
    inlines = [PatientProblemInline]
    list_display = ['get_full_name', 'slug', 'specialization', 'experience',
                    'is_active', 'order']
    list_filter = ['specialization', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'specialization', 'slug']
    list_editable = ['order', 'is_active']
    filter_horizontal = ['services']
    readonly_fields = ['slug']
    fieldsets = (
        ('Основное', {
            'fields': (
                'full_name', 'specialization', 'experience',
                'is_active', 'order', 'slug',
            ),
        }),
        ('О враче', {
            'fields': ('education', 'patient_problems', 'bio', 'photo'),
        }),
        ('Услуги и проблемы', {
            'fields': ('services',),
            'description': 'Ниже добавьте проблемы, с которыми работает врач. Они будут доступны при записи на прием.',
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'ФИО'


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'patient_problem', 'service', 'appointment_date',
                    'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__username', 'patient__email',
                     'doctor__user__first_name']
    date_hierarchy = 'appointment_date'
    list_editable = ['status']

    def patient(self, obj):
        return obj.patient.get_full_name()

    def doctor(self, obj):
        return obj.doctor.user.get_full_name()


class TestResultAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'doctor', 'created_at']
    search_fields = ['appointment__patient__username', 'findings']
    readonly_fields = ['created_at', 'updated_at']


class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'phone', 'email', 'is_active']
    list_editable = ['is_active']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at', 'is_processed']
    list_filter = ['is_processed', 'created_at']
    list_editable = ['is_processed']
    readonly_fields = ['created_at']


class PageContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'title', 'updated_at']
    readonly_fields = ['updated_at']


# Расширение стандартной админки пользователей
class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    extra = 0
    fields = ('phone', 'birth_date')


class CustomUserAdmin(UserAdmin):
    inlines = (*UserAdmin.inlines, PatientProfileInline)
    list_display = UserAdmin.list_display + ('date_joined', 'last_login')
    list_filter = UserAdmin.list_filter + ('is_staff', 'is_superuser')


# Регистрация моделей
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(TestResult, TestResultAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(PageContent, PageContentAdmin)

# Настройка админки
admin.site.site_header = 'Администрирование «Опора»'
admin.site.site_title = 'Опора'
admin.site.index_title = "Панель управления"
