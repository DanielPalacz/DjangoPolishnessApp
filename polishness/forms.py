from __future__ import annotations

from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Imię/nick",
        widget=forms.TextInput(attrs={"title": "Proszę podaj swoje imię lub nick."}),
        error_messages={"required": "Proszę podaj swoje imię lub nick."},
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.TextInput(attrs={"title": "Proszę podaj poprawny adres e-mail."}),
        error_messages={"required": "Proszę podać adres e-mail.", "invalid": "Wprowadź poprawny adres e-mail."},
    )
    message = forms.CharField(widget=forms.Textarea(attrs={"title": ""}), required=True, label="Wiadomość")
