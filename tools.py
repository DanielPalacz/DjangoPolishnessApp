import json
from os.path import exists, getsize
import logging
from typing import Optional

from django.http import QueryDict
from django.db.models.query import QuerySet

import pandas as pd
from os.path import dirname
from os import getenv
import requests
from random import randint
from openai import OpenAI


from polishness.models import Monument

def ask_ai(ask: str) -> str:
    client = OpenAI(
        # This is the default and can be omitted
        api_key=getenv("OPENAI_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": ask,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content



def get_static_dir() -> str:
    return dirname(__file__) + "/static/"

STATIC_DIR = get_static_dir()
CSV_DB_PATH = STATIC_DIR + "monuments.csv"

def populate_db() -> None:
    df_data = pd.read_csv(CSV_DB_PATH, dtype=object)
    df_size = len(df_data.index)
    for number in range(df_size):
        input_data = tuple(df_data.iloc[number])
        Monument.objects.create(
            library_id=input_data[0],
            security_form=input_data[1],
            location_accuracy=input_data[2],
            name=input_data[3],
            chronology=input_data[4],
            function=input_data[5],
            documents=input_data[6],
            registration_date=input_data[7],
            voivodeship=input_data[8],
            county=input_data[9],
            parish=input_data[10],
            locality=input_data[11],
            street=input_data[12],
            address_number=input_data[13],
            latitude=input_data[14],
            longitude=input_data[15]
        )

def get_polish_photo_link() -> dict:
    unplash_api_key = getenv("UNPLASH_API_KEY")
    url_request = f"https://api.unsplash.com/photos/random?query=poland&client_id={unplash_api_key}&count=1"
    response = requests.get(url_request)
    if response.status_code == 200:
        return {
            "photo_link": response.json()[0]["urls"]["full"],
            "photo_author": response.json()[0]["user"]["name"],
            "photo_author_link": response.json()[0]["user"]["links"]["html"],
            "photo_city": response.json()[0]["location"]["city"]
        }
    return {}

def get_monument_query_params(posta_data: QueryDict) -> dict:
    query_params = {
        "locality": posta_data["locality"],
        "parish": posta_data["parish"],
        "county": posta_data["county"],
        "voivodeship": posta_data["voivodeship"],
        "quantity": posta_data["quantity"],
    }
    return {key: value for key, value in query_params.items() if value}

def randomize_monuments(quantity: int, monuments: QuerySet[Monument]) -> list[Monument]:
    monuments_len = len(monuments)
    if quantity > monuments_len:
        return [monument for monument in monuments]

    randomized_monuments = []
    random_numbers = []
    for num in range(quantity):
        random_number = randint(1, monuments_len - 1)
        while random_number in random_numbers:
            random_number = randint(1, monuments_len)

        random_monument = monuments[random_number]
        randomized_monuments.append(random_monument)
        random_numbers.append(random_number)

    return randomized_monuments

class TripGenerator:
    QUANTITY_LIMIT = 10

    def __init__(self, quantity: int, monuments: list[Monument]):
        self.__monuments = monuments
        if quantity > self.QUANTITY_LIMIT:
            self.__quantity = 10
        elif quantity > len(monuments):
            self.__quantity = len(monuments)
        else:
            self.__quantity = quantity

    def generate_trip(self) -> list:
        return self.__sort_monuments()

    def __sort_monuments(self) -> list[Monument]:
        monument_items = []
        for monument in self.__monuments:
            latitude = monument.latitude
            longitude = monument.longitude
            monument_item = MonumentItem(data=monument, latitude=latitude, longitude=longitude)
            monument_items.append(monument_item)

        monument_items.sort()
        return [monument_item.monument for monument_item in monument_items]


class MonumentItem:

    def __init__(self, data: Monument, latitude: str, longitude: str):
        self.__data = data
        self.__latitude = float(latitude)
        self.__longitude = float(longitude)
        self.__reference_distance = self.calc_reference_measure()

    @property
    def monument(self):
        return self.__data

    @property
    def reference_measure(self):
        return self.__reference_distance

    def calc_reference_measure(self):
        measure = self.__latitude * self.__latitude + self.__longitude * self.__longitude
        return measure

    def __lt__(self, other):
        return self.reference_measure < other.reference_measure

    def __le__(self, other):
        return self.reference_measure <= other.reference_measure

    def __eq__(self, other):
        return self.reference_measure == other.reference_measure

    def __ne__(self, other):
        return self.reference_measure != other.reference_measure

    def __gt__(self, other):
        return self.reference_measure > other.reference_measure

    def __ge__(self, other):
        return self.reference_measure >= other.reference_measure


# API DBW
# https://api-dbw.stat.gov.pl/apidocs/index.html


class GusApiDbwClient:
    """ Delivers client functionalities for GUS DBW (Dziedzinowe Bazy Wiedzy)

    Documentation: https://api-dbw.stat.gov.pl/apidocs/index.html
    """
    DBW_LOGGER = logging.getLogger("autor_log")
    DBW_LOGGER.setLevel(logging.DEBUG)
    DBW_LOGGER_HANDLER = logging.FileHandler("logs/dbw.log")
    DBW_LOGGER_HANDLER.setLevel(logging.DEBUG)
    DBW_LOGGER_FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    DBW_LOGGER_HANDLER.setFormatter(DBW_LOGGER_FORMATTER)
    DBW_LOGGER.addHandler(DBW_LOGGER_HANDLER)

    GUS_DBW_API_KEY = getenv("GUS_DBW_API_KEY")
    REQUEST_HEADERS = {
        "accept": "application/json",
        "X-ClientId": GUS_DBW_API_KEY
    }

    @classmethod
    def get_dbw_root_fields(cls) -> list:
        """" Delivers 'Podstawowe Dziedziny Wiedzy' from DBW GUS API. """
        url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/area/area-area?lang=pl"
        cls.DBW_LOGGER.info(f"Zostaną pobrane podstawowe dziedziny.")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
        cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}). "
                            f"Zwrócony kod odpowiedzi: {response.status_code}.")
        if response.status_code == 200:
            root_fields = [
                {
                    "field_id": field_data.get("id"),
                    "field_name": field_data.get("nazwa")
                } for field_data in response.json() if field_data.get("id-nadrzedny-element") is None]
            cls.DBW_LOGGER.debug(f"Odszukano podstawowe dziedziny ({root_fields}).")
            return root_fields

        else:
            cls.DBW_LOGGER.error("Nieudane zapytanie, zostanie zwrócona pusta lista bez podstawowych dziedzin wiedzy.")
            return []

    @classmethod
    def get_dbw_fields(cls, field_id: int, field_name: str) -> list:
        """" Delivers 'Podkategorie Dziedzinowe Wiedzy' from DBW GUS API. """
        url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/area/area-area?lang=pl"
        cls.DBW_LOGGER.info(f"Zostaną wyszukane podkategorie dziedzin wiedzy dla: {field_name} (field_id={field_id}).")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
        cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}). "
                            f"Zwrócony kod odpowiedzi: {response.status_code}.")

        if response.status_code == 200:
            fields = [
                {
                    "field_id": field_data.get("id"),
                    "field_name": field_data.get("nazwa"),
                    "field_variables": field_data.get("czy-zmienne")
                } for field_data in response.json() if field_data.get("id-nadrzedny-element") == field_id]
            cls.DBW_LOGGER.info(f"Odszukano podkategorie dziedzin wiedzy dla: {field_name} (field_id={field_id}). "
                                f"Znaleziono: {fields}.")
            return fields

        else:
           cls.DBW_LOGGER.error("Nieudane zapytanie, zostanie zwrócona pusta lista bez podkategorii dziedzin wiedzy.")
           return []

    @classmethod
    def get_dbw_field_variables(cls, field_id: int, field_name: str) -> list:
        """" Delivers 'Zmienne dla Kategorii Dziedzin Wiedzy' from DBW GUS API. """
        url_request = f"https://api-dbw.stat.gov.pl/api/1.1.0/area/area-variable?id-obszaru={field_id}&lang=pl"
        cls.DBW_LOGGER.info(f"Zostaną wyszukane zmienne dla {field_name!r} (field_id={field_id}).")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające zmienne dla {field_name!r} ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
        cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające zmienne dla {field_name!r} ({url_request}). "
                            f"Zwrócony kod odpowiedzi: {response.status_code}.")

        if response.status_code == 200:
            field_variables = [
                {"field_id": field_data.get("id"),
                 "field_variable_id": field_data.get("id-zmienna"),
                 "field_variable_name": field_data.get("nazwa-zmienna")
                 } for field_data in response.json()]
            cls.DBW_LOGGER.info(f"Wyszukano zmienne dla: {field_name!r} (field_id={field_id}). "
                                f"Znaleziono: {field_variables}.")

            return field_variables

        elif response.status_code == 404:
            cls.DBW_LOGGER.info(f"Dany obszar najprawdopodobniej nie posiada zmiennych statystycznych, zostanie "
                                 f"zwrócona pusta lista bez zmiennych (wyszukiwanie dla {field_name!r}).")

        else:
            cls.DBW_LOGGER.error(f"Nieudane zapytanie, zostanie zwrócona pusta lista bez zmiennych (wyszukiwanych dla "
                                 f"{field_name!r}).")
            return []

    @classmethod
    def get_variable_section_periods(cls, field_variable_id: int, field_variable_name: str) -> list:
        """" Delivers 'Przekroje i okresy dla Zmiennej' from DBW GUS API. """

        section_periods = []
        responses_data = []
        filename_path = "static/all_section_periods.json"

        if exists(filename_path) and getsize(filename_path):
            cls.DBW_LOGGER.debug(f"Plik {filename_path!r} jest już na dysku, więc zostanie wykorzystany przy ustalaniu "
                                 f"przekrojów i okresów dla zmiennej {field_variable_name!r}.")
            with open(filename_path, "r", encoding='utf-8') as json_file:
                responses_data = json.load(json_file)

        else:
            cls.DBW_LOGGER.debug(f"Pliku {filename_path!r} nie ma jeszcze na dysku, więc wszystkie przekroje i okresy "
                                 f"zostaną wczytane z DBW API.")
            url_request1 = "https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-periods?ile-na-stronie=5000&numer-strony=0&lang=pl"
            url_request2 = "https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-periods?ile-na-stronie=5000&numer-strony=1&lang=pl"

            cls.DBW_LOGGER.info(f"Zostaną pobrane wszystkie przekroje/okresy z DBW API. "
                                f"Wykonane będą dwa zapytania (1: {url_request1}, 2: {url_request2}).")

            response1 = requests.get(url_request1, headers=cls.REQUEST_HEADERS)

            cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające przekroje/okresy z DBW API ({url_request1}). "
                                f"Zwrócony kod odpowiedzi: {response1.status_code}.")
            if response1.status_code == 200:
                responses_data = response1.json()["data"]
            response2 = requests.get(url_request2, headers=cls.REQUEST_HEADERS)
            cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające przekroje/okresy z DBW API ({url_request2}). "
                                f"Zwrócony kod odpowiedzi: {response2.status_code}.")
            if response2.status_code == 200:
                responses_data += response2.json()["data"]

            with open(filename_path, "w", encoding='utf-8') as json_file:
                json.dump(responses_data, json_file, indent=4)
                cls.DBW_LOGGER.info(f"Zapisano wszystkie przekroje/okresy do pliku {filename_path!r}.")

        cls.DBW_LOGGER.info(f"Ustalenie przekrojów i okresów dla zmiennej {field_variable_name!r}.")
        for item in responses_data:
            if item.get("id-zmienna") == field_variable_id:
                section_periods.append(item)

        cls.DBW_LOGGER.info(f"Ustalono przekroje i okresy dla zmiennej {field_variable_name!r} ({section_periods}).")

        return section_periods


    @classmethod
    def get_periods(cls) -> list:
        filename_path = "static/all_periods.json"

        if exists(filename_path) and getsize(filename_path):
            cls.DBW_LOGGER.debug(f"Plik {filename_path!r} jest już na dysku, więc zostanie wykorzystany. ")
            with open(filename_path, "r", encoding='utf-8') as json_file:
                periods = json.load(json_file)
                cls.DBW_LOGGER.info(f"Wczytano wszystkie okresy z pliku {filename_path!r}. "
                                    f"(Liczba okresów: {len(periods)}). Zostaną dalej wykorzystane.")
                return periods

        else:
            cls.DBW_LOGGER.debug(f"Pliku {filename_path!r} nie ma jeszcze na dysku, więc wszystkie okresy "
                                 f" zostaną wczytane z DBW API.")
            url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/dictionaries/periods-dictionary"
            response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
            periods = response.json()["data"]
            with open(filename_path, "w", encoding='utf-8') as json_file:
                json.dump(periods, json_file, indent=4)
                cls.DBW_LOGGER.info(f"Zapisano wszystkie okresy do pliku {filename_path!r}. "
                                    f"(Liczba okresów: {len(periods)}). Zostaną dalej wykorzystane.")
            return periods


    @classmethod
    def get_stats_data(cls, field_variable_id, section_id, year_id, period_id) -> list:
        url_request = (f"https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-data-section?"
                       f"id-zmienna={field_variable_id}&"
                       f"id-przekroj={section_id}&"
                       f"id-rok={year_id}&"
                       f"id-okres={period_id}&"
                       f"ile-na-stronie=5000&numer-strony=0&lang=pl")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające dane statystyczne ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
        cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające dane statystyczne ({url_request}). "
                            f"Zwrócony kod odpowiedzi: {response.status_code}.")

        if response.status_code == 200:
            stats_data = response.json()["data"]
            cls.DBW_LOGGER.info(f"Pobrane dane statystyczne ({url_request}): {stats_data}.")
            return stats_data

        cls.DBW_LOGGER.info(f"Dany obszar najprawdopodobniej nie posiada danych statystycznych, zostanie zwrócona "
                            f"pusta lista bez danych.")
        return []

    @classmethod
    def get_dimension_description(cls, section_id: int, dimension_id: int, dimension_position_id: Optional) -> str:
        if dimension_id is None or dimension_position_id is None:
            err_message = \
                "Zmienne dimension_id i dimension_position_id muszą być typu integer przy ustalaniu opisu wymiaru."
            cls.DBW_LOGGER.error(err_message)
            raise ValueError(err_message)


        cls.DBW_LOGGER.info(f"Nastąpi ustalanie opisu dla wymiaru {dimension_id!r} "
                             f"(id pozycji: {dimension_position_id}, id przekroju: {section_id}).")
        url_request = \
            f"https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-position?id-przekroj={section_id}&lang=pl"
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające dane wymarów dla przekroju {section_id!r} "
                             f"(id pozycji: {dimension_position_id}, id wymiaru: {dimension_id}) ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
        cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające dane wymarów dla przekroju {dimension_id!r} "
                            f"({url_request}). Zwrócony kod odpowiedzi: {response.status_code}.")
        if response.status_code == 200:
            dimensions = response.json()
            cls.DBW_LOGGER.info(f"Pobrane dane wymiarów przekroju {section_id!r}: ({dimensions}).")
            for dim in dimensions:
                if dim.get("id-pozycja") == dimension_position_id:
                    dim_description = dim.get("nazwa-wymiar")
                    cls.DBW_LOGGER.info(f"Ustalono opis wymiaru dla {dimension_id!r} "
                                        f"(id pozycji: {dimension_position_id}): {dim_description!r}.")
                    return dim_description

        return ""

    @classmethod
    def get_representation_description(cls, representation_id) -> str:
        cls.DBW_LOGGER.info(f"Nastąpi ustalanie opisu dla miary (id miary: {representation_id!r}).")
        url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/dictionaries/way-of-presentation?page=1&page-size=5000&lang=pl"
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające dane opisu miar ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS)
        cls.DBW_LOGGER.info(f"Wykonano zapytanie pobierające dane opisu miar ({url_request}). "
                            f"Zwrócony kod odpowiedzi: {response.status_code}.")
        if response.status_code == 200:
            representation_measures = response.json()["data"]
            cls.DBW_LOGGER.info(f"Pobrane dane opisu miar: {representation_measures}.")
            for representation in representation_measures:
                if representation.get("id-sposob-prezentacji-miara") == representation_id:
                    measure_name = representation.get("nazwa")
                    cls.DBW_LOGGER.info(f"Ustalono nazwę miary dla id miary {representation_id!r} => {measure_name!r}.")
                    return measure_name

        return ""
