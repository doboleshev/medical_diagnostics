from django.db import migrations, models
from django.utils.text import slugify


def populate_doctor_slugs(apps, schema_editor):
    Doctor = apps.get_model('core', 'Doctor')
    for doctor in Doctor.objects.select_related('user').all():
        if doctor.slug:
            continue
        user = doctor.user
        full_name = f'{user.first_name} {user.last_name}'.strip()
        source = full_name or user.username
        slug = slugify(source, allow_unicode=True) or slugify(doctor.user.username)
        original = slug
        counter = 1
        while Doctor.objects.filter(slug=slug).exclude(pk=doctor.pk).exists():
            slug = f'{original}-{counter}'
            counter += 1
        doctor.slug = slug
        doctor.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=200,
                verbose_name='Адрес страницы',
            ),
        ),
        migrations.RunPython(populate_doctor_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='doctor',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=200,
                unique=True,
                verbose_name='Адрес страницы',
            ),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='specialization',
            field=models.CharField(
                choices=[
                    ('chief_physician', 'Главный врач'),
                    ('allergist_immunologist', 'Врач аллерголог-иммунолог'),
                    ('therapist', 'Врач-терапевт'),
                    ('surgeon', 'Врач-хирург'),
                    ('gynecologist', 'Врач-акушер-гинеколог'),
                    ('ophthalmologist', 'Врач-офтальмолог'),
                    ('pediatrician', 'Врач-педиатр'),
                    ('ultrasound', 'Врач ультразвуковой диагностики'),
                    ('otorhinolaryngologist', 'Врач оториноларинголог'),
                ],
                max_length=100,
                verbose_name='Специализация',
            ),
        ),
    ]
