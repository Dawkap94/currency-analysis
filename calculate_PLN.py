import requests
import datetime
from statistics import mean
import json


def collect_gold_json(year_since: int):
    r = requests.get(f"http://api.nbp.pl/api/cenyzlota/{str(year_since)}-01-01/{str(year_since+1)}-01-01/?format=json")
    if r.status_code != 200:
        print("Error. Try another time.")
        return
    else:
        web_dict = r.json()
        return web_dict


def get_yearly_data_gold(data_list):
    gold_dict = {}
    start_month = 1
    avg_day_list = []

    for elem in data_list:
        dt = datetime.datetime.strptime(elem["data"], "%Y-%m-%d")
        if start_month == 1 and dt.month == 1:
            avg_day_list.append(elem["cena"])
            gold_dict["1"] = round(mean(avg_day_list), 3)
        elif start_month == dt.month:
            avg_day_list.append(elem["cena"])
            gold_dict[f"{start_month}"] = round(mean(avg_day_list), 3)
        else:
            avg_day_list = []
            start_month += 1
    return gold_dict


def collect_currency_json(year_since: int, currency: str):
    r = requests.get(
        f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{str(year_since)}-01-01/{str(year_since+1)}-01-01/?format=json")
    if r.status_code != 200:
        print("Error. Try another time.")
        return
    else:
        web_dict = r.json()
        return web_dict


def numbers_to_month(date_dict):
    new_dict = {}
    for months, values in date_dict.items():
        month_number = int(months)
        new_month = datetime.date(1900, month_number, 1).strftime('%B')
        new_dict[new_month] = values
    return new_dict


def get_yearly_data_currency(data_dict):
    currency_dict = {}
    start_month = 1
    avg_day_list = []
    for elem in data_dict["rates"]:
        dt = datetime.datetime.strptime(elem["effectiveDate"], "%Y-%m-%d")
        if start_month == 1 and dt.month == 1:
            avg_day_list.append(elem["mid"])
            currency_dict["1"] = round(mean(avg_day_list), 3)
        elif start_month == dt.month:
            avg_day_list.append(elem["mid"])
            currency_dict[f"{start_month}"] = round(mean(avg_day_list), 3)
        else:
            avg_day_list = []
            start_month += 1
    currency_dict = numbers_to_month(currency_dict)
    return currency_dict


def convert_yearly_data_to_pln(currency_dict):
    try:
        pln_amount = int(input("How many PLN do you have?"))
        pln_dict = currency_dict.copy()
        for keys, values in currency_dict.items():
            pln_dict[f"{keys}"] = round(pln_amount / values, 3)
        return pln_dict
    except ValueError:
        return "Invalid data"


def save_to_file(data):
    with open("exchange_rate.json", "w") as currency_file:
        json.dump(data, currency_file)
    print("Saved to file exchange rate")


def main():
    year_since = int(input("Which year to check?"))
    currency = input("Which currency to check?")
    collected_currency_data = collect_currency_json(year_since, currency)
    if collected_currency_data is None:
        print("BLAD")
        return
    yearly_data_currency = get_yearly_data_currency(collected_currency_data)
    converted_data = convert_yearly_data_to_pln(yearly_data_currency)
    saved_data = save_to_file(converted_data)

if __name__ == '__main__':
    main()