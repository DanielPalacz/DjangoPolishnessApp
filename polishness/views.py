from django.shortcuts import render, HttpResponseRedirect

from django.contrib import messages
from django.core.mail import send_mail

from tools import get_polish_photo_link, get_monument_query_params, randomize_monuments, TripGenerator
from .forms import ContactForm
from .models import Monument


def home(request):
    photo_link = get_polish_photo_link()
    return render(request, "polishness/home.html", {"photo_link": photo_link})

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
        monument_items_cleaned = Monument.objects.exclude(latitude="nan", longitude="nan").filter(**query_params)
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
