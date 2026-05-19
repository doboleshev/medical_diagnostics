from django.contrib.auth.models import User

from core.models import PatientProfile


def create_patient_user(username, password, email, first_name, last_name, phone, birth_date):
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    PatientProfile.objects.create(
        user=user,
        phone=phone,
        birth_date=birth_date,
    )
    return user
