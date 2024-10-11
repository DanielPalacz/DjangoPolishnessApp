
from django.db import models


class Monument(models.Model):
    library_id = models.CharField(max_length=100) # biblioteczny identyfikator
    security_form = models.CharField(max_length=100) # forma ochrony
    location_accuracy = models.CharField(max_length=100) # dokładność położenia
    name = models.CharField(max_length=100) # nazwa
    chronology = models.CharField(max_length=100) # chronologia
    function = models.CharField(max_length=100) # funkcja
    documents = models.CharField(max_length=100) # wykaz dokumentów
    registration_date = models.CharField(max_length=100) # data wpisu
    voivodeship = models.CharField(max_length=100) # województwo
    county = models.CharField(max_length=100) # powiat
    parish = models.CharField(max_length=100) # gmina
    locality = models.CharField(max_length=100) # miejscowość
    street = models.CharField(max_length=100) # ulica
    address_number = models.CharField(max_length=100) # numer adresowy
    latitude = models.CharField(max_length=100) #  szerokość geograficzna
    longitude = models.CharField(max_length=100) #  długość geograficzna

    class Meta:
        ordering = ("-name",)

    def __str__(self):
        return f"{self.name} {self.function}"
