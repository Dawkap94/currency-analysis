import requests
from datetime import datetime
from statistics import mean


def get_yearly_data(year_since: str, year_to: str, currency: str):
    r = requests.get(
        f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{year_since}-01-01/{year_to}-01-01/?format=json")
    if r.status_code != 200:
        print("Error. Try another time.")
    else:
        web_dict = r.json()
        currency_dict = {}
        start_month = 1
        avg_day_list = []

        for elem in web_dict["rates"]:
            dt = datetime.strptime(elem["effectiveDate"], "%Y-%m-%d")
            if start_month == 1 and dt.month == 1:
                avg_day_list.append(elem["mid"])
                currency_dict["1"] = round(mean(avg_day_list), 3)
            elif start_month == dt.month:
                avg_day_list.append(elem["mid"])
                currency_dict[f"{start_month}"] = round(mean(avg_day_list), 3)
            else:
                avg_day_list = []
                start_month += 1
        return currency_dict


def convert_yearly_data_to_pln(currency_dict):
    try:
        pln_amount = int(input("How many PLN do you have?"))
        pln_dict = currency_dict.copy()
        for keys, values in currency_dict.items():
            pln_dict[f"{keys}"] = round(pln_amount / values, 3)
        return pln_dict
    except ValueError:
        return "Nieprawidlowe dane, wystapil blad"



def save_to_file(data):
    with open("exchange_rate.txt", "w") as currency_file:
        currency_file.write(f"{data}")
    return print("Saved to file exchange rate")


save_to_file(convert_yearly_data_to_pln(get_yearly_data("2013", "2014","usd")))
