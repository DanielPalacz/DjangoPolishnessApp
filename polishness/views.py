from __future__ import annotations

from datetime import datetime
from os import getenv

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render

from .forms import ContactForm
from .models import ArcheologicalMonument
from .models import GeographicalObject
from .models import Monument
from helpers import configure_logger
from helpers import parent_function_name
from tools import ask_ai
from tools import GeoObjectsSupport
from tools import get_polish_photo_google_links
from tools import GusApiDbwClient
from tools import MonumentsSupport
from tools import TripGenerator

# from tools import get_polish_photo_data

LOGGER_VIEWS = configure_logger("views")
LOGGER_CONTACT_FORM = configure_logger("contact_form")


def home(request):
    """Homepage view"""
    # photo_data = get_polish_photo_data()
    # LOGGER_VIEWS.debug(
    #     f"Zostanie wyświetlone losowe polskie zdjęcie {photo_data!r} {request.build_absolute_uri()!r}, "
    #     f"(view: {parent_function_name()}, path: {request.path!r})."
    # )
    ask_text = (
        "Opowiedz, jak poznawać Polskę i dobrze się przy tym bawić? "
        "Zwróć tekst sformatowany, z paragrafami. Ma być 5 akapitów."
    )
    response_ai = ask_ai(ask=ask_text)
    # photo_data["response_ai"] = response_ai
    # response_ai = response_ai.replace("<body>", f"\n{iframe_script}\n<body>")

    response_ai = response_ai.split("\n\n")

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, (view: {parent_function_name()}, "
        f"path: {request.path!r})."
    )

    return render(request, "polishness/home.html", {"response_ai": response_ai})


def contact(request):
    """Contact view"""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            subject_text = f"[Formularz kontaktowy][poznajmypolske.pl] - wiadomość od: {name} [{email}]."

            LOGGER_CONTACT_FORM.debug(
                f"Zostanie wysłana wiadomość od: {name}/{email}. " f"Treść: {message}. Tytuł: {subject_text}"
            )
            # Send the email
            send_mail(
                subject=subject_text,
                message=message,  # Message content
                from_email="daniel.palacz@pyx.solutions",  # From email
                recipient_list=["daniel.palacz@pyx.solutions"],  # Recipient email list
                fail_silently=False,  # Raise exception if the email fails to send
            )
            messages.success(request, f"Cześć {name}, Twoja wiadomość została właśnie wysłana do mnie.")
            LOGGER_VIEWS.debug(
                f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
                f"(view: {parent_function_name()!r}, path: {request.path!r})."
            )
            return HttpResponseRedirect("/contact/")
    else:
        form = ContactForm()
        LOGGER_VIEWS.debug(
            f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
            f"(view: {parent_function_name()!r}, path: {request.path!r})."
        )
        return render(request, "polishness/contact.html", {"form": form})


def monuments(request):
    """Monuments view"""
    monument_items = None
    archeo_monuments = None
    is_archeological = None
    if request.method == "POST":
        query_params = MonumentsSupport.get_monument_query_params(request.POST)
        quantity = query_params.pop("quantity")
        quantity = 1000 if int(quantity) > 1000 else int(quantity)
        try:
            is_archeological = bool(query_params.pop("is_archeological"))
        except KeyError:
            is_archeological = False

        if is_archeological:
            archeo_monuments_filtered = ArcheologicalMonument.objects.filter(**query_params)
            archeo_monuments = MonumentsSupport.randomize_monuments(
                quantity=quantity, monuments=archeo_monuments_filtered
            )
            return render(request, "polishness/archeological-monuments.html", {"archeo_monuments": archeo_monuments})

        monument_items_cleaned = Monument.objects.filter(**query_params)
        monument_items = MonumentsSupport.randomize_monuments(quantity=int(quantity), monuments=monument_items_cleaned)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(request, "polishness/monuments.html", {"monuments": monument_items})


