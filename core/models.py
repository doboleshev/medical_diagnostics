from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
import os


class Service(models.Model):
    """Модель медицинских услуг"""
    name = models.CharField(max_length=200 , verbose_name="Название услуги")
    slug = models.SlugField(max_length=200 , unique=True)
    description = RichTextField(verbose_name="Описание услуги")
    detailed_description = RichTextField(verbose_name="Подробное описание" , blank=True)
    price = models.DecimalField(max_digits=10 , decimal_places=2 , verbose_name="Цена")
    duration = models.IntegerField(verbose_name="Длительность (мин)")
    icon = models.CharField(max_length=100 , default="bi-heart-pulse" , verbose_name="Иконка Bootstrap")
    image = models.ImageField(upload_to='services/' , null=True , blank=True)
    is_active = models.BooleanField(default=True , verbose_name="Активна")
    order = models.IntegerField(default=0 , verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['order' , 'name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    """Модель врачей"""
    SPECIALIZATION_CHOICES = [('diagnostic' , 'Врач-диагност') , ('radiologist' , 'Радиолог') ,
                              ('cardiologist' , 'Кардиолог') , ('neurologist' , 'Невролог') ,
                              ('therapist' , 'Терапевт') ,]

    user = models.OneToOneField(User , on_delete=models.CASCADE , related_name='doctor')
    specialization = models.CharField(max_length=100 , choices=SPECIALIZATION_CHOICES , verbose_name="Специализация")
    bio = RichTextField(verbose_name="Биография")
    experience = models.IntegerField(verbose_name="Стаж (лет)")
    education = models.TextField(verbose_name="Образование")
    photo = models.ImageField(upload_to='doctors/' , null=True , blank=True)
    services = models.ManyToManyField(Service , related_name='doctors' , verbose_name="Услуги")
    is_active = models.BooleanField(default=True , verbose_name="Работает в компании")
    order = models.IntegerField(default=0 , verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ['order' , 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"


class Appointment (models.Model):
    """Модель записи на прием"""
    STATUS_CHOICES = [('pending' , 'Ожидает подтверждения') , ('confirmed' , 'Подтверждена') ,
                      ('completed' , 'Завершена') , ('cancelled' , 'Отменена') ,]

    patient = models.ForeignKey(User , on_delete=models.CASCADE , related_name='appointments' , verbose_name="Пациент")
    doctor = models.ForeignKey(Doctor , on_delete=models.CASCADE , related_name='appointments' , verbose_name="Врач")
    service = models.ForeignKey(Service , on_delete=models.CASCADE , related_name='appointments' ,
                                verbose_name="Услуга")
    appointment_date = models.DateTimeField(verbose_name="Дата и время приема")
    status = models.CharField(max_length=20 , choices=STATUS_CHOICES , default='pending' , verbose_name="Статус")
    notes = models.TextField(blank=True , verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"
        ordering = ['-appointment_date']

    def __str__(self):
        return (f"{self.patient.get_full_name()} - {self.service.name} - "
                f"{self.appointment_date.strftime('%d.%m.%Y %H:%M')}")


class TestResult (models.Model):
    """Модель результатов диагностики"""
    appointment = models.OneToOneField(Appointment , on_delete=models.CASCADE , related_name='test_result')
    doctor = models.ForeignKey(Doctor , on_delete=models.CASCADE , related_name='test_results' , verbose_name="Врач")
    findings = RichTextField(verbose_name="Результаты обследования")
    recommendations = RichTextField(verbose_name="Рекомендации")
    pdf_file = models.FileField(upload_to='results/' , null=True , blank=True , verbose_name="PDF-отчет")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Результат диагностики"
        verbose_name_plural = "Результаты диагностики"

    def __str__(self):
        return f"Результат: {self.appointment.patient.get_full_name()} - {self.appointment.service.name}"


class ContactInfo (models.Model):
    """Модель контактной информации"""
    company_name = models.CharField(max_length=200 , verbose_name="Название компании")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20 , verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    working_hours = models.TextField(verbose_name="Режим работы")
    map_embed_code = models.TextField(blank=True , verbose_name="Код карты (iframe)")
    is_active = models.BooleanField(default=True , verbose_name="Активные контакты")

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self):
        return self.company_name


class Feedback (models.Model):
    """Модель обратной связи"""
    name = models.CharField(max_length=100 , verbose_name="Имя")
    phone = models.CharField(max_length=20 , verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False , verbose_name="Обработано")

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y')}"


class PageContent(models.Model):
    """Модель для управления контентом страниц"""
    PAGE_CHOICES = [('home' , 'Главная страница') , ('about' , 'О компании') , ('services' , 'Услуги') ,
                    ('contacts' , 'Контакты') ,]

    page = models.CharField(max_length=20 , choices=PAGE_CHOICES , unique=True , verbose_name="Страница")
    title = models.CharField(max_length=200 , verbose_name="Заголовок")
    content = RichTextField(verbose_name="Содержание")
    meta_description = models.TextField(blank=True , verbose_name="Meta описание")
    meta_keywords = models.TextField(blank=True , verbose_name="Meta ключевые слова")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Контент страницы"
        verbose_name_plural = "Контент страниц"

    def __str__(self):
        return self.get_page_display()
