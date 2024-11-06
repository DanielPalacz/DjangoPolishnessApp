from __future__ import annotations

import json

import requests
from django.core.mail import send_mail
from requests.exceptions import ConnectTimeout
from requests.exceptions import ReadTimeout

from helpers import configure_logger
from mysite.celery_setup import app

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


@app.task
def get_krs_foundation_data(krs_number: str):
    krs_api_request = f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs_number}?rejestr=S&format=json"
    try:
        response = requests.get(krs_api_request, timeout=5)
    except (ReadTimeout, ConnectTimeout):
        return None

    if response.status_code != 200:
        return None

    try:
        foundation_name = response.json()["odpis"]["dane"]["dzial1"]["danePodmiotu"]["nazwa"]
        supervision = response.json()["odpis"]["dane"]["dzial1"]["organSprawujacyNadzor"]["nazwa"].replace("\n", ";")
        target = response.json()["odpis"]["dane"]["dzial3"]["celDzialaniaOrganizacji"]["celDzialania"].capitalize()
    except KeyError:
        return None
    except json.decoder.JSONDecodeError:
        return None

    try:
        email = response.json()["odpis"]["dane"]["dzial1"]["siedzibaIAdres"]["adresPocztyElektronicznej"].lower()
    except KeyError:
        email = "brak"
    except json.decoder.JSONDecodeError:
        email = "-"

    return [foundation_name, str(krs_number), supervision, target, repr(email)]