def monument_single(request, pk):
    """Monuments single view"""
    monument_item = Monument.objects.get(id=pk)
    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )

    ask_text = f"Opowiedz mi o zabytku: {monument_item.name}, {monument_item.locality}"
    if monument_item.street and monument_item.street != "nan":
        ask_text += f", {monument_item.street}"

    if monument_item.address_number and monument_item.address_number != "nan":
        ask_text += f", {monument_item.address_number}"

    if monument_item.chronology != "Data nieznana":
        ask_text += f", czas pochodzenia zabytku {monument_item.chronology}"

    ask_text += "Opis ma mieć maksymalnie 4 zdania."
    response_ai = ask_ai(ask=ask_text)

    return render(request, "polishness/monument_single.html", {"monument": monument_item, "response_ai": response_ai})


def monument_single_archeo(request, pk):
    """Archeological monument single view"""
    monument_item = ArcheologicalMonument.objects.get(id=pk)
    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )

    ask_text = (
        f"Opowiedz mi o zabytku archeogicznym: "
        f"{monument_item.name}, {monument_item.locality}, {monument_item.chronology}, {monument_item.function}. "
        f"Opis ma mieć maksymalnie 4 zdania."
    )

    response_ai = ask_ai(ask=ask_text)

    return render(
        request, "polishness/monument_single_archeo.html", {"monument": monument_item, "response_ai": response_ai}
    )


def monument_single_ai(request, pk):
    """Monument question to AI view"""
    monument_item = Monument.objects.get(id=pk)

    ask_text = f"Opowiedz mi o zabytku: {monument_item.name}, {monument_item.locality}"
    if monument_item.street and monument_item.street != "nan":
        ask_text += f", {monument_item.street}"

    if monument_item.address_number and monument_item.address_number != "nan":
        ask_text += f", {monument_item.address_number}"

    if monument_item.chronology != "Data nieznana":
        ask_text += f", czas pochodzenia zabytku {monument_item.chronology}"

    response_ai = ask_ai(ask=ask_text)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(
        request, "polishness/monument_single_ai.html", {"monument": monument_item, "response_ai": response_ai}
    )


def monument_single_photos(request, pk):
    """Monument view for photo search/displaying"""
    monument_item = Monument.objects.get(id=pk)
    phrase = f"{monument_item.name}, {monument_item.function}, {monument_item.locality}"
    photo_google_links_raw, phrase = get_polish_photo_google_links(phrase=phrase)
    photo_google_links = []
    for link in photo_google_links_raw:
        if "facebook" in link:
            continue
        elif "fbsbx" in link:
            continue
        else:
            photo_google_links.append(link)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(
        request,
        "polishness/monument_single_photos.html",
        {"photo_google_links": photo_google_links, "name": monument_item.name, "locality": monument_item.locality},
    )


def monument_archeo_single_ai(request, pk):
    """Archeological monument question to AI view"""
    monument_item = ArcheologicalMonument.objects.get(id=pk)

    ask_text = (
        f"Opowiedz mi o zabytku archeogicznym: "
        f"{monument_item.name}, {monument_item.locality}, {monument_item.chronology}, {monument_item.function}"
    )

    response_ai = ask_ai(ask=ask_text)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(
        request, "polishness/monument_single_archeo_ai.html", {"monument": monument_item, "response_ai": response_ai}
    )


def nature(request):
    """Nature view"""
    nature_items = None
    if request.method == "POST":
        query_params = GeoObjectsSupport.get_query_params(request.POST)
        quantity = query_params.pop("quantity")
        quantity = 5000 if int(quantity) > 5000 else int(quantity)
        try:
            nature_object_type = query_params.pop("nature_objects")
        except KeyError:
            nature_object_type = None

        nature_items_prefiltered = GeographicalObject.objects.filter(**query_params)
        if nature_object_type is None:
            nature_items = GeoObjectsSupport.randomize(quantity=quantity, geo_objects=nature_items_prefiltered)
            return render(request, "polishness/nature.html", {"nature_items": nature_items})

        elif nature_object_type == "inne":
            nature_items_filtered = nature_items_prefiltered.exclude(geo_object_type__in=GeoObjectsSupport.MAPPER_ALL)
            nature_items = GeoObjectsSupport.randomize(quantity=quantity, geo_objects=nature_items_filtered)
            return render(request, "polishness/nature.html", {"nature_items": nature_items})

        else:
            nature_items_filtered = nature_items_prefiltered.filter(
                geo_object_type__in=GeoObjectsSupport.MAPPER[nature_object_type]
            )
            nature_items = GeoObjectsSupport.randomize(quantity=quantity, geo_objects=nature_items_filtered)
            return render(request, "polishness/nature.html", {"nature_items": nature_items})

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(request, "polishness/nature.html", {"nature_items": nature_items})


