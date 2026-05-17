document.addEventListener('DOMContentLoaded', () => {
    const optionsNode = document.getElementById('doctor-appointment-options');
    const doctorSelect = document.getElementById('id_doctor');
    const problemSelect = document.getElementById('id_patient_problem');
    const serviceSelect = document.getElementById('id_service');

    if (!optionsNode || !doctorSelect || !problemSelect || !serviceSelect) {
        return;
    }

    const options = JSON.parse(optionsNode.textContent);
    const initialProblem = problemSelect.value;
    const initialService = serviceSelect.value;

    const fillSelect = (select, items, placeholder, getValue, getLabel) => {
        const currentValue = select.value;
        select.innerHTML = '';

        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        select.appendChild(placeholderOption);

        items.forEach((item) => {
            const option = document.createElement('option');
            option.value = String(getValue(item));
            option.textContent = getLabel(item);
            select.appendChild(option);
        });

        if (currentValue && [...select.options].some((option) => option.value === currentValue)) {
            select.value = currentValue;
        }
    };

    const refreshDependentFields = () => {
        const doctorId = doctorSelect.value;
        const doctorOptions = options[doctorId];

        if (!doctorOptions) {
            fillSelect(problemSelect, [], 'Сначала выберите врача', (item) => item.id, (item) => item.title);
            fillSelect(serviceSelect, [], 'Сначала выберите врача', (item) => item.id, (item) => item.name);
            return;
        }

        fillSelect(
            problemSelect,
            doctorOptions.problems,
            'Выберите проблему',
            (item) => item.id,
            (item) => item.title,
        );
        fillSelect(
            serviceSelect,
            doctorOptions.services,
            'Выберите услугу',
            (item) => item.id,
            (item) => item.name,
        );
    };

    doctorSelect.addEventListener('change', () => {
        problemSelect.value = '';
        serviceSelect.value = '';
        refreshDependentFields();
    });

    refreshDependentFields();

    if (initialProblem) {
        problemSelect.value = initialProblem;
    }
    if (initialService) {
        serviceSelect.value = initialService;
    }
});
