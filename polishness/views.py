from datetime import datetime
from django.utils.text import slugify

from django.shortcuts import render, HttpResponseRedirect

from django.contrib import messages
from django.core.mail import send_mail

from tools import GusApiDbwClient, get_polish_photo_link, get_monument_query_params, randomize_monuments, \
    TripGenerator, ask_ai
from .forms import ContactForm
from .models import Monument


def home(request):
    photo_data = get_polish_photo_link()
    return render(request, "polishness/home.html", photo_data)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send the email
            send_mail(
                subject=f"[Formularz kontaktowy][poznajmypolske.pl] - wiadomość od: {name} [{email}].",  # Subject of the email
                message=message,  # Message content
                from_email='daniel.palacz@pyx.solutions',  # From email
                recipient_list=['daniel.palacz@pyx.solutions'],  # Recipient email list
                fail_silently=False,  # Raise exception if the email fails to send
            )
            messages.success(request, f"Cześć {name}, Twoja wiadomość została właśnie wysłana do mnie.")
            return HttpResponseRedirect("/contact/")
    else:
        form = ContactForm()
        return render(request, "polishness/contact.html", {"form": form})

def monuments(request):
    monument_items = None
    if request.method == 'POST':
        query_params = get_monument_query_params(request.POST)
        quantity = query_params.pop("quantity")
        monument_items_cleaned = Monument.objects.filter(**query_params)
        monument_items = randomize_monuments(quantity=int(quantity), monuments=monument_items_cleaned)

    return render(request, "polishness/monuments.html", {"monuments": monument_items})

def monument_single(request, pk):
    monument_item = Monument.objects.get(id=pk)
    return render(request, "polishness/monument_single.html", {"monument": monument_item})


def trips(request):
    monument_items = None
    if request.method == 'POST':
        query_params = get_monument_query_params(request.POST)
        quantity = query_params.pop("quantity")
        quantity = 10 if int(quantity) > 10 else int(quantity)
        monument_items_cleaned = Monument.objects.exclude(latitude="nan", longitude="nan").filter(**query_params)
        monument_items = randomize_monuments(quantity=int(quantity), monuments=monument_items_cleaned)

        trip_generator = TripGenerator(quantity=quantity, monuments=monument_items)
        monument_items = trip_generator.generate_trip()

    return render(request, "polishness/trips.html", {"monuments": monument_items})


def monument_single_ai(request, pk):
    monument_item = Monument.objects.get(id=pk)

    ask_text = f"Opowiedz mi o zabytku: {monument_item.name}, {monument_item.locality}"
    if monument_item.street and monument_item.street != "nan":
        ask_text += f", {monument_item.street}"

    if monument_item.address_number and monument_item.address_number != "nan":
        ask_text += f", {monument_item.address_number}"

    response_ai = ask_ai(ask=ask_text)

    return render(request,
                  "polishness/monument_single_ai.html",
                  {"monument": monument_item, "response_ai": response_ai})

def poland_in_numbers(request):
    """" Presents root fields (Podstawowe Dziedziny Wiedzy) from DBW GUS API. """
    root_fields = GusApiDbwClient.get_dbw_root_fields()
    return render(request, "polishness/poland_in_numbers.html", {"root_fields": root_fields})

def poland_in_numbers_fields(request, field_id, field_name):
    fields = GusApiDbwClient.get_dbw_fields(field_id=field_id, field_name=field_name)
    field_variables = GusApiDbwClient.get_dbw_field_variables(field_id=field_id, field_name=field_name)

    return render(request, "polishness/poland_in_numbers_fields.html",
                  {"fields": fields, "field_variables": field_variables})

def poland_in_numbers_field_browser(request, field_id, field_variable_id, field_variable_name):

    if request.method == 'POST':
        section_name, section_id, period_id, period_description = request.POST["przekroj__przekrojid__okresid"].split("__")
        year_id = request.POST["rok"]
        GusApiDbwClient.DBW_LOGGER.info(f"Dla następujących parametrów zostaną pobrane dane statystyczne. "
                                        f"Przekrój: {section_name} (przekroj_id={section_id}). "
                                        f"Zmienna: {field_variable_name} (zmienna_id={field_variable_id}). "
                                        f"Okres: {period_description} (okres_id={period_id}). "
                                        f"Rok: {year_id}.")
        stats_data = GusApiDbwClient.get_stats_data(field_variable_id, section_id, year_id, period_id)

        GusApiDbwClient.DBW_LOGGER.info("Zostaną wzbogacone pobrane statystyki.")
        for stats in stats_data:
            GusApiDbwClient.DBW_LOGGER.info(f"Wzbogacanie następującego rekordu statystyk: {stats}.")
            dimension_id = stats["id-wymiar-1"]
            dimension_position_id = stats["id-pozycja-1"]
            dimension_description = GusApiDbwClient.get_dimension_description(
                section_id=section_id, dimension_id=dimension_id, dimension_position_id=dimension_position_id)
            stats["dimension_description"] = dimension_description

            try:
                dimension_id_beta = stats.get("id-wymiar-2", None)
                dimension_position_id_beta = stats.get("id-pozycja-2", None)
                dimension_description_beta = GusApiDbwClient.get_dimension_description(
                    section_id=section_id, dimension_id=dimension_id_beta,
                    dimension_position_id=dimension_position_id_beta
                )
                stats["dimension_description_beta"] = dimension_description_beta
            except ValueError:
                stats["dimension_description_beta"] = "-"

            representation_id = stats["id-sposob-prezentacji-miara"]
            stats["representation_description"] = GusApiDbwClient.get_representation_description(representation_id)

        return render(request, "polishness/poland_in_numbers_field_viewing.html",
                  {
                      "field_id": field_id,
                      "field_variable_id": field_variable_id,
                      "field_variable_name": field_variable_name,
                      "section_name": section_name,
                      "period_description": period_description,
                      "stats_data": stats_data,
                  }
                  )

    section_periods = GusApiDbwClient.get_variable_section_periods(
        field_variable_id=field_variable_id, field_variable_name=field_variable_name)

    periods = GusApiDbwClient.get_periods()

    for item_section_periods in section_periods:
        item_section_periods["nazwa_przekroj"] = item_section_periods["nazwa-przekroj"]
        item_section_periods["id_przekroj"] = item_section_periods["id-przekroj"]
        item_section_periods["id_okres"] = item_section_periods["id-okres"]

        for period in periods:
            if period["id-okres"] == item_section_periods["id_okres"]:
                item_section_periods["opis_okres"] = period["opis"]

    current_year = datetime.now().year
    years = range(2000, current_year + 1)

    return render(request, "polishness/poland_in_numbers_field_browser.html",
                  {
                      "field_id": field_id,
                      "field_variable_id": field_variable_id,
                      "field_variable_name": field_variable_name,
                      "section_periods": section_periods,
                      'years': years,
                  }
                  )



def history(request):
    return render(request, "polishness/history.html", {})
