from __future__ import annotations

import datetime
import json
from datetime import date
from os import getenv
from os.path import exists
from os.path import getsize
from secrets import randbelow
from typing import Optional

import feedparser
import pandas as pd
import requests
from django.db.models.query import QuerySet
from django.http import QueryDict
from openai import OpenAI

from helpers import configure_logger
from helpers import get_static_dir
from polishness.models import ArcheologicalMonument
from polishness.models import GeographicalObject
from polishness.models import Monument


def ask_ai(ask: str) -> str:
    """Asks openai question.

    Args:
        ask: Question text.

    Returns:
        Answer text from the openai.
    """
    client = OpenAI(
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


def current_day_message() -> str:
    """Provides current day message (without year).

    Returns:
        Current day message (without year).
    """
    days = {
        1: "pierwszy",
        2: "drugi",
        3: "trzeci",
        4: "czwarty",
        5: "piąty",
        6: "szósty",
        7: "siódmy",
        8: "ósmy",
        9: "dziewiąty",
        10: "dziesiąty",
        11: "jedenasty",
        12: "dwunasty",
        13: "trzynasty",
        14: "czternasty",
        15: "piętnasty",
        16: "szesnasty",
        17: "siedemnasty",
        18: "osiemnasty",
        19: "dziewiętnasty",
        20: "dwudziesty",
        21: "dwudziesty pierwszy",
        22: "dwudziesty drugi",
        23: "dwudziesty trzeci",
        24: "dwudziesty czwarty",
        25: "dwudziesty piąty",
        26: "dwudziesty szósty",
        27: "dwudziesty siódmy",
        28: "dwudziesty ósmy",
        29: "dwudziesty dziewiąty",
        30: "trzydziesty",
        31: "trzydziesty pierwszy",
    }

    # Słownik z nazwami miesięcy
    months = {
        1: "styczeń",
        2: "luty",
        3: "marzec",
        4: "kwiecień",
        5: "maj",
        6: "czerwiec",
        7: "lipiec",
        8: "sierpień",
        9: "wrzesień",
        10: "październik",
        11: "listopad",
        12: "grudzień",
    }

    current_day = datetime.date.today()

    day_ = days[current_day.day]
    month_ = months[current_day.month]

    return f"{day_} {month_}"


def get_history_news() -> str:
    """Provides current day message (without year).

    Returns:
        Current day message (without year).
    """
    current_day = datetime.date.today()
    filename = f"{current_day.day}d_{current_day.month}m.txt"
    file_path = get_static_dir() + "historical_news/" + str(current_day.month) + "/" + filename

    with open(file_path, "r") as file:
        text = file.read()

    return text


def get_polish_photo_data() -> dict:
    """Download polish photo data from the unplash api.

    Returns:
        The polish photo data dictionary (photo_link, photo_author, photo_author_link, photo_city)
    """
    unplash_api_key = getenv("UNPLASH_API_KEY")
    url_request = f"https://api.unsplash.com/photos/random?query=poland&client_id={unplash_api_key}&count=1"
    response = requests.get(url_request, timeout=60)
    if response.status_code == 200:
        return {
            "photo_link": response.json()[0]["urls"]["full"],
            "photo_author": response.json()[0]["user"]["name"],
            "photo_author_link": response.json()[0]["user"]["links"]["html"],
            "photo_city": response.json()[0]["location"]["city"],
        }
    return {}


def get_polish_photo_google_links(phrase: Optional[str] = None) -> list:
    """Download polish photo data from the Google custom search engine api.

    Args:
        phrase: Query text.

    Returns:
        List with the polish photo links.
    """
    query_keywords = [
        "Polski krajobraz",
        "Polski pejzaż",
        "Polskie lasy",
        "Polskie rzeki",
        "Polskie góry, Tatry",
        "Polskie jeziora",
        "Morze Bałtyckie, Polska",
        "Wisła, Polska",
        "Odra, Polska",
        "Warta, Polska",
        "Polskie plaże",
        "Polska przyroda",
        "Parki Narodowe w Polsce",
        "Polskie zwierzęta",
        "Polska grzyby",
        "Polska wieś",
        "Polska PRL",
        "Polskie kościoły",
        "Polskie zabytki",
        "Polskie zabytki archeologiczne",
        "Polskie herby",
        "Polska sztuka",
        "Polska znaczki pocztowe",
        "Kraków Wawel",
        "Łazienki Warszawa",
        "Kraków Rynek",
        "Warszawa Belweder",
        "Warszawa Pałac Kultury",
        "Kraków Kościół Mariacki",
        "Kraków sukiennice",
        "Kraków Kazimierz",
        "Polska Wrocław",
        "Polska Bydgoszcz",
        "Polska Lublin",
        "Polska Zielona Góra",
        "Polska Łódź",
        "Polska Kraków",
        "Polska Warszawa",
        "Polska Opole",
        "Polska Rzeszów",
        "Polska Białystok",
        "Polska Gdańsk",
        "Polska Katowice",
        "Polska Kielce",
        "Polska Olsztyn",
        "Polska Poznań",
        "Polska Szczecin",
    ]
    if phrase is None:
        random_number = randbelow(len(query_keywords))
        phrase = query_keywords[random_number]

    google_custom_search_api_key = getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    google_custom_search_engine_id = getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    url_request = (
        f"https://www.googleapis.com/customsearch/v1?q={phrase}&searchType=image&"
        f"imgSize=xlarge&key={google_custom_search_api_key}&cx={google_custom_search_engine_id}"
    )
    response = requests.get(url_request, timeout=60)
    if response.status_code == 200:
        photo_items = response.json().get("items", [])
        # print(photo_items)
        photo_links = [photo_item.get("link") for photo_item in photo_items]
        return [photo_links, phrase]
    else:
        return [[], phrase]


def populate_archeological_monument_db_table() -> None:
    """Populates data for the monuments table.

    Returns:
        None
    """
    csv_db_path = get_static_dir() + "archaeological_monuments.csv"
    df_data = pd.read_csv(csv_db_path, sep=";", dtype=object)
    df_size = len(df_data.index)
    for number in range(df_size):
        if number == 0:
            continue
        input_data = tuple(df_data.iloc[number])
        ArcheologicalMonument.objects.create(
            library_id=input_data[0],
            security_form=input_data[1],
            location_accuracy=input_data[2],
            name=input_data[3],
            field_azp=input_data[4],
            position_area_number=input_data[5],
            chronology=input_data[6],
            function=input_data[7],
            documents=input_data[8],
            registration_date=input_data[9],
            voivodeship=input_data[10],
            county=input_data[11],
            parish=input_data[12],
            locality=input_data[13],
            link=input_data[14],
        )


def populate_geographical_object_table() -> None:
    """Populates data for the monuments table.

    Returns:
        None
    """
    csv_db_path = get_static_dir() + "geographicalObjects.csv"
    df_data = pd.read_csv(csv_db_path, sep=";", dtype=object)
    df_size = len(df_data.index)
    for number in range(df_size):
        input_data = tuple(df_data.iloc[number])
        GeographicalObject.objects.create(
            name=input_data[0],
            geo_object_type=input_data[1],
            parish=input_data[2],
            county=input_data[3],
            voivodeship=input_data[4],
            latitude=input_data[5],
            longitude=input_data[6],
        )


def populate_monument_db_table() -> None:
    """Populates data for the monuments table.

    Returns:
        None
    """
    csv_db_path = get_static_dir() + "monuments.csv"
    df_data = pd.read_csv(csv_db_path, dtype=object)
    df_size = len(df_data.index)
    for number in range(df_size):
        input_data = tuple(df_data.iloc[number])
        Monument.objects.create(
            library_id=input_data[0],
            security_form=input_data[1],
            location_accuracy=input_data[2],
            name=input_data[3],
            chronology_date=input_data[4],
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
            longitude=input_data[15],
            chronology=input_data[16],
        )


class GeoObjectsSupport:
    """Class with static method for supporting geographical object functionalities."""

    MAPPER = {
        "doliny": ["dolina", "jar", "wąwóz", "wąwozy", "rów", "obniżenie", "zagłębienie"],
        "bagna": ["bagna/błota", "bagno/błoto", "torfowiska", "torfowisko"],
        "cyrki": ["cyrk lodowcowy"],
        "gory": ["góry", "góra/szczyt", "wzgórze/wzniesienie", "wzgórza/wzniesienia", "zbocze/stok", "pasmo górskie"],
        "groble": ["grobla", "śluza"],
        "jaskinie": ["jaskinia/grota", "bagno/błoto", "torfowiska", "torfowisko"],
        "jeziora": ["jezioro", "jeziora", "staw", "stawy", "sztuczny zbiornik wodny"],
        "lasy": ["las", "lasy", "część lasu"],
        "mosty": ["most"],
        "parki": ["park"],
        "wydmy": ["wydma", "wydmy", "obszar piasków"],
        "wyspy": ["półwysep", "wyspa", "zatoka"],
        "regiony": ["region naturalny"],
        "rzeki": ["rzeka", "potok", "struga", "strumień", "kanał"],
        "skaly": ["skała", "skały", "głaz", "głazy"],
        "starorzecza": ["starorzecze", "stare koryto"],
        "uroczyska": ["uroczysko", "uroczysko/dawna miejscowość"],
        "wodospady": ["wodospad", "wodospady"],
    }

    MAPPER_ALL = []
    for mapped_list in MAPPER.values():
        MAPPER_ALL += mapped_list

    @staticmethod
    def get_query_params(post_data: QueryDict) -> dict:
        """Parse monument query POST request

        Returns:
            Dictionary with parsed monument query.
        """
        query_params = {
            "parish__icontains": post_data.get("parish"),
            "county__icontains": post_data.get("county"),
            "voivodeship__icontains": post_data.get("voivodeship"),
            "quantity": post_data.get("quantity"),
            "nature_objects": post_data.get("nature_objects"),
        }
        return {key: value for key, value in query_params.items() if value}

    @staticmethod
    def randomize(quantity: int, geo_objects: QuerySet[GeographicalObject]) -> list[GeographicalObject]:
        """Randomize queried geographical objects

        Args:
            quantity: quantity limit
            geo_objects: geographical objects selection

        Returns:
            List with randomized geographical objects.
        """
        geo_objects_len = len(geo_objects)
        if quantity > geo_objects_len:
            return [geo_item for geo_item in geo_objects]

        randomized_geo_objects = []
        random_numbers = []
        for num in range(quantity):
            random_number = randbelow(geo_objects_len)
            while random_number in random_numbers:
                random_number = randbelow(geo_objects_len)

            random_geo_object = geo_objects[random_number]
            randomized_geo_objects.append(random_geo_object)
            random_numbers.append(random_number)

        return randomized_geo_objects


class MonumentsSupport:
    """Class with static method for supporting monuments functionalities."""

    @staticmethod
    def get_monument_query_params(post_data: QueryDict) -> dict:
        """Parse monument query POST request

        Returns:
            Dictionary with parsed monument query/
        """
        query_params = {
            "locality__icontains": post_data.get("locality"),
            "parish__icontains": post_data.get("parish"),
            "county__icontains": post_data.get("county"),
            "voivodeship__icontains": post_data.get("voivodeship"),
            "function__icontains": post_data.get("function"),
            "chronology": post_data.get("chronology"),
            "quantity": post_data.get("quantity"),
            "is_archeological": post_data.get("is_archeological"),
        }
        return {key: value for key, value in query_params.items() if value}

    @staticmethod
    def randomize_monuments(quantity: int, monuments: QuerySet[Monument | ArcheologicalMonument]) -> list[Monument]:
        """Randomize queried monuments

        Because of the method always different monuments are queried.

        Returns:
            List with randomized monuments.
        """
        monuments_len = len(monuments)
        if quantity > monuments_len:
            return [monument for monument in monuments]

        randomized_monuments = []
        random_numbers = []
        for num in range(quantity):
            random_number = randbelow(monuments_len)
            while random_number in random_numbers:
                random_number = randbelow(monuments_len)

            random_monument = monuments[random_number]
            randomized_monuments.append(random_monument)
            random_numbers.append(random_number)

        return randomized_monuments


class TripGenerator:
    """Class for generating a trip.

    Args:
        quantity (int): Size of the trip.
        monuments (list[Monument]): Base list of monuments.

    Attributes:
        QUANTITY_LIMIT (int): Limit for trip generation.
        __quantity (int): Size of the trip.
        __monuments (list[Monument]): Base list of monuments.
    """

    QUANTITY_LIMIT = 10

    def __init__(self, quantity: int, monuments: list[Monument]):
        self.__monuments = monuments
        if quantity > self.QUANTITY_LIMIT:
            self.__quantity = 10
        elif quantity > len(monuments):
            self.__quantity = len(monuments)
        else:
            self.__quantity = quantity

    def generate_trip(self) -> list[Monument]:
        """Generates trip.

        Returns:
            List with monuments for the trip.
        """
        return self.__sort_monuments()

    def __sort_monuments(self) -> list[Monument]:
        """Sort list of monuments.

        Sorting is handled by the 'MonumentItem' functionalities.

        Returns:
            List of sorted monuments for the trip.
        """
        monument_items = []
        for monument in self.__monuments:
            latitude = monument.latitude
            longitude = monument.longitude
            monument_item = MonumentItem(data=monument, latitude=latitude, longitude=longitude)
            monument_items.append(monument_item)

        monument_items.sort()
        return [monument_item.monument for monument_item in monument_items]


class MonumentItem:
    """Class for representing monuments and solving sorting issue.

    Args:
        data (Monument): Monument from the 'Monument' model class.
        latitude (str): Latitude of the monument.
        longitude (str): Longitude of the monument.

    Attributes:
        __data (Monument): Monument object (from the 'Monument' model class).
        __latitude (float): Latitude of the monument.
        __longitude (float): Longitude of the monument.
        __reference_measure (float): Calculated reference measure.
    """

    def __init__(self, data: Monument, latitude: str, longitude: str):
        self.__data = data
        self.__latitude = float(latitude)
        self.__longitude = float(longitude)
        self.__reference_measure = self.calc_reference_measure()

    @property
    def monument(self):
        """Provides monument object (from the 'Monument' model class).

        Returns:
            Monument object (from the 'Monument' model class).
        """
        return self.__data

    @property
    def reference_measure(self):
        """Provides calculated reference measure.

        Returns:
            Calculated reference measure.
        """
        return self.__reference_measure

    def calc_reference_measure(self) -> float:
        """Provides calculated reference measure.

        Returns:
            Calculated reference measure (float).
        """
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
class GusApiDbwClient:
    """Delivers client functionalities for GUS DBW API

    Documentation: https://api-dbw.stat.gov.pl/apidocs/index.html

    Attributes:
        DBW_LOGGER (logging.Logger): Dedicated logger object for the DBW API.
        GUS_DBW_API_KEY (str): DBW API key.
        REQUEST_HEADERS (float): Setuped request headers.
    """

    DBW_LOGGER = configure_logger(logger_name="dbw")

    GUS_DBW_API_KEY = getenv("GUS_DBW_API_KEY")
    REQUEST_HEADERS = {"accept": "application/json", "X-ClientId": GUS_DBW_API_KEY}

    @classmethod
    def get_dbw_root_fields(cls) -> list[dict]:
        """Delivers Base Knowledge Fields from.

        Returns:
            List with Base Knowledge Fields data dictionaries.
            For example:
                [{"field_id":727, "field_name": "Gospodarka"}, ...]

            If there was no 200 response code then empty list is returned.
        """
        url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/area/area-area?lang=pl"
        cls.DBW_LOGGER.info("Zostaną pobrane podstawowe dziedziny wiedzy.")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
        cls.DBW_LOGGER.info(
            f"Wykonano zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}). "
            f"Zwrócony kod odpowiedzi: {response.status_code}."
        )
        if response.status_code == 200:
            root_fields = [
                {"field_id": field_data.get("id"), "field_name": field_data.get("nazwa").replace("/", "-")}
                for field_data in response.json()
                if field_data.get("id-nadrzedny-element") is None
            ]
            cls.DBW_LOGGER.debug(f"Odszukano podstawowe dziedziny wiedzy ({root_fields}).")
            return root_fields

        else:
            cls.DBW_LOGGER.error("Nieudane zapytanie, zostanie zwrócona pusta lista bez podstawowych dziedzin wiedzy.")
            return []

    @classmethod
    def get_dbw_fields(cls, field_id: int, field_name: str) -> list[dict]:
        """Delivers Knowledge Fields categories.

        Args:
            field_id: Knowledge field id.
            field_name: Knowledge field category name.

        Returns:
            List with Knowledge Fields category data grouped in dictionaries.
            For example:
                [{"field_id":1, "field_name": "Ceny", "field_variables": False}, ...]

            If there was no 200 response code then empty list is returned.
        """
        url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/area/area-area?lang=pl"
        cls.DBW_LOGGER.info(f"Zostaną wyszukane podkategorie dziedzin wiedzy dla: {field_name} (field_id={field_id}).")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
        cls.DBW_LOGGER.info(
            f"Wykonano zapytanie pobierające wszystkie dziedziny wiedzy ({url_request}). "
            f"Zwrócony kod odpowiedzi: {response.status_code}."
        )

        if response.status_code == 200:
            fields = [
                {
                    "field_id": field_data.get("id"),
                    "field_name": field_data.get("nazwa").replace("/", "-"),
                    "field_variables": field_data.get("czy-zmienne"),
                }
                for field_data in response.json()
                if field_data.get("id-nadrzedny-element") == field_id
            ]
            cls.DBW_LOGGER.info(
                f"Odszukano podkategorie dziedzin wiedzy dla: {field_name} (field_id={field_id}). "
                f"Znaleziono: {fields}."
            )
            return fields

        else:
            cls.DBW_LOGGER.error("Nieudane zapytanie, zostanie zwrócona pusta lista bez podkategorii dziedzin wiedzy.")
            return []

    @classmethod
    def get_dbw_field_variables(cls, field_id: int, field_name: str) -> list[dict]:
        """ " Delivers Knowledge Fields category variables.

        Args:
            field_id: Knowledge field id.
            field_name: Knowledge field category name.

        Returns:
            List with Knowledge Fields category variables data grouped in dictionaries.
            For example:
                [{
                "field_id":3, "field_variable_id": 313,
                "field_variable_name": "Ceny producentów wyrobów spożywczych"}, ...]

            If there was no 200 response code then most probably category doesn't have statistical variables.
            Empty list is returned.
        """
        url_request = f"https://api-dbw.stat.gov.pl/api/1.1.0/area/area-variable?id-obszaru={field_id}&lang=pl"
        cls.DBW_LOGGER.info(f"Zostaną wyszukane zmienne dla {field_name!r} (field_id={field_id}).")
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające zmienne dla {field_name!r} ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
        cls.DBW_LOGGER.info(
            f"Wykonano zapytanie pobierające zmienne dla {field_name!r} ({url_request}). "
            f"Zwrócony kod odpowiedzi: {response.status_code}."
        )

        if response.status_code == 200:
            field_variables = [
                {
                    "field_id": field_data.get("id"),
                    "field_variable_id": field_data.get("id-zmienna"),
                    "field_variable_name": field_data.get("nazwa-zmienna").replace("/", "-"),
                }
                for field_data in response.json()
            ]
            cls.DBW_LOGGER.info(
                f"Wyszukano zmienne dla: {field_name!r} (field_id={field_id}). " f"Znaleziono: {field_variables}."
            )

            return field_variables

        elif response.status_code == 404:
            cls.DBW_LOGGER.info(
                f"Dany obszar najprawdopodobniej nie posiada zmiennych statystycznych, zostanie "
                f"zwrócona pusta lista bez zmiennych (wyszukiwanie dla {field_name!r})."
            )
            return []

        else:
            cls.DBW_LOGGER.error(
                f"Nieudane zapytanie, zostanie zwrócona pusta lista bez zmiennych (wyszukiwanych dla "
                f"{field_name!r})."
            )
            return []

    @classmethod
    def get_variable_section_periods(cls, field_variable_id: int, field_variable_name: str) -> list[dict]:
        """ " Delivers sections and periods for the given variable.

        Args:
            field_variable_id: Variable id.
            field_variable_name: Variable name.

        Returns:
            List with Knowledge Fields category variable - sections and periods - data grouped in dictionaries.
            For example:
                [...
                    {
                        "id-zmienna": 1679,
                        "nazwa-zmienna": "Wysokie Koszty, Niskie Dochody - wska\u017anik",
                        "id-przekroj": 2,
                        "nazwa-przekroj": "Polska, wojew\u00f3dztwa",
                        "id-okres": 282
                    },
                ...]
        """
        section_periods = []
        responses_data = []
        filename_path = "static/all_section_periods.json"
        url_request1 = (
            "https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-periods?"
            "ile-na-stronie=5000&numer-strony=0&lang=pl"
        )
        url_request2 = (
            "https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-periods?"
            "ile-na-stronie=5000&numer-strony=1&lang=pl"
        )

        if exists(filename_path) and getsize(filename_path):
            cls.DBW_LOGGER.debug(
                f"Plik {filename_path!r} jest już na dysku, więc zostanie wykorzystany przy ustalaniu "
                f"przekrojów i okresów dla zmiennej {field_variable_name!r}."
            )
            with open(filename_path, "r", encoding="utf-8") as json_file:
                responses_data = json.load(json_file)

        else:
            cls.DBW_LOGGER.debug(
                f"Pliku {filename_path!r} nie ma jeszcze na dysku, więc wszystkie przekroje i okresy "
                f"zostaną wczytane z DBW API."
            )

            cls.DBW_LOGGER.info(
                f"Zostaną pobrane wszystkie przekroje/okresy z DBW API. "
                f"Wykonane będą dwa zapytania (1: {url_request1}, 2: {url_request2})."
            )

            response1 = requests.get(url_request1, headers=cls.REQUEST_HEADERS, timeout=60)

            cls.DBW_LOGGER.info(
                f"Wykonano zapytanie pobierające przekroje/okresy z DBW API ({url_request1}). "
                f"Zwrócony kod odpowiedzi: {response1.status_code}."
            )
            if response1.status_code == 200:
                responses_data = response1.json()["data"]
            response2 = requests.get(url_request2, headers=cls.REQUEST_HEADERS, timeout=60)
            cls.DBW_LOGGER.info(
                f"Wykonano zapytanie pobierające przekroje/okresy z DBW API ({url_request2}). "
                f"Zwrócony kod odpowiedzi: {response2.status_code}."
            )
            if response2.status_code == 200:
                responses_data += response2.json()["data"]

            with open(filename_path, "w", encoding="utf-8") as json_file:
                json.dump(responses_data, json_file, indent=4)
                cls.DBW_LOGGER.info(f"Zapisano wszystkie przekroje/okresy do pliku {filename_path!r}.")

        cls.DBW_LOGGER.info(f"Ustalenie przekrojów i okresów dla zmiennej {field_variable_name!r}.")
        for item in responses_data:
            if item.get("id-zmienna") == field_variable_id:
                section_periods.append(item)

        cls.DBW_LOGGER.info(f"Ustalono przekroje i okresy dla zmiennej {field_variable_name!r} ({section_periods}).")

        return section_periods

    @classmethod
    def get_periods(cls) -> list[dict]:
        """Delivers all periods data.

        Returns:
            List with all periods data, grouped in dictionaries.
            For example:
                [...
                    "id-okres": 247,
                    "symbol": "M01",
                    "opis": "miesi\u0105c - dane miesi\u0119czne - stycze\u0144",
                    "id-czestotliwosc": 3,
                    "nazwa-czestotliwosc": "Miesi\u0105c",
                    "id-typ": 1,
                    "nazwa-typ": "dane miesi\u0119czne"
                },
                ...]
        """
        filename_path = "static/all_periods.json"

        if exists(filename_path) and getsize(filename_path):
            cls.DBW_LOGGER.debug(f"Plik {filename_path!r} jest już na dysku, więc zostanie wykorzystany. ")
            with open(filename_path, "r", encoding="utf-8") as json_file:
                periods = json.load(json_file)
                cls.DBW_LOGGER.info(
                    f"Wczytano wszystkie okresy z pliku {filename_path!r}. "
                    f"(Liczba okresów: {len(periods)}). Zostaną dalej wykorzystane."
                )
                return periods

        else:
            cls.DBW_LOGGER.debug(
                f"Pliku {filename_path!r} nie ma jeszcze na dysku, więc wszystkie okresy "
                f" zostaną wczytane z DBW API."
            )
            url_request = "https://api-dbw.stat.gov.pl/api/1.1.0/dictionaries/periods-dictionary"
            response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
            periods = response.json()["data"]
            with open(filename_path, "w", encoding="utf-8") as json_file:
                json.dump(periods, json_file, indent=4)
                cls.DBW_LOGGER.info(
                    f"Zapisano wszystkie okresy do pliku {filename_path!r}. "
                    f"(Liczba okresów: {len(periods)}). Zostaną dalej wykorzystane."
                )
            return periods

    @classmethod
    def get_stats_data(cls, field_variable_id: int, section_id: int, period_id: int, year_id: int) -> list[dict]:
        """Delivers stats data for the given query.

        Args:
            field_variable_id: Variable id.
            section_id: Section id.
            period_id: Period id.
            year_id: Year number.

        Returns:
            List with Knowledge Fields category variable - sections and periods - data grouped in dictionaries.
            For example:
            [{
                'rownumber': 1, 'id-zmienna': 313, 'id-przekroj': 655, 'id-wymiar-1': 2, 'id-pozycja-1': 33617,
                'id-wymiar-2': 490, 'id-pozycja-2': 7289157000018, 'id-okres': 247, 'id-sposob-prezentacji-miara': 180,
                'id-daty': 2024, 'id-brak-wartosci': 253, 'id-tajnosci': 43, 'id-flaga': 36, 'wartosc': 8.53,
                'precyzja': 2}, ...
            ]

            If there was no 200 response code then most probably stats data don't exist for the such query.
            Then empty list is returned.
        """
        url_request = (
            f"https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-data-section?"
            f"id-zmienna={field_variable_id}&"
            f"id-przekroj={section_id}&"
            f"id-rok={year_id}&"
            f"id-okres={period_id}&"
            f"ile-na-stronie=5000&numer-strony=0&lang=pl"
        )
        cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające dane statystyczne ({url_request}).")
        response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
        cls.DBW_LOGGER.info(
            f"Wykonano zapytanie pobierające dane statystyczne ({url_request}). "
            f"Zwrócony kod odpowiedzi: {response.status_code}."
        )

        if response.status_code == 200:
            stats_data = response.json()["data"]
            cls.DBW_LOGGER.info(f"Pobrane dane statystyczne ({url_request}): {stats_data}.")
            return stats_data

        cls.DBW_LOGGER.info(
            "Dany obszar najprawdopodobniej nie posiada danych statystycznych, "
            "zostanie zwrócona pusta lista bez danych."
        )
        return []

    @classmethod
    def get_dimension_description(
        cls, section_id: int, dimension_id: int, dimension_position_id: int, section_dimensions: list
    ) -> str:
        """Delivers dimension description for the given query.

        Args:
            section_id: Section id.
            dimension_id: Dimension id.
            dimension_position_id: Dimension position id.
            section_dimensions: List with all dimensions data for the given section, grouped in dictionaries.

        Returns:
            Text with dimension description built as below:
             - dim.get('nazwa-wymiar') / dim.get('nazwa-pozycja')
             For example:
             - 'Wyroby spożywcze / Cukier biały kryształ, workowany [kg]'

            If there was no 200 response code then empty string is returned.
        """
        if not dimension_id or not dimension_position_id:
            err_message = (
                "Zmienne dimension_id i dimension_position_id muszą mieć niezerową wartość typu integer "
                "przy ustalaniu opisu wymiaru."
            )
            cls.DBW_LOGGER.error(err_message)
            raise ValueError(err_message)

        cls.DBW_LOGGER.info(
            f"Nastąpi ustalanie opisu dla wymiaru '{dimension_id}' "
            f"(id pozycji: {dimension_position_id}, id przekroju: {section_id})."
        )

        for dim in section_dimensions:
            if dim.get("id-pozycja") == dimension_position_id:
                dim_description = f"{dim.get('nazwa-wymiar')} / {dim.get('nazwa-pozycja')}"
                cls.DBW_LOGGER.info(
                    f"Ustalono opis wymiaru dla '{dimension_id}' "
                    f"(id pozycji: {dimension_position_id}): {dim_description!r}."
                )
                return dim_description
        else:
            cls.DBW_LOGGER.info(
                f"Nie ustalono opisu wymiaru dla '{dimension_id}' "
                f"(id pozycji: {dimension_position_id}). Zostanie zwrócony pusty string."
            )
            return ""

    @classmethod
    def get_representation_description(cls, representation_id) -> str:
        filename_path = "static/all_representation_measures.json"
        representation_measures = []

        cls.DBW_LOGGER.info(f"Nastąpi ustalenie opisu dla miary (id miary: '{representation_id}').")

        if exists(filename_path) and getsize(filename_path):
            cls.DBW_LOGGER.debug(
                f"Plik {filename_path!r} jest już na dysku, więc zostanie wykorzystany przy ustalaniu "
                f"opisu dla miary (id miary: {representation_id!r})."
            )
            with open(filename_path, "r", encoding="utf-8") as json_file:
                representation_measures = json.load(json_file)
        else:

            url_request = (
                "https://api-dbw.stat.gov.pl/api/1.1.0/dictionaries/way-of-presentation?page=1&page-size=5000&lang=pl"
            )
            cls.DBW_LOGGER.debug(f"Zostanie wykonane zapytanie pobierające dane opisu miar ({url_request}).")
            response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
            cls.DBW_LOGGER.info(
                f"Wykonano zapytanie pobierające wszystkie dane opisujące miary ({url_request}). "
                f"Zwrócony kod odpowiedzi: {response.status_code}."
            )
            if response.status_code == 200:
                representation_measures = response.json()["data"]
                cls.DBW_LOGGER.info(f"Pobrane dane opisu miar: {representation_measures}.")

            with open(filename_path, "w", encoding="utf-8") as json_file:
                json.dump(representation_measures, json_file, indent=4)
                cls.DBW_LOGGER.info(
                    f"Zapisano wszystkie dane opisujące miary do pliku {filename_path!r}. "
                    f"(Liczba elementów: {len(representation_measures)}). Zostaną dalej wykorzystane."
                )

        for representation in representation_measures:
            if representation.get("id-sposob-prezentacji-miara") == representation_id:
                measure_name = representation.get("nazwa")
                cls.DBW_LOGGER.info(f"Ustalono nazwę miary dla id miary {representation_id!r} => {measure_name!r}.")
                return measure_name

        return ""

    @classmethod
    def get_section_dimensions(cls, section_id: int) -> list[dict]:
        """Delivers dimensions data for the given section.

        Args:
            section_id: Section id.

        Returns:
            List with all dimensions data for the given section, grouped in dictionaries.
            For example:
                [
                {'id-przekroj': 485, 'id-wymiar': 10, 'nazwa-wymiar': 'Polska, województwa, powiaty',
                'id-pozycja': 33617, 'nazwa-pozycja': 'POLSKA'}, ...
                ]
            If there was no 200 response code then empty list is returned.
        """
        cls.DBW_LOGGER.debug(
            f"Zostanie wykonane zapytanie pobierające wszystkie dane wymiarów dla przekroju {section_id!r}."
        )
        url_request = (
            f"https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-position?"
            f"id-przekroj={section_id}&lang=pl"
        )

        response = requests.get(url_request, headers=cls.REQUEST_HEADERS, timeout=60)
        cls.DBW_LOGGER.info(
            f"Wykonano zapytanie pobierające dane wymiarów dla przekroju '{section_id}'. "
            f"Zwrócony kod odpowiedzi: {response.status_code}."
        )
        if response.status_code == 200:
            dimensions = response.json()
            cls.DBW_LOGGER.debug(f"Pobrane dane wymiarów przekroju {section_id!r}: ({dimensions}).")
            return dimensions

        cls.DBW_LOGGER.error(
            f"Nieudane zapytanie - pobierające wszystkie dane wymiarów dla przekroju {section_id!r} - "
            f"zostanie zwrócona pusta lista."
        )
        return []


class PressNewsItem:
    """Class for representing press news.

    Args:
        link (str): Link of press news.
        publisher (str): Publisher of press news.
        title (str): Title of press news.
        when (str): Time of press news.
        minutes (int): Time day converted to number of minutes (for sorting).

    Attributes:
        link (str): Link of press news.
        publisher (str): Publisher of press news.
        publisher_nick (str): Publisher nick of press news.
        title (str): Title of press news.
        when (str): Time of press news.
        minutes (int): Time day converted to number of minutes (for sorting).
    """

    def __init__(self, link: str, publisher: str, publisher_nick: str, title: str, when: str, minutes: int):
        self.link = link
        self.publisher = publisher
        self.publisher_nick = publisher_nick
        self.title = title
        self.when = when
        self.minutes = minutes


def collect_press_news() -> list[PressNewsItem]:
    """
    Args:
        publisher (str or None): Publisher of press news.

    Returns:
        List with PressNewsItem objects
    """
    publisher_rss_channel = {
        "Polsat": ["polsat", "https://www.polsatnews.pl/rss/polska.xml"],
        "Onet": ["onet", "https://wiadomosci.onet.pl/.feed"],
        "WP": ["wp", "https://wiadomosci.wp.pl/rss.xml"],
        # "Bankier.pl": ["bankier", "https://www.bankier.pl/rss/wiadomosci.xml"],
        # "Business Insider": ["businessinsider", "https://businessinsider.com.pl/.feed"],
        "tvn24": ["tvn24", "https://tvn24.pl/wiadomosci-z-kraju,3.xml"],
        "Interia": ["interia", "http://fakty.interia.pl/polska/feed"],
        # "rmf24": ["rmf24", "http://www.rmf24.pl/fakty/feed fakty"],
        "tvpinfo": ["tvpinfo", "https://tvp.info/tvp.info/rss+xml.php"],
    }

    press_news = []

    for media, media_data in publisher_rss_channel.items():
        try:
            rss_feed = feedparser.parse(media_data[1].replace(" ", "%20"))
        except Exception as e:
            print("Error dla:", media, e)
            continue
        for entry in rss_feed.entries:

            time = entry.published_parsed
            today = date.today()
            if time.tm_mday != today.day or time.tm_mon != today.month:
                continue

            if len(str(time.tm_min)) == 1:
                time_ = f"{time.tm_hour+1}:0{time.tm_min}"
            else:
                time_ = f"{time.tm_hour+1}:{time.tm_min}"

            total_minutes = 60 * (time.tm_hour + 1) + time.tm_min

            if media == "tvpinfo":
                print(entry)

            news = PressNewsItem(
                link=entry.link,
                publisher=media,
                publisher_nick=media_data[0],
                title=entry.title,
                when=time_,
                minutes=total_minutes,
            )
            press_news.append(news)

    press_news.sort(key=lambda x: x.minutes, reverse=True)

    return press_news


class CeidgVoivodeshipClient:
    """Class with functionalities for downloading data from Ceidg per Voivodeship,

    Args:
        voivodeship (str): Voivodeship.

    Attributes:
        CEIDG_API_KEY (str): Limit for trip generation.
        __voivodeship (str): Voivodeship.
        __page_number (int): Result page to be processed.
    """

    CEIDG_API_KEY = f'Bearer {getenv("CEIDG_API_KEY")}'
    REQUEST_HEADERS = {"accept": "application/json", "Authorization": CEIDG_API_KEY}
    voivodeships = [
        "dolnośląskie",
        "kujawsko-pomorskie",
        "lubelskie",
        "lubuskie",
        "łódzkie",
        "małopolskie",
        "mazowieckie",
        "opolskie",
        "podkarpackie",
        "podlaskie",
        "pomorskie",
        "śląskie",
        "świętokrzyskie",
        "warmińsko-mazurskie",
        "wielkopolskie",
        "zachodniopomorskie",
    ]

    def __init__(self, voivodeship: str):
        if voivodeship not in self.voivodeships:
            raise ValueError(
                "Województwo musi byc odpowiednią wartość ze zbioru województw.",
                voivodeship,
                "nie jest taką wartością.",
            )
        self.__voivodeship = voivodeship
        self.__page_number = 0
        self.__last_process_succeed = False

    def get_inital_request(self) -> dict:
        url = f"https://dane.biznes.gov.pl/api/ceidg/v2/firmy?wojewodztwo={self.__voivodeship}&limit=25"
        response = requests.get(url, headers=self.REQUEST_HEADERS, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            print("To nie zadziałało dla:", self.__voivodeship, "Zapytanie zwróciło:", response.status_code)
            return {}

    def update_page_number(self):
        self.__last_process_succeed = True
        self.__page_number += 1


def run_all_voivodeships():
    c = CeidgVoivodeshipClient("dolnośląskie")

    for voivodeship in c.voivodeships:
        cx = CeidgVoivodeshipClient(voivodeship)
        data = cx.get_inital_request()
        # print(data)
        # print(data.get("links"))
        num_of_companies = data.get("count")
        print(num_of_companies, "-", voivodeship)
