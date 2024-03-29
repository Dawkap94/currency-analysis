import os
import csv
import datetime
import json
import matplotlib.pyplot as plt
import requests
from statistics import mean
from typing import Dict
from fpdf import FPDF


class UrlConstructor:
    def __init__(self, currency, year_since):
        self.year_since = year_since
        self.currency = currency
        self.base = "http://api.nbp.pl/api"

    def generate_url(self, currency):
        if self.currency.upper() == "GOLD":
            link = self.base + f"/cenyzlota/{self.year_since}-01-01/{int(self.year_since) + 1}-01-01/?format=json"
            return link
        else:
            link = self.base + f"/exchangerates/rates/a/{currency}/{self.year_since}-01-01/{int(self.year_since) + 1}-01-01/?format=json"
            return link


class GetData:
    def __init__(self, url, type_data):
        self.url = url
        self.type_data = type_data

    def download_data(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            print("Error. Try another time.")
            return
        if self.type_data == "json" or self.type_data == "txt" or self.type_data == "csv" or self.type_data == "pdf":
            web_dict = r.json()
            return web_dict

    def parse_data(self, data) -> Dict:
        pass

    def numbers_to_month(self, data):
        self.data = data
        new_dict = {}

        for months, values in self.data.items():
            month_number = int(months)
            new_month = datetime.date(1900, month_number, 1).strftime('%B')
            new_dict[new_month] = values
        return new_dict


class GetDataMoney(GetData):
    def __init__(self, url, type_data):
        super().__init__(url, type_data)

    def parse_data(self, web_dict) -> Dict:
        self.web_dict = web_dict
        currency_dict = {}
        start_month = 1
        avg_day_list = []
        for elem in self.web_dict["rates"]:
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
        return GetData.numbers_to_month(self, currency_dict)


class GetDataGold(GetData):
    def __init__(self, url, type_data):
        super().__init__(url, type_data)

    def parse_data(self, web_dict) -> Dict:
        self.web_dict = web_dict
        gold_dict = {}
        start_month = 1
        avg_day_list = []

        for elem in web_dict:
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
        return GetData.numbers_to_month(self, gold_dict)


class ReportDataBase:
    def __init__(self, data_to_save: Dict, suffix):
        self.data_to_save = data_to_save
        self.suffix = suffix

    def create_report(self):
        if self.suffix == "json":
            with open(f"Report file.{self.suffix}", "w") as currency_file:
                json.dump(self.data_to_save, currency_file)
        elif self.suffix == "txt":
            with open(f"Report file.{self.suffix}", "w") as currency_file:
                currency_file.write(str(self.data_to_save))
        print("Saved to Report file.")
        if self.suffix == "csv":
            with open(f"Report file.{self.suffix}", "w") as currency_file:
                file = csv.writer(currency_file)
                for key, value in self.data_to_save.items():
                    file.writerow([key, value])


class PDFReportData(ReportDataBase):
    def __init__(self, data_to_save, suffix):
        super().__init__(data_to_save, suffix)

    def create_graph(self, currency):
        self.currency = currency
        value = [val for val in self.data_to_save.values()]
        months = [keys[0:3] for keys in self.data_to_save.keys()]
        plt.title(f"Price chart for {currency.upper()}")
        plt.plot(months, value)
        plt.savefig(f"Graph_to_report.png")

    def create_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        for keys, values in self.data_to_save.items():
            pdf.cell(200, 10, txt=f"In {keys}, the price was {values} PLN",
                     ln=1, align='C')
        pdf.image("Graph_to_report.png", x=0, y=130, w=0, h=0)
        pdf.output(f"Report file.{self.suffix}")
        print("Saved to Report file")
        os.remove("Graph_to_report.png")


def main():
    # Konstrukcja URL
    currency = input("Podaj co chcesz zbadac?")
    year_since = input("Wprowadz rok, ktory chcesz sprawdzic?")
    file_format = input("W jakim formacie zapisac raport? csv/json/txt/pdf: ")

    Url_object = UrlConstructor(currency, year_since)
    Collected_link = Url_object.generate_url(currency)

    # Pobranie odpowiednich danych
    Pobieranie_danych = GetData(Collected_link, file_format)
    Pobrane_dane = GetData.download_data(Pobieranie_danych)

    # GOLD
    if currency.upper() == "GOLD":
        Slownik_gold_object = GetDataGold(Collected_link, file_format)
        Slownik_gotowy = GetDataGold.parse_data(Slownik_gold_object, Pobrane_dane)

        # Slownik_gotowy to gotowy slownik {Miesiac: sredni kurs}

    # WALUTY
    else:
        Slownik_waluty_object = GetDataMoney(Collected_link, file_format)
        Slownik_gotowy = GetDataMoney.parse_data(Slownik_waluty_object, Pobrane_dane)
        # Slownik_gotowy to gotowy slownik {Miesiac: sredni kurs}

    # Zapis do pliku, w przypadu pdf dodany został wykres
    if file_format == "pdf":
        raport_object = PDFReportData(Slownik_gotowy, file_format)
        raport_object.create_graph(currency)
    else:
        raport_object = ReportDataBase(Slownik_gotowy, file_format)

    raport_object.create_report()


if __name__ == '__main__':
    main()
