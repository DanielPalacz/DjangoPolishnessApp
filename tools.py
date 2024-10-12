from polishness.models import Monument
import pandas as pd
from os.path import dirname

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
