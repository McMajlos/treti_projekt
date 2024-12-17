import requests
from bs4 import BeautifulSoup
import argparse
import lxml
import csv

parser = argparse.ArgumentParser(description="Scraping data from 2017 votes.")

parser.add_argument(
    "url",
    type=str,
    help="Insert URL from District - example: 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103'",
)

parser.add_argument(
    "csv_file_name",
    type=str,
    help="Insert a name of output file. Example: 'Okres_Prostejov.csv'",
)

args = parser.parse_args()


url = args.url
csv_file_name = args.csv_file_name


def header_of_csv_file(url, file_name):
    answer = requests.get(url)
    soup = BeautifulSoup(answer.text, "lxml")
    prefix = "https://www.volby.cz/pls/ps2017nss/"
    q = soup.select_one("td", {"class": "cislo", "headers": "t1sa1 t1sb1"})
    link = q.find("a")
    href = link.get("href")
    full_url = prefix + href
    response = requests.get(full_url)
    soup = BeautifulSoup(response.text, "lxml")
    header = ["Code", "Location", "Registered", "Envelopes", "Valid votes"]
    partaje_first_tab = soup.find_all(
        "td", {"class": "overflow_name", "headers": "t1sa1 t1sb2"}
    )
    for partaj in partaje_first_tab:
        header.append(partaj.get_text(strip=True))

    partaje_second_tab = soup.find_all(
        "td", {"class": "overflow_name", "headers": "t2sa1 t2sb2"}
    )
    for partaj in partaje_second_tab:
        header.append(partaj.get_text(strip=True))
    with open(file=file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)


def odkazy(url, file_name):
    answer = requests.get(url)
    soup = BeautifulSoup(answer.text, "lxml")
    odkazy = soup.find_all("td", {"class": "cislo"})
    for td in odkazy:
        prefix = "https://www.volby.cz/pls/ps2017nss/"
        link = td.find("a")
        href = link.get("href")
        full_url = prefix + href
        response = requests.get(full_url)
        # row = []
        for i in td:
            row = []
            soup = BeautifulSoup(response.text, "lxml")
            # code
            kod = response.url.split("obec=")[1].split("&")[0]
            row.append(kod)
            # obec
            location_selector = soup.select("#publikace > h3:nth-child(4)")
            location = (location_selector[0].text).replace("Obec: ", "").strip()
            # print(location)
            row.append(location)
            # registered
            registered = soup.find("td", {"class": "cislo", "headers": "sa2"})
            row.append(registered.get_text(strip=True))
            # given_envelope
            given_envelopes = soup.find("td", {"class": "cislo", "headers": "sa3"})
            row.append(given_envelopes.get_text(strip=True))
            # valid_votes
            valid_votes = soup.find("td", {"class": "cislo", "headers": "sa6"})
            row.append(valid_votes.get_text(strip=True))
            # partaj
            partaj_valid_votes_tab1 = soup.find_all(
                "td", {"class": "cislo", "headers": "t1sa2 t1sb3"}
            )
            for partaj_valid_vote1 in partaj_valid_votes_tab1:
                row.append(partaj_valid_vote1.get_text(strip=True))

            partaj_valid_votes_tab2 = soup.find_all(
                "td", {"class": "cislo", "headers": "t2sa2 t2sb3"}
            )
            for partaj_valid_vote2 in partaj_valid_votes_tab2:
                row.append(partaj_valid_vote2.get_text(strip=True))

        with open(file=file_name, mode="+a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)



print("Starting now")
header_of_csv_file(url, csv_file_name)
odkazy(url, csv_file_name)
print(f"Data scraped, saved in {csv_file_name}")