def nature_single(request, pk):
    """Nature single item view"""
    nature_item = GeographicalObject.objects.get(id=pk)
    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    ask_text = (
        f"Opowiedz mi o obiekcie przyrodniczym: {nature_item.name}. Typ obiektu: {nature_item.geo_object_type}."
        f" Lokalizacja obiektu: województwo {nature_item.voivodeship}, powiat: {nature_item.county},"
        f" gmina: {nature_item.parish}. Opis ma mieć maksymalnie 4 zdania."
    )
    response_ai = ask_ai(ask=ask_text)
    map_photo_link = get_map_photo_link(latitude=nature_item.latitude, longitude=nature_item.longitude)
    return render(
        request,
        "polishness/nature_single.html",
        {"nature_item": nature_item, "response_ai": response_ai, "map_photo_link": map_photo_link},
    )


def nature_single_ai(request, pk):
    """Nature question to AI view"""
    nature_item = GeographicalObject.objects.get(id=pk)

    ask_text = (
        f"Opowiedz mi o obiekcie przyrodniczym: {nature_item.name}. Typ obiektu: {nature_item.geo_object_type}."
        f" Lokalizacja obiektu: województwo {nature_item.voivodeship}, powiat: {nature_item.county},"
        f" gmina: {nature_item.parish}."
    )
    response_ai = ask_ai(ask=ask_text)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(request, "polishness/nature_single_ai.html", {"nature_item": nature_item, "response_ai": response_ai})


def poland_in_numbers(request):
    """Presents root fields view"""
    root_fields = GusApiDbwClient.get_dbw_root_fields()
    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(request, "polishness/poland_in_numbers.html", {"root_fields": root_fields})


def poland_in_numbers_fields(request, field_id, field_name):
    """Poland in numbers fields"""
    fields = GusApiDbwClient.get_dbw_fields(field_id=field_id, field_name=field_name)
    field_variables = GusApiDbwClient.get_dbw_field_variables(field_id=field_id, field_name=field_name)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(
        request, "polishness/poland_in_numbers_fields.html", {"fields": fields, "field_variables": field_variables}
    )


