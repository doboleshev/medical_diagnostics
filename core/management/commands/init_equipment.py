from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Equipment


class Command(BaseCommand):
    help = 'Создает карточки оборудования для раздела сайта'

    EQUIPMENT = [
        (
            'canon-aplio-500' ,
            'Canon Aplio 500' ,
            'УЗИ-аппарат экспертного класса с высокой диагностической точностью для кардиологии, акушерства, гинекологии, урологии и других направлений.' ,
            '<p>Canon Aplio 500 — экспертная система премиум-класса, сочетающая высокую диагностическую точность и расширенные функциональные возможности.</p><p>Аппарат помогает получать детализированные изображения мягких тканей, оценивать кровоток и проводить комплексные обследования в разных клинических сценариях.</p>' ,
            'canon-aplio-500.jpg' ,
            1 ,
        ) ,
        (
            'voluson-e8-expert' ,
            'Voluson E8 Expert' ,
            'Ультразвуковая система нового поколения для акушерства и гинекологии с качественным 4D-изображением.' ,
            '<p>Voluson E8 Expert — ультразвуковой аппарат экспертного класса для акушерско-гинекологической диагностики.</p><p>Высококачественное 4D-изображение помогает выявлять патологии на ранних стадиях и повышает информативность гинекологического обследования.</p>' ,
            'voluson-e8-expert.jpg' ,
            2 ,
        ) ,
        (
            'fotofinder' ,
            'FotoFinder — цифровая дерматоскопия' ,
            'Передовая цифровая дерматоскопия для точной диагностики новообразований кожи и контроля динамики изменений.' ,
            '<p>FotoFinder — одно из самых востребованных решений в цифровой дерматоскопии.</p><p>Система помогает врачу детально анализировать кожные образования, фиксировать результаты исследования и своевременно выявлять подозрительные изменения.</p>' ,
            'fotofinder.jpg' ,
            3 ,
        ) ,
        (
            'olympus-evis-exera-iii' ,
            'Olympus EVIS EXERA III' ,
            'Универсальная платформа экспертного класса для диагностической эндоскопии и эндохирургии.' ,
            '<p>Olympus EVIS EXERA III — современная эндоскопическая система для исследования пищевода, желудка, двенадцатиперстной и толстой кишки.</p><p>Платформа поддерживает скрининговые исследования, включая колоноскопию для ранней диагностики заболеваний желудочно-кишечного тракта.</p>' ,
            'olympus-evis-exera-iii.jpg' ,
            4 ,
        ) ,
        (
            'video-frenzel' ,
            'Видеофрензель' ,
            'Диагностический комплекс для обследования вестибулярных нарушений и уточнения причин головокружения.' ,
            '<p>Видеофрензель позволяет фиксировать малейшие непроизвольные движения глаз, которые сложно заметить при обычном осмотре.</p><p>Метод помогает точнее оценить состояние вестибулярного аппарата и подобрать дальнейшую тактику обследования и лечения.</p>' ,
            'video-frenzel.jpg' ,
            5 ,
        ) ,
        (
            'hil-btl-6000' ,
            'HIL BTL 6000' ,
            'Высокоинтенсивная лазерная терапия нового поколения для физиотерапии и восстановительного лечения.' ,
            '<p>HIL BTL 6000 — технология высокоинтенсивной лазерной терапии, применяемая в физиотерапии и реабилитации.</p><p>Метод используют для обезболивания, ускорения восстановления тканей и поддержки лечения заболеваний опорно-двигательного аппарата.</p>' ,
            'hil-btl-6000.jpg' ,
            6 ,
        ) ,
    ]

    @transaction.atomic
    def handle(self , *args , **options):
        photos_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'equipment'
        created_count = 0
        updated_count = 0

        for slug , name , summary , description , image_name , order in self.EQUIPMENT:
            equipment , created = Equipment.objects.get_or_create(
                slug=slug ,
                defaults={
                    'name': name ,
                    'summary': summary ,
                    'description': description ,
                    'order': order ,
                    'is_active': True ,
                } ,
            )

            if not created:
                equipment.name = name
                equipment.summary = summary
                equipment.description = description
                equipment.order = order
                equipment.is_active = True
                equipment.save()
                updated_count += 1
            else:
                created_count += 1

            photo_path = photos_dir / image_name
            if photo_path.exists():
                with photo_path.open('rb') as photo_file:
                    equipment.image.save(image_name , File(photo_file) , save=True)
                self.stdout.write(self.style.SUCCESS(f'OK {name}'))
            else:
                self.stdout.write(
                    self.style.WARNING(f'! Нет файла {image_name} для {name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nOK Инициализация оборудования завершена. Создано: {created_count}, обновлено: {updated_count}.'
            )
        )
