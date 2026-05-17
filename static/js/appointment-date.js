function formatAppointmentDate(value) {
    const digits = value.replace(/\D/g, '').slice(0, 8);

    if (digits.length <= 2) {
        return digits;
    }

    if (digits.length <= 4) {
        return `${digits.slice(0, 2)}/${digits.slice(2)}`;
    }

    return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.querySelector('#id_appointment_date_0');
    if (!dateInput) {
        return;
    }

    const timeInput = document.querySelector('#id_appointment_date_1');

    dateInput.addEventListener('input', function () {
        const cursorPosition = dateInput.selectionStart;
        const previousLength = dateInput.value.length;
        dateInput.value = formatAppointmentDate(dateInput.value);

        if (dateInput.value.length > previousLength && dateInput.value[cursorPosition - 1] === '/') {
            dateInput.setSelectionRange(cursorPosition + 1, cursorPosition + 1);
        }

        if (dateInput.value.length === 10 && timeInput) {
            timeInput.focus();
        }
    });

    dateInput.addEventListener('paste', function (event) {
        const clipboard = event.clipboardData || window.clipboardData;
        if (!clipboard) {
            return;
        }

        event.preventDefault();
        dateInput.value = formatAppointmentDate(clipboard.getData('text'));
    });
});
