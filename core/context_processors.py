from .models import ContactInfo

def contact_info(request):
    """Добавляет контактную информацию в контекст всех шаблонов"""
    return {
        'contact_info': ContactInfo.objects.filter(is_active=True),
    }