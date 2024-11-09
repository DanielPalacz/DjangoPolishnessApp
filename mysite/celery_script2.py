from __future__ import annotations

from mysite.celery_setup import app
from mysite.celery_tasks import get_krs_company_data

app.tasks.register(get_krs_company_data)

for num in range(1, 2000000):
    # Running tasks synchronously
    result = get_krs_company_data.apply((num,))

    result = result.get()
    # print(result)
    if result is None:
        continue

    result_cleaned = [item.replace(";", ",") for item in result]

    result_str = ";".join(result_cleaned) + "\n"
    with open("krs_company.csv", "a+") as file:
        file.write(result_str)
