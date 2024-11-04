from __future__ import annotations

import requests
from django.core.mail import send_mail

from .celery_setup import app
from helpers import configure_logger


LOGGER_WEBSITE_AVAILABILITY = configure_logger("check_website_availability")


@app.task
def check_website_availability():
    response = requests.get("https://poznajmypolske.pl", timeout=60)
    if response.status_code == 200:
        LOGGER_WEBSITE_AVAILABILITY.info("Test dostępności strony przeszedł pomyślnie.")

    else:
        subject_text = "[https://poznajmypolske.pl][Test dostępności strony] - wykryto błąd."
        message_text = (
            f"Sprawdź co się dzieje. Test dostępności strony wykrył błąd. "
            f"Zwrócony status odpowiedzi: '{response.status_code}'."
        )
        send_mail(
            subject=subject_text,
            message=message_text,
            from_email="daniel.palacz@pyx.solutions",
            recipient_list=["daniel.palacz@pyx.solutions", "daniel.palacz@gmail.com"],
            fail_silently=False,  # Raise exception if the email fails to send
        )
        LOGGER_WEBSITE_AVAILABILITY.error(message_text)