def poland_in_numbers_field_browser(request, field_id, field_variable_id, field_variable_name):
    """Poland in numbers browser view"""
    if request.method == "POST":
        section_name, section_id, period_id, period_description = request.POST["przekroj__przekrojid__okresid"].split(
            "__"
        )
        year_id = request.POST["rok"]
        GusApiDbwClient.DBW_LOGGER.info(
            f"Dla następujących parametrów zostaną pobrane dane statystyczne. "
            f"Przekrój: {section_name} (przekroj_id={section_id}). "
            f"Zmienna: {field_variable_name} (zmienna_id={field_variable_id}). "
            f"Okres: {period_description} (okres_id={period_id}). "
            f"Rok: {year_id}."
        )
        stats_data = GusApiDbwClient.get_stats_data(field_variable_id, section_id, period_id, year_id)

        GusApiDbwClient.DBW_LOGGER.info("Zostaną wzbogacone pobrane dane statystyczne.")
        section_dimensions = GusApiDbwClient.get_section_dimensions(section_id=section_id)
        for stats in stats_data:
            GusApiDbwClient.DBW_LOGGER.info(f"Wzbogacanie następującego rekordu danych statystycznych: {stats}.")
            dimension_id = stats["id-wymiar-1"]
            dimension_position_id = stats["id-pozycja-1"]
            dimension_description = GusApiDbwClient.get_dimension_description(
                section_id=section_id,
                dimension_id=dimension_id,
                dimension_position_id=dimension_position_id,
                section_dimensions=section_dimensions,
            )
            stats["dimension_description"] = dimension_description

            try:
                dimension_id_beta = stats.get("id-wymiar-2", False)
                dimension_position_id_beta = stats.get("id-pozycja-2", False)
                dimension_description_beta = GusApiDbwClient.get_dimension_description(
                    section_id=section_id,
                    dimension_id=dimension_id_beta,
                    dimension_position_id=dimension_position_id_beta,
                    section_dimensions=section_dimensions,
                )
                stats["dimension_description_beta"] = dimension_description_beta
            except ValueError:
                stats["dimension_description_beta"] = "-"

            representation_id = stats["id-sposob-prezentacji-miara"]
            stats["representation_description"] = GusApiDbwClient.get_representation_description(representation_id)

        LOGGER_VIEWS.debug(
            f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
            f"(view: {parent_function_name()!r}, path: {request.path!r})."
        )
        return render(
            request,
            "polishness/poland_in_numbers_field_viewing.html",
            {
                "field_id": field_id,
                "field_variable_id": field_variable_id,
                "field_variable_name": field_variable_name,
                "section_name": section_name,
                "period_description": period_description,
                "stats_data": stats_data,
            },
        )

    section_periods = GusApiDbwClient.get_variable_section_periods(
        field_variable_id=field_variable_id, field_variable_name=field_variable_name
    )

    periods = GusApiDbwClient.get_periods()

    for item_section_periods in section_periods:
        item_section_periods["nazwa_przekroj"] = item_section_periods["nazwa-przekroj"]
        item_section_periods["id_przekroj"] = item_section_periods["id-przekroj"]
        item_section_periods["id_okres"] = item_section_periods["id-okres"]

        for period in periods:
            if period["id-okres"] == item_section_periods["id_okres"]:
                item_section_periods["opis_okres"] = period["opis"]

    current_year = datetime.now().year
    years = range(2011, current_year + 1)

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(
        request,
        "polishness/poland_in_numbers_field_browser.html",
        {
            "field_id": field_id,
            "field_variable_id": field_variable_id,
            "field_variable_name": field_variable_name,
            "section_periods": section_periods,
            "years": years,
        },
    )


def history(request):
    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(request, "polishness/history.html", {})


def trips(request):
    """Trips generation view"""
    monument_items = None
    if request.method == "POST":
        query_params = MonumentsSupport.get_monument_query_params(request.POST)
        quantity = query_params.pop("quantity")
        quantity = 10 if int(quantity) > 10 else int(quantity)
        monument_items_cleaned = Monument.objects.exclude(latitude="nan", longitude="nan").filter(**query_params)
        monument_items = MonumentsSupport.randomize_monuments(quantity=int(quantity), monuments=monument_items_cleaned)

        trip_generator = TripGenerator(quantity=quantity, monuments=monument_items)
        monument_items = trip_generator.generate_trip()

    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    return render(request, "polishness/trips.html", {"monuments": monument_items})


def get_map_photo_link(latitude: str, longitude=str) -> str:
    """Prepares link to the map satellite photo.

    Args:
        latitude: Latitude of geographical point.
        longitude: Longitude of geografical point.

    Returns:
        Link to the map satellite photo of geografical point.
    """
    google_maps_key = getenv("GOOGLE_MAPS_API_KEY")
    return (
        f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=14&size=1280x1280&"
        f"scale=2&format=png&maptype=hybrid&markers=color:yellow%7C{latitude},{longitude}&markers=size:mid%&"
        f"key={google_maps_key}"
    )


def photo_discovery(request):
    LOGGER_VIEWS.debug(
        f"Zostanie wyświetlona strona {request.build_absolute_uri()!r}, "
        f"(view: {parent_function_name()!r}, path: {request.path!r})."
    )
    photo_google_links_raw, phrase = get_polish_photo_google_links()
    # "fbsbx.com"
    photo_google_links = []
    for link in photo_google_links_raw:
        if "facebook" in link:
            continue
        elif "fbsbx" in link:
            continue
        else:
            photo_google_links.append(link)

    # print(photo_google_links)

    return render(
        request, "polishness/photo_discovery.html", {"photo_google_links": photo_google_links, "phrase": phrase}
    )
