from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Doctor


class Command(BaseCommand):
    help = 'Создает шаблоны врачей для заполнения через админ-панель'

    DOCTORS = [
        ('chief_physician' , 'Главный врач' , 1) ,
        ('allergist_immunologist' , 'Аллерголог-иммунолог' , 2) ,
        ('therapist' , 'Терапевт' , 3) ,
        ('surgeon' , 'Хирург' , 4) ,
        ('gynecologist' , 'Акушер-гинеколог' , 5) ,
        ('ophthalmologist' , 'Офтальмолог' , 6) ,
        ('pediatrician' , 'Педиатр' , 7) ,
        ('ultrasound' , 'УЗ-диагност' , 8) ,
        ('otorhinolaryngologist' , 'Оториноларинголог' , 9) ,
    ]

    @transaction.atomic
    def handle(self , *args , **options):
        created_count = 0
        existing_count = 0

        for specialization , title , order in self.DOCTORS:
            username = f'doctor_{specialization}'
            user , user_created = User.objects.get_or_create(
                username=username ,
                defaults={
                    'first_name': title ,
                    'last_name': 'Новый врач' ,
                    'email': f'{username}@opora.local' ,
                    'is_staff': False ,
                    'is_active': True ,
                } ,
            )

            if user_created:
                user.set_unusable_password()
                user.save(update_fields=['password'])

            doctor_defaults = {
                'specialization': specialization ,
                'bio': f'<p>Заполните информацию о враче ({title}) в админ-панели.</p>' ,
                'experience': 0 ,
                'education': 'Укажите образование и квалификацию в админ-панели.' ,
                'is_active': True ,
                'order': order ,
            }

            doctor , doctor_created = Doctor.objects.get_or_create(
                user=user ,
                defaults=doctor_defaults ,
            )

            if not doctor.slug:
                doctor.save()

            if doctor_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'OK Создан врач: {title}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(f'! Врач уже существует: {title}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nOK Инициализация врачей завершена. Создано: {created_count}, уже было: {existing_count}.'
            )
        )
