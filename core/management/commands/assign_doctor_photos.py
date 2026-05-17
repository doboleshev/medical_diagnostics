from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import Doctor


class Command(BaseCommand):
    help = 'Привязывает индивидуальные фото врачей из static/images/doctors/'

    def add_arguments(self , parser):
        parser.add_argument(
            '--force' ,
            action='store_true' ,
            help='Заменить уже привязанные фото' ,
        )

    def handle(self , *args , **options):
        photos_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'doctors'
        assigned = 0
        missing = 0

        for doctor in Doctor.objects.select_related('user').order_by('order'):
            photo_path = photos_dir / f'{doctor.slug}.jpg'
            if not photo_path.exists():
                missing += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'! Нет файла для {doctor.user.get_full_name()}: {photo_path.name}'
                    )
                )
                continue

            if doctor.photo and not options['force']:
                self.stdout.write(
                    self.style.WARNING(f'! Пропущен {doctor.user.get_full_name()} (уже есть фото)')
                )
                continue

            if doctor.photo:
                doctor.photo.delete(save=False)

            with photo_path.open('rb') as photo_file:
                doctor.photo.save(photo_path.name , File(photo_file) , save=True)

            assigned += 1
            self.stdout.write(self.style.SUCCESS(f'OK {doctor.user.get_full_name()}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nOK Привязано фото: {assigned}. Без файла: {missing}.'
            )
        )
