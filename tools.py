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

def get_polish_photo_link() -> str:
    unplash_api_key = getenv("UNPLASH_API_KEY")
    url_request = f"https://api.unsplash.com/photos/random?query=poland&client_id={unplash_api_key}&count=1"
    response = requests.get(url_request)
    photo_link = response.json()[0]["urls"]["full"]
    return photo_link

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
