from django.core.exceptions import ValidationError

from core.models import Appointment

NON_EDITABLE_STATUSES = frozenset({'completed', 'cancelled'})


def appointment_is_editable(appointment):
    return appointment.status not in NON_EDITABLE_STATUSES


def ensure_appointment_editable(appointment):
    if not appointment_is_editable(appointment):
        raise ValidationError(
            'Редактирование недоступно для завершённых и отменённых записей.',
            code='not_editable',
        )


def ensure_appointment_cancellable(appointment):
    if not appointment_is_editable(appointment):
        raise ValidationError(
            'Отмена недоступна для завершённых и отменённых записей.',
            code='not_cancellable',
        )


def validate_doctor_problem_service(doctor, patient_problem, service):
    if doctor and patient_problem and patient_problem.doctor_id != doctor.pk:
        raise ValidationError(
            {'patient_problem': 'Выберите проблему выбранного врача.'},
        )

    if doctor and service and not doctor.services.filter(pk=service.pk).exists():
        raise ValidationError(
            {'service': 'Выберите услугу выбранного врача.'},
        )


def check_doctor_schedule_conflict(doctor, appointment_date, exclude_appointment_id=None):
    queryset = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=appointment_date,
    ).exclude(status='cancelled')

    if exclude_appointment_id:
        queryset = queryset.exclude(pk=exclude_appointment_id)

    if queryset.exists():
        raise ValidationError(
            'На это время у врача уже есть запись. Выберите другое время.',
            code='schedule_conflict',
        )
