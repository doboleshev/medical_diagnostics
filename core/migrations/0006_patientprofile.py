from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_appointment_patient_problem'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='patient_profile',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Пользователь',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Профиль пациента',
                'verbose_name_plural': 'Профили пациентов',
            },
        ),
    ]
