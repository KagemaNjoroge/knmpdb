import csv
import json
import random
from faker import Faker
from core.models import MissingPersonContact, MissingPerson

fake = Faker()


def insert_test_lost_persons(count=200):
    """
    Utility script to insert test lost persons into the database.
    """

    with open(
        "static/data/counties-constituencies-wards.json", "r", encoding="utf-8"
    ) as f:
        """
            {
        "MOMBASA": {
            "CHANGAMWE": [
                "PORT REITZ",
                "KIPEVU",
                "AIRPORT",
                "CHANGAMWE",
                "CHAANI"
            ],
            "JOMVU": [
                "JOMVU KUU",
                "MIRITINI",
                "MIKINDANI"
            ],
            "KISAUNI": [
                "MJAMBERE",
                "JUNDA",
                "BAMBURI",
                "MWAKIRUNGE",
                "MTOPANGA",
                "MAGOGONI",
                "SHANZU"
            ],
            "NYALI": [
                "FRERE TOWN",
                "ZIWA LA NG'OMBE",
                "MKOMANI",
                "KONGOWEA",
                "KADZANDANI"
            ],
            "LIKONI": [
                "MTONGWE",
                "SHIKA ADABU",
                "BOFU",
                "LIKONI",
                "TIMBWANI"
            ],
            "MVITA": [
                "MJI WA KALE/MAKADARA",
                "TUDOR",
                "TONONOKA",
                "SHIMANZI/GANJONI",
                "MAJENGO"
            ]
        },
        ...
        }
        """
        counties_data = json.load(f)
        statuses = [
            "missing",
            "found_pending",
            "found_confirmed",
        ]

        for i in range(count):
            # first create a contact
            contact_name = fake.name()
            contact_phone = fake.phone_number()
            contact_email = fake.email()

            contact = MissingPersonContact(
                name=contact_name, phone_number=contact_phone, email=contact_email
            )
            contact.save()
            # then create a missing person
            genders = ["M", "F"]

            # select random gender
            random_gender = random.choice(genders)
            random_age = random.randint(1, 100)
            random_county = random.choice(list(counties_data.keys()))
            # select a random constituency in that county
            random_constituency = random.choice(
                list(counties_data[random_county].keys())
            )
            # select a random ward in that constituency
            random_ward = random.choice(
                counties_data[random_county][random_constituency]
            )
            random_status = random.choice(statuses)
            person_name = fake.name()
            last_seen_location = fake.address()
            description = fake.text(max_nb_chars=200)

            person = MissingPerson(
                name=person_name,
                gender=random_gender,
                age=random_age,
                last_seen_location=last_seen_location,
                description=description,
                county=random_county,
                sub_county=random_constituency,
                ward=random_ward,
                status=random_status,
            )
            person.save()
            person.contacts.add(contact)
            person.save()


def convert_counties_constituencies_wards_csv_to_json(
    csv_file_path="static/data/counties-constituencies-wards.csv",
    json_file_path="static/data/counties-constituencies-wards.json",
):
    """ "
    Utility script to convert the CSV file containing counties, constituencies, and wards to a JSON structure.
    """
    data = {}
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            county = row["COUNTY NAME"].strip()
            constituency = row["CONSTITUENCY NAME"].strip()
            ward = row["WARD NAME"].strip()

            if county not in data:
                data[county] = {}

            if constituency not in data[county]:
                data[county][constituency] = []

            if ward and ward not in data[county][constituency]:
                data[county][constituency].append(ward)

    with open(json_file_path, mode="w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=4)
