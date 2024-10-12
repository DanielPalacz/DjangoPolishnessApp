from django.http import QueryDict
from django.shortcuts import render, HttpResponseRedirect

from django.contrib import messages
from django.core.mail import send_mail

from tools import get_polish_photo_link
from .forms import ContactForm
from .models import Monument


def __get_monument_query_params(posta_data: QueryDict) -> dict:
    query_params = {
        "locality": posta_data["locality"],
        "parish": posta_data["parish"],
        "county": posta_data["county"],
        "voivodeship": posta_data["voivodeship"],
        "quantity": posta_data["quantity"],
    }

    return {key: value for key, value in query_params.items() if value}


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
    monuments = None
    if request.method == 'POST':
        cleaned_query_params = __get_monument_query_params(request.POST)
        limit_quatity = cleaned_query_params.pop("quantity")
        monuments = Monument.objects.filter(**cleaned_query_params)[:int(limit_quatity)]

    return render(request, "polishness/monuments.html", {"monuments": monuments})

def monument_single(request, pk):
    monument_item = Monument.objects.get(id=pk)
    print(pk)
    print(pk)
    print(pk)
    return render(request, "polishness/monument_single.html", {"monument": monument_item})
