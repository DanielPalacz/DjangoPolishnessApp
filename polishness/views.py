from django.shortcuts import render, HttpResponseRedirect

from django.contrib import messages
from django.core.mail import send_mail

from tools import get_polish_photo_link, get_monument_query_params, randomize_monuments, TripGenerator, ask_ai, \
    get_dbw_fields, get_dbw_field_variables, get_dbw_root_fields, get_variable_section_periods, get_periods, \
    get_stats_data
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
    root_fields = get_dbw_root_fields()
    return render(request, "polishness/poland_in_numbers.html", {"root_fields": root_fields})

def poland_in_numbers_fields(request, field_id):
    fields = get_dbw_fields(root_field=field_id)
    field_variables = get_dbw_field_variables(field_id=field_id)

    return render(request, "polishness/poland_in_numbers_fields.html",
                  {"fields": fields, "field_variables": field_variables})

def poland_in_numbers_field_viewing(request, field_id, field_variable_id, field_variable_name):

    if request.method == 'POST':
        section, section_id, period_id = request.POST["przekroj__przekrojid__okresid"].split("__")
        year_id = request.POST["rok"]
        print(section)
        print(section_id)
        print(period_id)
        print(year_id)

        stats_data = get_stats_data(field_variable_id, section_id, year_id, period_id)
        return render(request, "polishness/poland_in_numbers_field_viewing.html", {"stats_data": stats_data})

    section_periods = get_variable_section_periods(field_variable_id=field_variable_id)

    section_periods_cleaned = []
    periods = get_periods()

    for item_section_periods in section_periods:
        item_section_periods["nazwa_przekroj"] = item_section_periods["nazwa-przekroj"]
        item_section_periods["id_przekroj"] = item_section_periods["id-przekroj"]
        item_section_periods["id_okres"] = item_section_periods["id-okres"]

        for period in periods:
            if period["id-okres"] == item_section_periods["id_okres"]:
                item_section_periods["opis_okres"] = period["opis"]

    return render(request, "polishness/poland_in_numbers_field_browser.html",
                  {
                      "field_id": field_id,
                      "field_variable_id": field_variable_id,
                      "field_variable_name": field_variable_name, "section_periods": section_periods
                  }
                  )



def history(request):
    return render(request, "polishness/history.html", {})

