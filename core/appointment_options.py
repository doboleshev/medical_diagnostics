from .models import Doctor


def build_doctor_appointment_options():
    options = {}
    doctors = Doctor.objects.filter(is_active=True).prefetch_related(
        'patient_problem_items' ,
        'services' ,
    ).order_by('order' , 'user__last_name')

    for doctor in doctors:
        options[str(doctor.pk)] = {
            'problems': [
                {'id': problem.pk , 'title': problem.title}
                for problem in doctor.patient_problem_items.filter(is_active=True)
            ] ,
            'services': [
                {'id': service.pk , 'name': service.name}
                for service in doctor.services.filter(is_active=True)
            ] ,
        }

    return options
