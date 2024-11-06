from __future__ import annotations

from mysite.celery_setup import app
from mysite.celery_tasks import get_krs_foundation_data

app.tasks.register(get_krs_foundation_data)


for num in range(100, 1000000):
    # Synchronically running tasks
    result = get_krs_foundation_data.apply((num,))

    # Status
    # print("Status:", result.status)

    result = result.get()
    print(result)
    if result is None:
        print("Brak danych dla nr krs:", num)
        continue

    result_str = ";".join(result) + "\n"
    with open("krs_foundations.csv", "a+") as file:
        file.write(result_str)
