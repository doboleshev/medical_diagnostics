from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import (
    Appointment,
    Doctor,
    PatientProblem,
    PatientProfile,
    Service,
    TestResult,
)


class MedicalSiteTestMixin:
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            name='Консультация',
            slug='konsultaciya',
            description='Описание',
            price=1000,
            duration=30,
        )
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='pass12345',
            first_name='Иван',
            last_name='Иванов',
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='therapist',
            bio='Биография',
            experience=5,
            education='МГУ',
            is_active=True,
        )
        self.doctor.services.add(self.service)
        self.problem = PatientProblem.objects.create(
            doctor=self.doctor,
            title='Головная боль',
            is_active=True,
        )
        future = timezone.localtime() + timedelta(days=2)
        self.appointment_date = future.replace(minute=0, second=0, microsecond=0)

    def create_patient(self, username='patient1', password='pass12345'):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f'{username}@example.com',
            first_name='Петр',
            last_name='Петров',
        )
        PatientProfile.objects.create(
            user=user,
            phone='+79990001122',
            birth_date=date(1990, 1, 15),
        )
        return user


class RegistrationTests(MedicalSiteTestMixin, TestCase):
    def test_registration_creates_patient_profile(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newpatient',
                'first_name': 'Анна',
                'last_name': 'Смирнова',
                'email': 'anna@example.com',
                'phone': '+79991112233',
                'birth_date': '1995-05-20',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newpatient')
        profile = PatientProfile.objects.get(user=user)
        self.assertEqual(profile.phone, '+79991112233')
        self.assertEqual(str(profile.birth_date), '1995-05-20')


class AppointmentTests(MedicalSiteTestMixin, TestCase):
    def test_create_appointment(self):
        patient = self.create_patient()
        self.client.login(username='patient1', password='pass12345')

        response = self.client.post(
            reverse('appointment_create'),
            {
                'doctor': self.doctor.pk,
                'patient_problem': self.problem.pk,
                'service': self.service.pk,
                'appointment_date_0': self.appointment_date.strftime('%d/%m/%Y'),
                'appointment_date_1': self.appointment_date.strftime('%H:%M'),
                'notes': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Appointment.objects.filter(patient=patient, doctor=self.doctor).exists(),
        )

    def test_doctor_schedule_conflict(self):
        patient = self.create_patient()
        other_patient = self.create_patient(username='patient2')
        Appointment.objects.create(
            patient=other_patient,
            doctor=self.doctor,
            patient_problem=self.problem,
            service=self.service,
            appointment_date=self.appointment_date,
            status='confirmed',
        )

        self.client.login(username='patient1', password='pass12345')
        response = self.client.post(
            reverse('appointment_create'),
            {
                'doctor': self.doctor.pk,
                'patient_problem': self.problem.pk,
                'service': self.service.pk,
                'appointment_date_0': self.appointment_date.strftime('%d/%m/%Y'),
                'appointment_date_1': self.appointment_date.strftime('%H:%M'),
                'notes': '',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Appointment.objects.filter(patient=patient, appointment_date=self.appointment_date).exists(),
        )

    def test_cannot_access_other_patient_appointment_edit(self):
        owner = self.create_patient()
        intruder = self.create_patient(username='intruder')
        appointment = Appointment.objects.create(
            patient=owner,
            doctor=self.doctor,
            patient_problem=self.problem,
            service=self.service,
            appointment_date=self.appointment_date,
        )

        self.client.login(username='intruder', password='pass12345')
        response = self.client.get(reverse('appointment_edit', kwargs={'pk': appointment.pk}))
        self.assertEqual(response.status_code, 404)

    def test_cannot_edit_completed_appointment(self):
        patient = self.create_patient()
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            patient_problem=self.problem,
            service=self.service,
            appointment_date=self.appointment_date,
            status='completed',
        )

        self.client.login(username='patient1', password='pass12345')
        response = self.client.get(reverse('appointment_edit', kwargs={'pk': appointment.pk}))
        self.assertRedirects(response, reverse('profile'))


class TestResultAccessTests(MedicalSiteTestMixin, TestCase):
    def test_patient_can_view_own_test_result(self):
        patient = self.create_patient()
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            patient_problem=self.problem,
            service=self.service,
            appointment_date=self.appointment_date,
            status='completed',
        )
        test_result = TestResult.objects.create(
            appointment=appointment,
            doctor=self.doctor,
            findings='Норма',
            recommendations='Контроль через год',
        )

        self.client.login(username='patient1', password='pass12345')
        response = self.client.get(reverse('test_result_detail', kwargs={'pk': test_result.pk}))
        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_view_other_test_result(self):
        owner = self.create_patient()
        intruder = self.create_patient(username='intruder')
        appointment = Appointment.objects.create(
            patient=owner,
            doctor=self.doctor,
            patient_problem=self.problem,
            service=self.service,
            appointment_date=self.appointment_date,
            status='completed',
        )
        test_result = TestResult.objects.create(
            appointment=appointment,
            doctor=self.doctor,
            findings='Норма',
            recommendations='Контроль через год',
        )

        self.client.login(username='intruder', password='pass12345')
        response = self.client.get(reverse('test_result_detail', kwargs={'pk': test_result.pk}))
        self.assertEqual(response.status_code, 404)
