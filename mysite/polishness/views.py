from django.shortcuts import render, HttpResponseRedirect

from django.contrib import messages
from django.core.mail import send_mail

from .forms import ContactForm



def home(request):
    return render(request, "polishness/home.html", {})

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
                subject=f"Contact form message from {name} [{email}].",  # Subject of the email
                message=message,  # Message content
                from_email='daniel.palacz@pyx.solutions',  # From email
                recipient_list=['daniel.palacz@pyx.solutions'],  # Recipient email list
                fail_silently=False,  # Raise exception if the email fails to send
            )
            messages.success(request, f"{name}, Twoja wiadomość właśnie została wysłana do mnie. Dziękuję.")
            return HttpResponseRedirect("/contact/")
    else:
        form = ContactForm()
        return render(request, "polishness/contact.html", {"form": form})

def monuments(request):
    return render(request, "polishness/monuments.html", {})