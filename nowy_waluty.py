from typing import Dict
import requests
import datetime
from statistics import mean
import json


class UrlConstructor:
    def __init__(self, waluta):
        self.waluta = waluta
        self.base = "http://api.nbp.pl/api"

    def generate_url(self, waluta):
        year_since = input("Wprowadz rok od ktorego chcesz sprawdzic?")
        if self.waluta.upper() == "GOLD":
            URL = self.base + f"/cenyzlota/{year_since}-01-01/{int(year_since) + 1}-01-01/?format=json"
            return URL
        else:
            URL = self.base + f"/exchangerates/rates/a/{waluta}/{year_since}-01-01/{int(year_since) + 1}-01-01/?format=json"
            return URL


class GetData:
    def __init__(self, url, type_data):
        self.url = url
        self.type_data = type_data

    def download_data(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            print("Error. Try another time.")
            return
        if self.type_data == "json":
            web_dict = r.json()
            return web_dict

    def parse_data(self) -> Dict:
        pass


class GetDataMoney:
    def __init__(self, data_dict):
        self.data_dict = data_dict

    def numbers_to_month(self, data_dict):
        self.data_dict = data_dict
        new_dict = {}

        for months, values in self.data_dict.items():
            month_number = int(months)
            new_month = datetime.date(1900, month_number, 1).strftime('%B')
            new_dict[new_month] = values
        return new_dict

    def parse_data(self, data_dict) -> Dict:
        self.data_dict = data_dict
        currency_dict = {}
        start_month = 1
        avg_day_list = []
        for elem in self.data_dict["rates"]:
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
        currency_dict = GetDataMoney.numbers_to_month(self, currency_dict)
        return currency_dict


class GetDataGold:
    def __init__(self, data_list):
        self.data_list = data_list

    def numbers_to_month(self, data_list):
        self.data_list = data_list
        new_dict = {}

        for months, values in self.data_list.items():
            month_number = int(months)
            new_month = datetime.date(1900, month_number, 1).strftime('%B')
            new_dict[new_month] = values
        return new_dict

    def parse_data(self, data_list) -> Dict:
        self.data_list = data_list
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
        gold_dict = GetDataGold.numbers_to_month(self, gold_dict)
        return gold_dict


class ReportDataBase:
    def __init__(self, data_to_save: Dict, suffix):
        self.data_to_save = data_to_save
        self.suffix = suffix

    def create_report(self):
        with open(f"{self.suffix}.json", "w") as currency_file:
            json.dump(self.data_to_save, currency_file)
        print("Zapisano do pliku.")


class PDFReportData(ReportDataBase):
    pass


def main():
    # Konstrukcja URL
    waluta = input("Podaj co chcesz zbadac?")
    url = UrlConstructor(waluta)
    URL = url.generate_url(waluta)

    # Pobranie odpowiednich danych
    pobranie_danych = GetData(URL, "json")
    duzy_slownik = pobranie_danych.download_data()

    # Obróbka danych
    if waluta.upper() == "GOLD":
        maly_slownik_gold = GetDataGold(duzy_slownik)
        slownik_miesieczny_gold = maly_slownik_gold.parse_data(duzy_slownik)
        wynik_gold = slownik_miesieczny_gold
        dane_do_pliku = ReportDataBase(wynik_gold, "Plik json z walutami")
        dane_do_pliku.create_report()
    else:
        maly_slownik_waluty = GetDataMoney(duzy_slownik)
        slownik_miesieczny_waluty = maly_slownik_waluty.parse_data(duzy_slownik)
        wynik_waluty = slownik_miesieczny_waluty

        #Zapis do pliku
        dane_do_pliku = ReportDataBase(wynik_waluty, "Raport JSON")
        dane_do_pliku.create_report()


if __name__ == '__main__':
    main()


    # json, csv, txt
