import os
from io import BytesIO, StringIO
import json
import requests
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import yagmail
import pytz
import time
from datetime import datetime
from itertools import groupby
from sanic import Blueprint
from sanic.response import json as sanic_json, text
from sqlalchemy import select, delete
from sqlalchemy.dialects.mysql import insert
from sanic.exceptions import SanicException
from web.db_connection import engine, p_do_zatwierdzenia, p_zatwierdzacze, p_zatwierdzone, p_zatwierdzone_json, p_anulowane_json, p_users, p_zatwierdzone_bonusy, p_odrzucone, p_benefity, p_bledy
# from web.passes import google_pass
import random
import string
load_dotenv()

file = Blueprint('file')

yag = yagmail.SMTP(user=f"{os.environ['MAIL_ADDRESS']}",
                   password=f"{os.environ['MAIL_PASS']}", host=f"{os.environ['MAIL_HOST']}", port=f"{os.environ['MAIL_PORT']}", smtp_ssl=False)

verify_val = False
# ca_bundle = certifi.where()

local_tz = pytz.timezone('Europe/Warsaw')
user = os.environ.get('PIERSCIEN_USER')
address = os.environ.get('PIERSCIEN_ADDRESS')
password = os.environ.get('PIERSCIEN_PASS')
session = requests.Session()
session.auth = (user, password)
project_url = f"https://{address}/v1/projects/"
person_url = f"https://{address}/v1/persons"
contract_url = f"https://{address}/v1/contracts"
umowy = session.get(
    url=f"https://{address}/v1/form_of_employment_dicts", verify=verify_val).json()
umowy_id = [2, 7]
umowy_z_zus_id = [3]
project_request = session.get(url=project_url, verify=verify_val)
project_response = project_request.json()
values = {
    'stawki': 'stawki',
    'dodatki': 'dodatki'
}



class Removal:
    def __init__(self) -> None:
        self.project_code = ""
        self.project_name = ""
        self.okres_rozliczenia = ""
        self.kto_wysylal = ""
        self.data_wyslania = ""
        self.kto_usunal = ""
        self.powod_usuniecia = ""
        self.data_usuniecia = ""
        self.odrzucenie = 'N'
        self.powod_odrzucenia = None


class Project:
    def __init__(self):
        self.total_kts = 0
        self.monthly_hours = 0.0
        self.avg_rbh = 0.0
        self.total_project_salary = 0.0
        self.avg_salary = 0.0
        self.total_bonus = 0.0
        self.total_cost = 0.0
        self.complete_total = 0.0
        self.details = []


class User:
    def __init__(self):
        self.suma_godzin_w_miesiacu = 0.0
        self.suma_nieefe = 0.0
        self.suma_szkolen = 0.0
        self.suma_bonusow = 0.0
        self.suma_kosztow = 0.0
        self.dane = []
        self.bonusy = []


class Missing:
    letters = string.ascii_lowercase

    def __init__(self):
        self.missing_id = ''.join(random.choice(self.letters)
                                  for i in range(20))
        self.mocarz_id = None
        self.imie = None
        self.nazwisko = None
        self.projekt_kod_plik = None
        self.projekt_nazwa_plik = None
        self.nazwa_pliku = None
        self.problem = "¯\_(ツ)_/¯ nic nie pasuje, sprawdź manualnie"
        self.profil = None
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_contract_name(contract):
    contract_details = session.get(
        f"{contract_url}/{contract['id']}", verify=verify_val).json()
    id_umowy = contract_details['employment_form']['id']
    nazwa_umowy = list(filter(lambda u: u['id'] == id_umowy, umowy))[0]['name']
    return {
        'nazwa': nazwa_umowy,
        'ma_zus': True if id_umowy in umowy_z_zus_id else False
    }


@file.get('/api/find_lists/<user>')
def get_list(request, user):
    def check_access():
        query = select(p_users.c.access).where(
            p_users.c.login == user
        )
        return query

    def find_co():
        query = select(p_zatwierdzacze.c.lokalizacja).where(
            p_zatwierdzacze.c.login == user
        )
        return query

    def find_zatwierdzone(table):
        query = select(
            table.c.zatwierdzenie_id,
            table.c.project_name,
            table.c.project_code,
            table.c.okres_rozliczenia,
            # func.round(func.sum(table.c.wyplata_za_dzien), 2).label('total_sum')
        ).group_by(
            table.c.zatwierdzenie_id,
            table.c.project_name,
            table.c.project_code,
            table.c.okres_rozliczenia,
        )
        return query

    do_zatwierdzenia_query = select(p_do_zatwierdzenia.c.zatwierdzenie_id, p_do_zatwierdzenia.c.project_code,
                                    p_do_zatwierdzenia.c.okres_rozliczenia, p_do_zatwierdzenia.c.project_name)

    znajdz_zatwierdzone_stawki = find_zatwierdzone(p_zatwierdzone)
    znajdz_zatwierdzone_bonusy = find_zatwierdzone(p_zatwierdzone_bonusy)
    with engine.begin() as conn:
        user_access = conn.execute(check_access()).first()
        if user_access.access == '*':
            list_table = conn.execute(do_zatwierdzenia_query).fetchall()
            zatwierdzone = conn.execute(znajdz_zatwierdzone_stawki).fetchall()
            zatwierdzone_id = list(dict.fromkeys(
                [z.zatwierdzenie_id for z in zatwierdzone]))
            zatwierdzone_bonusy = conn.execute(znajdz_zatwierdzone_bonusy.where(
                p_zatwierdzone_bonusy.c.zatwierdzenie_id.not_in(zatwierdzone_id)
            )).fetchall()
        elif user_access.access == 'zatwierdzacz':
            list_of_cos = conn.execute(find_co()).fetchall()
            list_of_cos = [co.lokalizacja for co in list_of_cos]
            list_table = conn.execute(do_zatwierdzenia_query.where(
                p_do_zatwierdzenia.c.lokalizacja.in_(list_of_cos)
            )).fetchall()
            zatwierdzone = conn.execute(znajdz_zatwierdzone_stawki.where(
                p_zatwierdzone.c.lokalizacja.in_(list_of_cos)
            )).fetchall()
            zatwierdzone_kody = list(dict.fromkeys(
                [z.project_code for z in zatwierdzone]))
            zatwierdzone_bonusy = conn.execute(znajdz_zatwierdzone_bonusy.where(
                p_zatwierdzone_bonusy.c.lokalizacja.in_(list_of_cos),
                p_zatwierdzone_bonusy.c.project_code.not_in(zatwierdzone_kody)
            )).fetchall()
        else:
            list_table = conn.execute(do_zatwierdzenia_query.where(
                p_do_zatwierdzenia.c.osoba_wysylajaca == user
            )).fetchall()
            zatwierdzone = conn.execute(znajdz_zatwierdzone_stawki).fetchall()

    zatwierdzone.extend(zatwierdzone_bonusy)
    zatwierdzone = sorted(zatwierdzone, key=lambda d: d['project_name'])
    response = {}
    response['do_zatwierdzenia'] = json.dumps(
        [dict(result._mapping) for result in list_table], default=str, ensure_ascii=False)
    response['zatwierdzone'] = json.dumps(
        [dict(result._mapping) for result in zatwierdzone], default=str, ensure_ascii=False)
    return sanic_json(response)


@file.post('/api/dane_do_zatwierdzenia')
def dane_do_zatwierdzenia(request):
    request_data = request.json
    query = select(
        p_do_zatwierdzenia.c.dane,
        p_do_zatwierdzenia.c.zatwierdzenie_id,
        p_do_zatwierdzenia.c.osoba_wysylajaca,
        p_do_zatwierdzenia.c.data_wyslania
    ).where(
        p_do_zatwierdzenia.c.project_code == request_data['code']
    ).where(
        p_do_zatwierdzenia.c.okres_rozliczenia == request_data['timePeriod']
    )
    with engine.begin() as conn:
        response = conn.execute(query).first()
    response_dict = {
        'dane': response.dane,
        'id': response.zatwierdzenie_id,
        'wysylacz': response.osoba_wysylajaca,
        'data_wyslania': str(response.data_wyslania)
    }
    return sanic_json(response_dict)



def wyrzuc_smieci(id):
    delete_query = delete(p_do_zatwierdzenia).where(
        p_do_zatwierdzenia.c.zatwierdzenie_id == id
    )
    return delete_query


def znajdz_wysylacza(login):
    query = select(p_users).where(
        p_users.c.login == login
    )
    return query


@file.post('/api/zatwierdz_lp')
def zatwierdz_lp(request):
    request_data = request.json
    parsed_data = json.loads(request_data['dane'])
    osoba_zatwierdzajaca = request_data['osobaZatwierdzajaca']
    nazwa_pliku = parsed_data['file_name']
    project_name = parsed_data['project_name']
    project_code = parsed_data['code']
    time_period = parsed_data['time_period']
    zatwierdzenie_id = request_data['zatwierdzenieId'] if request_data[
        'zatwierdzenieId'] else f"{project_code}_{time_period}"
    osoba_wysylajaca = request_data['osobaWysylajaca'] if request_data[
        'osobaWysylajaca'] else request_data['osobaZatwierdzajaca']
    data_wyslania = request_data['dataWyslania'] if request_data['osobaWysylajaca'] else datetime.now(
        tz=local_tz)

    data_zatwierdzenia = datetime.now(tz=local_tz)

    with engine.begin() as conn:
        for detail in parsed_data['details']:
            for dane in detail['dane']:
                conn.execute(insert(p_zatwierdzone).values(
                    zatwierdzenie_id=zatwierdzenie_id,
                    nazwa_pliku=nazwa_pliku,
                    project_code=project_code,
                    project_name=project_name,
                    lokalizacja=parsed_data['lokalizacja'],
                    okres_rozliczenia=time_period,
                    mocarz_id=detail['mocarz_id'],
                    imie_i_nazwisko=detail['imie_i_nazwisko'],
                    PESEL=detail['pesel'],
                    data_pracy=dane['data'],
                    suma_godzin=dane['suma_godzin'],
                    w_tym_nieefektywne=dane['w_tym_nieEFE'],
                    w_tym_szkoleniowe=dane['w_tym_szkoleniowe'],
                    uwagi=dane['uwagi'],
                    stawka_za_dzien=dane['stawka_za_dzien'],
                    rodzaj_umowy=dane['rodzaj_umowy'],
                    kwota=dane['kwota'],
                    koszt=dane['koszt_pracodawcy'],
                    kwota_z_kosztem=dane['kwota_z_kosztem'],
                    osoba_wysylajaca=osoba_wysylajaca,
                    osoba_zatwierdzajaca=osoba_zatwierdzajaca,
                    data_wyslania=data_wyslania,
                    data_zatwierdzenia=data_zatwierdzenia
                ))
            for bonus in detail['bonusy']:
                conn.execute(insert(p_zatwierdzone_bonusy).values(
                    zatwierdzenie_id=zatwierdzenie_id,
                    nazwa_pliku=nazwa_pliku,
                    project_code=project_code,
                    project_name=project_name,
                    lokalizacja=parsed_data['lokalizacja'],
                    okres_rozliczenia=time_period,
                    mocarz_id=detail['mocarz_id'],
                    imie_i_nazwisko=detail['imie_i_nazwisko'],
                    kwota=bonus['kwota'],
                    kategoria=bonus['kategoria'],
                    komentarz=bonus['komentarz'],
                    osoba_wysylajaca=osoba_wysylajaca,
                    osoba_zatwierdzajaca=osoba_zatwierdzajaca,
                    data_wyslania=data_wyslania,
                    data_zatwierdzenia=data_zatwierdzenia
                ))
        conn.execute(insert(p_zatwierdzone_json).values(
            zatwierdzenie_id=zatwierdzenie_id,
            project_code=project_code,
            project_name=project_name,
            lokalizacja=parsed_data['lokalizacja'],
            okres_rozliczenia=time_period,
            dane=request_data['dane'],
            osoba_wysylajaca=osoba_wysylajaca,
            osoba_zatwierdzajaca=osoba_zatwierdzajaca,
            data_wyslania=data_wyslania,
            data_zatwierdzenia=data_zatwierdzenia
        ))
        conn.execute(wyrzuc_smieci(zatwierdzenie_id))
        find_sender = conn.execute(znajdz_wysylacza(osoba_wysylajaca)).first()
        mail = find_sender.mail
        imie = find_sender.imie
        response_text = 'Lista płac została zaakceptowana!'
    try:
        content = f"""Witaj, {imie}!
      Twoja lista płac dla projectu: {project_name} za okres: {time_period} została zaakceptowana.
      Gratulacje!
          """
        if mail and osoba_zatwierdzajaca != osoba_wysylajaca:
            yag.send(mail, "Twoja lista płac została zaakceptowana!", content)
        return text(response_text)
    except Exception:
        return text(response_text)


@file.post('/api/anuluj_zatwierdzenie')
def anuluj_zatwierdzenie(request):
    data = request.json

    def find_mail_info(table):
        query = select(
            p_users.c.mail,
            p_users.c.imie,
            table.c.project_name,
            table.c.osoba_wysylajaca
        ).select_from(
            p_users
        ).join(
            table, p_users.c.login == table.c.osoba_wysylajaca
        ).where(
            table.c.okres_rozliczenia == data['date'],
            table.c.project_code == data['code']
        )
        return query

    def skopiuj_anulowana_lp():
        find_record_query = select(p_zatwierdzone_json).where(
            p_zatwierdzone_json.c.okres_rozliczenia == data['date'],
            p_zatwierdzone_json.c.project_code == data['code']
        )
        with engine.begin() as conn:
            record_to_copy = conn.execute(find_record_query).first()
            conn.execute(insert(p_anulowane_json).values(
                zatwierdzenie_id=record_to_copy.zatwierdzenie_id,
                project_code=record_to_copy.project_code,
                project_name=record_to_copy.project_name,
                lokalizacja=record_to_copy.lokalizacja,
                okres_rozliczenia=record_to_copy.okres_rozliczenia,
                osoba_wysylajaca=record_to_copy.osoba_wysylajaca,
                data_wyslania=record_to_copy.data_wyslania,
                dane=record_to_copy.dane,
                osoba_zatwierdzajaca=record_to_copy.osoba_zatwierdzajaca,
                data_zatwierdzenia=record_to_copy.data_zatwierdzenia,
                osoba_anulujaca=data['login'],
                data_anulowania=datetime.now(tz=local_tz)
            ))

    def delete_data(tabela):
        delete_query = delete(tabela).where(
            tabela.c.okres_rozliczenia == data['date']
        ).where(
            tabela.c.project_code == data['code']
        )
        with engine.begin() as conn:
            conn.execute(delete_query)
    with engine.begin() as conn:
        mail_info = conn.execute(find_mail_info(p_zatwierdzone)).first()
        if not mail_info:
            mail_info = conn.execute(
                find_mail_info(p_zatwierdzone_bonusy)).first()
    powod_anulowania = f"Zatwierdzenie zostało anulowane przez {data['login']}"
    trace_deletion(from_zatwierdzone=True,
                   code=data['code'], date=data['date'], deleter=data['login'], reason=powod_anulowania)
    skopiuj_anulowana_lp()
    try:
        mail_content = f"""Witaj, {mail_info.imie}!
      Dostajesz tego maila, ponieważ akceptacja dla projektu {mail_info.project_name} ({data['code']}) została właśnie anulowana przez {data['login']}.
      Pozdrawiamy,
      Zespół Pierścienia.
      """
        delete_data(p_zatwierdzone)
        delete_data(p_zatwierdzone_json)
        delete_data(p_zatwierdzone_bonusy)
        try:
            if mail_info.mail and data['login'] != mail_info.osoba_wysylajaca:
                yag.send(to=mail_info.mail,
                         subject=f"Lista płac dla projektu {mail_info.project_name} została anulowana!", contents=mail_content)
        except Exception:
            pass
    except AttributeError:
        delete_data(p_zatwierdzone)
        delete_data(p_zatwierdzone_json)
        delete_data(p_zatwierdzone_bonusy)
    return text('Dane usunięte!')


@file.post('/api/reject_rates')
def reject_rates(request):
    req = request.json

    def find_wysylacz(login):
        find_wysylacz_query = select(
            p_users.c.mail
        ).where(
            p_users.c.login == login
        )
        return find_wysylacz_query
    try:
        with engine.begin() as conn:
            project = trace_deletion(rejection='Y', rejection_reason=req['reason'], code=req['code'],
                                     date=req['date'], deleter=req['rejector'], reason='Odrzucenie stawek')
            conn.execute(delete(p_do_zatwierdzenia).where(
                p_do_zatwierdzenia.c.project_code == req['code']
            ).where(
                p_do_zatwierdzenia.c.okres_rozliczenia == req['date']
            ))
            wysylacz = conn.execute(find_wysylacz(project['wysylacz'])).first()
            content = f"""Twoja lista płac dla projektu {project['project']} za okres: {req['date']} została odrzucona.
          Powód odrzucenia: {req['reason']}.
          Proszę, nanieś niezbędne zmiany i dodaj listę płac ponownie.
          """
            try:
                if wysylacz.mail:
                    yag.send(wysylacz.mail,
                             "Twoja lista płac została odrzucona", content)
                return text('Usunięto')
            except Exception:
                return text('Usunięto')
    except Exception as e:
        raise SanicException(f'Nie udało się odrzucić stawek - {e}')


@file.post('/api/upload_data')
def upload_data(request):
    upload_data = request.json
    # parsed_data = json.loads(upload_data['dane'])
    find_zatwierdzacz_query = select(
        p_users.c.mail
    ).select_from(
        p_users
    ).join(
        p_zatwierdzacze, p_users.c.login == p_zatwierdzacze.c.login
    ).where(
        p_zatwierdzacze.c.lokalizacja == upload_data['location']
    )
    insert_query = insert(p_do_zatwierdzenia).values(
        zatwierdzenie_id=f"{upload_data['code']}_{upload_data['timePeriod']}",
        project_code=upload_data['code'],
        project_name=upload_data['projectName'],
        lokalizacja=upload_data['location'],
        okres_rozliczenia=upload_data['timePeriod'],
        osoba_wysylajaca=upload_data['sender'],
        dane=upload_data['dane'],
        data_wyslania=datetime.now(tz=local_tz)
    )
    update_query = insert_query.on_duplicate_key_update(
        project_code=insert_query.inserted.project_code,
        project_name=insert_query.inserted.project_name,
        lokalizacja=insert_query.inserted.lokalizacja,
        okres_rozliczenia=insert_query.inserted.okres_rozliczenia,
        osoba_wysylajaca=insert_query.inserted.osoba_wysylajaca,
        dane=insert_query.inserted.dane,
        data_wyslania=insert_query.inserted.data_wyslania,
    )
    adress = 'http://pierscien.voicecc.pl'
    content = f"""Witaj!
        <a href="{adress}">W systemie Pierścień</a> czeka na ciebie do zatwierdzenia lista płac dla projektu: {upload_data['projectName']} za okres: {upload_data['timePeriod']}, wysłany przez: {upload_data['sender']}..
        """

    with engine.begin() as conn:
        conn.execute(update_query)
        zatwierdzacze_data = conn.execute(find_zatwierdzacz_query).fetchall()
    mails_to_send = [d.mail for d in zatwierdzacze_data if d.mail]
    response_text = "Twój plik został załadowany do bazy danych i oczekuje na zatwierdzenie."
    try:
        if len(mails_to_send) > 0:
            yag.send(mails_to_send,
                     f"Nowa lista płac dla projektu {upload_data['projectName']} czeka na zatwierdzenie!", content)
            return text(f"""{response_text} |
                      Mail z informacją został wysłany na {'adres' if len(mails_to_send) == 1 else 'adresy'}: {mails_to_send}.|
                      W razie problemów na pewno się o nich dowiesz.|
                      """)
        else:
            return text(f"""{response_text} |
                        W bazie danych brakuje danych kontaktowych do osoby odpowiedzialnej za zatwierdzenie pliku. | 
                        Poinformuj tę osobę o pliku czekającym na zatwierdzenie i poinformuj ekipę odpowiedzialną za Pierścień o tym rażącym niedopatrzeniu.|
                        Dziękujemy! 
                    """)
    except Exception:
        return text(f"""{response_text} |
                      Nie udało się wysłać maila do osoby odpowiedzialnej za zatwierdzenie pliku - pracujemy nad tym! | 
                      Poinformuj tę osobę o pliku czekającym na zatwierdzenie |
                      Dziękujemy i miłego dnia! 
                  """)


config = {}
config["upload"] = "./web/uploads"


def insert_mistakes(missing):
    with engine.begin() as conn:
        conn.execute(insert(p_bledy).values(
            missing_id=missing.missing_id,
            mocarz_id=missing.mocarz_id,
            imie=missing.imie,
            nazwisko=missing.nazwisko,
            profil=missing.profil,
            projekt_kod_z_pliku=missing.projekt_kod_plik,
            projekt_nazwa_z_mocarza=missing.projekt_nazwa_plik,
            nazwa_pliku=missing.nazwa_pliku,
            problem=missing.problem,
            czas_utworzenia=missing.time
        ))


def check_missing(users, file_name, file_code, date):
    missing = Missing()
    t = time.localtime()
    current_time = time.strftime("%H_%M_%S", t)
    project_data = [obj for obj in project_response if
                    obj['project_code'] == file_code][0]
    project_name = project_data['name']
    for u in users:
        missing.missing_id = f"{file_code}_{date}_{current_time}"
        if not isinstance(u['mocarz_id'], str) or 'VCC' not in u['mocarz_id']:
            missing.projekt_kod_plik = file_code
            missing.projekt_nazwa_plik = file_name
            missing.mocarz_id = u['mocarz_id']
            missing.problem = 'Mocarz ID jest w złym formacie, powinno być stringiem składającym się z liter VCC i PIĘCIU cyfr'
        else:
            user_url = f"https://{address}/v1/persons/{u['mocarz_id'].split('VCC')[1]}"
            user_request = session.get(url=user_url, verify=verify_val)
            user_response = user_request.json()
            missing.imie = user_response['first_name']
            missing.nazwisko = user_response['last_name']
            missing.mocarz_id = u['mocarz_id']
            missing.profil = f"https://mocarz.voicecc.pl/person/{u['mocarz_id'].split('VCC')[1]}/related_projects"
            missing.projekt_kod_plik = file_code
            missing.projekt_nazwa_plik = file_name
            if len(user_response['allocation_set']) > 0:
                allocation_check = [obj for obj in user_response['allocation_set'] if
                                    obj['project'] == project_name]
                if len(allocation_check) == 0:
                    # print(f"{user_response['first_name']} {user_response['last_name']} nigdy nie miał/a przypisanej alokacji do projektu: {project_name}")
                    missing.problem = f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) nigdy nie miał/a przypisanej alokacji do projektu: {project_name}"
                else:
                    for a in allocation_check:
                        if not a['end_date']:
                            # print(f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) jest teoretycznie przypisany do projektu: {project_name}. Alokacja nie ma daty zakończenia - trzeba sprawdzić ręcznie")
                            missing.problem = f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) jest teoretycznie przypisany do projektu: {project_name}. Alokacja nie ma daty zakończenia - trzeba sprawdzić ręcznie"
                            break
                        elif date in a['end_date']:
                            # print(f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) jest teoretycznie przypisany do projektu: {project_name} a alokacja kończy się w miesiącu za który sprawdzamy - trzeba sprawdzić ręcznie")
                            missing.problem = f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) jest teoretycznie przypisany do projektu: {project_name} a alokacja kończy się w miesiącu za który sprawdzamy - trzeba sprawdzić ręcznie"
                            break
                        else:
                            # print(f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) miał/a przypisaną alokację do projektu: {project_name}. Ostatnia data zakończenia alokacji: {a['end_date']}")
                            missing.problem = f"{user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) miał/a przypisaną alokację do projektu: {project_name}. Ostatnia data zakończenia alokacji: {a['end_date']}"
                            break
            else:
                missing.problem = f"Użytkownik: {user_response['first_name']} {user_response['last_name']} ({u['mocarz_id']}) nie ma przypisanej żadnej alokacji"
        insert_mistakes(missing)
    return missing.missing_id


def check_files(file):
    if file:
        file_parameters = {
            'body': file.body,
            'name': file.name,
            'type': file.type,
        }

        file_name_split = file_parameters['name'].split('.')
        file_extension = file_name_split[-1]
        file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + \
            '_'+file_name_split[0]+'_upload'
        file_body = file_parameters['body']

        return {
            'name': file_name,
            'extension': file_extension,
            'body': file_body,
            'original_name': file_parameters['name']
        }
    else:
        return None


def check_databases(db, code, period):
    query = select(db).where(
        db.c.project_code == code
    ).where(
        db.c.okres_rozliczenia == period
    )
    with engine.begin() as conn:
        query_result = conn.execute(query).fetchall()
    if len(query_result) == 0:
        return True
    else:
        return False


def response_text(status, name, time_period):
    if status == 406:
        return f"Rekordy dla {name} za okres {time_period} zostały już zatwierdzone. Skontaktuj się ze swoim przełożonym w celu cofnięcia ich zatwierdzenia."
    else:
        return f"Rekordy dla {name} za okres {time_period} zostały już wysłane do zatwierdzenia. Kontynuacja oznacza zastąpienie lub usunięcie części danych!"


def correct_extensions(ext1, ext2=None):
    if ext2:
        extensions = [ext1, ext2]
        for extension in extensions:
            if extension == 'csv' or extension == 'xlsx':
                continue
            else:
                return extension
    else:
        if ext1 == 'csv' or ext1 == 'xlsx':
            return True
        else:
            return False


def header_info(file=None):
    header_df = pd.read_csv(BytesIO(file),
                            nrows=4, usecols=range(2), names=['id', 'values'])
    # pd.read_csv(BytesIO(body), delimiter=",", header=4, engine='python')
    header = {}
    for key, value in (header_df.values):
        header[key] = value
    return header


def exclude_keys(dict, keys):
    return {
        key: value for key, value in dict.items()
        if key not in keys
    }


def compare_mocarz_and_file(file_ids, project_id):
    mocarz_not_in_file = []
    current_project_url = f"{project_url}{project_id}"
    current_project_request = session.get(
        url=current_project_url, verify=verify_val)
    active_users_in_mocarz = [{
        'name': f"{user['person']['first_name']} {user['person']['last_name']}",
        'mocarz_id': f"VCC{str(user['person']['id']).zfill(5)}"
                              #  'last_name': user['person']['last_name']
                              } for user in current_project_request.json()[
        'allocation_set'] if user['is_active'] == True]
    for obj in active_users_in_mocarz:
        if obj['mocarz_id'] not in file_ids and obj not in mocarz_not_in_file:
            mocarz_not_in_file.append(obj)
    return mocarz_not_in_file


def calculate_employer_cost(zus, number, percentage=19.48):
    cost = 0.0
    if zus:
        cost = round(number * (percentage / 100), 2)
    return cost


def calculate_base_rates(data, date_for_allocation, project_code, project_data, og_name):
    # try:
    missing = Missing()

    def key_func(k):
        return k['mocarz_id']

    def parse_dates(date):
        return datetime.strptime(date, '%Y-%m-%d').date()
    date_for_url = date_for_allocation.split('-')
    rates_url = f"https://{address}/v1/service/list_active_rates/{date_for_url[0]}/{date_for_url[1]}/{project_data['id']}"
    rates_date = f"{date_for_url[0]}-{date_for_url[1]}"
    project_id = project_data['id']
    rates_request = session.get(url=rates_url, verify=verify_val)
    rates_response = rates_request.json()

    rates_data = [
        obj for obj in rates_response if rates_date in obj['start_date']]

    INFO = sorted(rates_data, key=key_func)
    rates_from_mocarz = groupby(INFO, key_func)

    sorted_rates = {f"VCC{str(mocarz_id).zfill(5)}": [{'start': d['start_date'], 'end': d['end_date'],
                                                      'rate': d['rate_value'], 'rate_name': d['rate_name']} for d in data] for mocarz_id, data in rates_from_mocarz}

    def sprawdz_stawki_i_kontrakty(date, name, kontrakty, stawki=[]):
        try:
            stawka = 0.0
            umowa = None
            # stawki mogą być pustą tabelą, bo w podsumowaniu w project_routes będziemy używać tej funkcji bez danych na temat stawek - dla samych kontraktów
            if len(stawki) > 0:
                # jeżeli dla danej osoby w danym miesiacu jest tylko jedna stawka i nie ma wpisanej daty końca obowiązywania to przypisujemy automatycznie tę stawkę dla danego dnia
                if not stawki[0]['end']:
                    stawka = stawki[0]['rate']
                else:
                    # jeśli jest więcej stawek, porównujemy datę końca stawki z dniem dla którego wykonujemy obliczenia
                    # jeśli data zakończenia stawki jest większa lub równa dacie dla której obliczamy - przypisujemy tę stawkę do konkretnego dnia
                    for s in stawki:
                        if s['end']:
                            if parse_dates(s['end']) >= parse_dates(date):
                                stawka = s['rate']
                                break
                        else:
                            stawka = s['rate']

            # sortujemy tabelę z kontraktami, żeby ułatwić ich porównanie z obecną datą, następnie wykonujemy te same operacje co powyżej dla stawek
            sorted_kontrakty = sorted(kontrakty, key=lambda d: d['start_date'])
            if not sorted_kontrakty[0]['end_date']:
                # umowa = sorted_kontrakty[0]['name']
                umowa = get_contract_name(sorted_kontrakty[0])
            else:
                for sk in sorted_kontrakty:
                    if sk['end_date']:
                        if parse_dates(sk['end_date']) >= parse_dates(date):
                            # umowa = sk['name']
                            umowa = get_contract_name(sk)
                            break
                    else:
                        # umowa = sk['name']
                        umowa = get_contract_name(sk)

            # zwracamy stawkę i rodzaj umowy które zgodnie z obliczeniami powinny obowiązywać danego dnia
            return {
                'stawka': stawka,
                'umowa': umowa['nazwa'],
                'zus': umowa['ma_zus']
            }
        except ValueError as ve:
            missing = Missing()
            missing.problem = ve
            missing.nazwa_pliku = name
            insert_mistakes(missing)
            raise SanicException(
                f"Wystąpił problem z formatem danych w załadowanym pliku. \nSzczegóły: {ve}", 422)

    result_dict = {}

    for d in data:
        t = result_dict.setdefault(d['mocarz_id'], [])
        t.append(d)
    details = []
    present_ids = []
    missing_ids = []
    # mocarz_not_in_file = []
    total_hours = 0.00
    total_ineffective = 0.0
    total_training = 0.0
    total_project_salary = 0.0
    total_project_cost = 0.0
    for id, data_list in result_dict.items():
        if id in sorted_rates.keys():
            present_ids.append(id)
            for mocarz_id, rate_data in sorted_rates.items():
                if mocarz_id == id:
                    user = User()
                    mocarz_id = data_list[0]['mocarz_id']
                    imie_i_nazwisko = data_list[0]['imie_i_nazwisko']
                    pesel = data_list[0]['PESEL']
                    dane_list = []
                    person_request = session.get(
                        url=f"{person_url}/{mocarz_id[3:]}", verify=verify_val)
                    historia_kontraktow = person_request.json()['contract_set']

                    for each in data_list:
                        rate_check = sprawdz_stawki_i_kontrakty(
                            each['data'], og_name, historia_kontraktow, rate_data)
                        each['stawka_za_dzien'] = rate_check['stawka']
                        each['rodzaj_umowy'] = rate_check['umowa']
                        each['kwota'] = round(float(
                            each['stawka_za_dzien'])*float(each['suma_godzin']), 2)
                        each['koszt_pracodawcy'] = round(calculate_employer_cost(
                            rate_check['zus'], each['kwota']), 2)
                        each['kwota_z_kosztem'] = round(each['kwota'] + each['koszt_pracodawcy'], 2)
                        dane_list.append(exclude_keys(
                            each, ['mocarz_id', 'imie_i_nazwisko', 'PESEL']))
                        user.suma_godzin_w_miesiacu += each['suma_godzin']
                        user.suma_nieefe += each['w_tym_nieEFE'] if each['w_tym_nieEFE'] else 0.0
                        user.suma_szkolen += each['w_tym_szkoleniowe'] if each['w_tym_szkoleniowe'] else 0.0
                        user.suma_kosztow += each['koszt_pracodawcy']
                        user.mocarz_id = mocarz_id
                        user.imie_i_nazwisko = imie_i_nazwisko
                        user.pesel = pesel
                        user.dane = dane_list
                    details.append(vars(user))
        else:
            missing_ids.append({
                'name': data_list[0]['imie_i_nazwisko'],
                'mocarz_id': data_list[0]['mocarz_id'],
                'pesel': data_list[0]['PESEL'],
            })
 
    for each in details:
        sum = 0.0
        cost_sum = 0.0
        total_hours += each['suma_godzin_w_miesiacu']
        total_ineffective += each['suma_nieefe']
        total_training += each['suma_szkolen']
        for c in each['dane']:
            sum += c['kwota']
            cost_sum += c['koszt_pracodawcy']
        total_project_salary += sum
        total_project_cost += cost_sum
        each['total_salary'] = round(sum, 2)
        each['total_cost'] = round(cost_sum, 2)
        each['complete_salary'] = round((sum + cost_sum), 2)
    total_kt = len(present_ids)

    avg_salary = round(total_project_salary /
                       float(total_kt), 2) if total_kt != 0 else 0.0
    avg_work_time = round(total_hours / float(total_kt),
                          2) if total_kt != 0 else 0.0
    project = Project()
    project.file_name = og_name
    project.project_name = project_data['name']
    project.lokalizacja = project_data['location']
    project.total_kts = total_kt
    project.monthly_hours = str(round(total_hours, 2))
    project.avg_rbh = avg_work_time
    project.total_project_salary = str(round(total_project_salary, 2))
    project.total_cost = str(round(total_project_cost, 2))
    project.complete_total = str(round(total_project_salary + total_project_cost, 2))
    project.avg_salary = avg_salary
    project.client = project_data['client']
    project.code = project_code
    project.time_period = date_for_allocation
    project.details = details
    # os.remove(file_path)

    id_for_details = check_missing(
        missing_ids, project_data['name'], project_code, rates_date)

    return {
        "message": "Ok",
        'in_mocarz': vars(project),
        'file_ids': result_dict.keys(),
        'project_id': project_id,
        'not_in_mocarz': missing_ids,
        'details_id': id_for_details,
        'status': 200
    }


def calculate_bonuses(data, date_for_allocation, project_code, project_data, og_name):
    try:
        details = []
        total_bonus = 0.0
        total_salary = 0.0
        result_dict = {}
        for d in data:
            t = result_dict.setdefault(d['mocarz_id'], [])
            t.append(d)
        for data_list in result_dict.values():
            user = User()
            mocarz_id = data_list[0]['mocarz_id']
            imie_i_nazwisko = data_list[0]['imie_i_nazwisko']
            pesel = data_list[0]['PESEL']
            bonus_list = []
            for each in data_list:
                bonus_list.append(exclude_keys(
                    each, ['mocarz_id', 'imie_i_nazwisko', 'PESEL']))

                user.mocarz_id = mocarz_id
                user.imie_i_nazwisko = imie_i_nazwisko
                user.pesel = pesel
                user.total_salary = total_salary
                user.bonusy = bonus_list
            for bonus in bonus_list:
                total_bonus += float(bonus['kwota'])
                user.suma_bonusow += float(bonus['kwota'])
                user.complete_salary = user.total_salary + user.suma_bonusow
            details.append(vars(user))

        project = Project()
        project.total_kts = len(result_dict.keys())
        project.file_name = og_name
        project.project_name = project_data['name']
        project.lokalizacja = project_data['location']
        project.total_bonus = total_bonus
        project.complete_total = total_bonus
        project.client = project_data['client']
        project.code = project_code
        project.time_period = date_for_allocation
        project.details = details
        return {
            'bonus_data': vars(project),
            'status': 200
        }
    except Exception as e:
        raise SanicException(e, 422)


def add_money(base, bonus):
    if base['time_period'] != bonus['time_period'] or base['code'] != bonus['code']:
        raise SanicException(
            "Dane w plikach się nie zgadzają. Sprawdź czy pola \"project_id\" i \"period\" na pewno są takie same w obu plikach!", 422)
    else:
        base['total_bonus'] = bonus['total_bonus']
        matched_ids = set()
        for base_det in base['details']:
            for bonus_det in bonus['details']:
                if base_det['mocarz_id'] == bonus_det['mocarz_id']:
                    base_det['bonusy'] = bonus_det['bonusy']
                    base_det['suma_bonusow'] = bonus_det['suma_bonusow']
                    base_det['complete_salary'] += float(
                        bonus_det['suma_bonusow'])
                    matched_ids.add(bonus_det['mocarz_id'])

        for bonus_det in bonus['details']:
            if bonus_det['mocarz_id'] not in matched_ids:
                base['details'].append(bonus_det)

        base['complete_total'] = str(round(float(
            base['complete_total']) + float(base['total_bonus']),2))

        return base


def recalculate_rates(rates):
    total_hours = 0.0
    total_ineffective = 0.0
    total_training = 0.0
    total_project_salary = 0.0
    total_bonus = 0.0
    total_kt = len([d['mocarz_id'] for d in rates['details']])
    details = rates['details'].copy()
    for each in details:
        sum = 0.0
        sum_of_hours = 0.0
        for c in each['dane']:
            sum += (float(c['suma_godzin']) *
                    float(c['stawka_za_dzien']))
            sum_of_hours += float(c['suma_godzin'])
        each['suma_godzin_w_miesiacu'] = sum_of_hours
        total_project_salary += sum
        total_bonus += float(each['suma_bonusow'])
        total_hours += each['suma_godzin_w_miesiacu']
        total_ineffective += each['suma_nieefe']
        total_training += each['suma_szkolen']
        each['total_salary'] = round(sum, 2)
        each['complete_salary'] = float(
            each['total_salary']) + float(each['suma_bonusow'])
    avg_salary = round(total_project_salary / float(total_kt), 2)
    avg_work_time = round(total_hours / float(total_kt), 2)
    project = Project()
    project.file_name = rates['file_name']
    project.project_name = rates['project_name']
    project.total_kts = total_kt
    project.monthly_hours = str(round(total_hours, 2))
    project.avg_rbh = avg_work_time
    project.total_bonus = total_bonus
    project.total_project_salary = str(round(total_project_salary, 2))
    project.complete_total = round(
        total_project_salary, 2) + round(total_bonus, 2)
    project.avg_salary = avg_salary
    project.client = rates['client']
    project.code = rates['code']
    project.time_period = rates['time_period']
    project.details = details
    return vars(project)


def correct_rates(db_data, file_data):
    project = Project()
    details = []
    existing = [d['mocarz_id'] for d in db_data['details']]
    for file in file_data['details']:
        if file['mocarz_id'] not in existing:
            project.details.append(file)
            details.append(file)
        else:
            for db in db_data['details']:
                if db['mocarz_id'] == file['mocarz_id']:
                    if len(db['dane']) > 0:
                        for file_date in file['dane']:
                            for db_date in db['dane']:
                                if file_date['data'] == db_date['data']:
                                    db_date.update({
                                        'suma_godzin': file_date['suma_godzin'],
                                        'w_tym_nieEFE': file_date['w_tym_nieEFE'],
                                        'w_tym_szkoleniowe': file_date['w_tym_szkoleniowe'],
                                        'uwagi': file_date['uwagi'],
                                        'stawka_za_dzien': file_date['stawka_za_dzien'],
                                        'kwota': file_date['kwota']
                                    })
                                else:
                                    if file_date not in db['dane']:
                                        db['dane'].append(file_date)

                    else:
                        db['dane'] = file['dane']
                db['dane'] = sorted(db['dane'], key=lambda d: d['data'])
                details.append(db)

    db_data['details'] = details
    return_val = recalculate_rates(db_data)
    return return_val


def correct_bonus(db_data, file_data):
    for db in db_data['details']:
        for file in file_data['details']:
            if db['mocarz_id'] == file['mocarz_id']:
                db['suma_bonusow'] = file['suma_bonusow']
                db_data['total_bonus'] += float(file['suma_bonusow'])
                db['bonusy'] = file['bonusy']
    return db_data


def correct_data(date, code, main_file=None, bonus_file=None):
    query = select(p_do_zatwierdzenia).where(
        p_do_zatwierdzenia.c.okres_rozliczenia == date
    ).where(
        p_do_zatwierdzenia.c.project_code == code
    )
    with engine.begin() as conn:
        result = conn.execute(query).first()
    from_db = json.loads(result.dane)
    if main_file:
        response = correct_rates(from_db, main_file)

    if bonus_file:
        bonus = correct_bonus(from_db, bonus_file)
        response = add_money(from_db, bonus)
    return response


@ file.post('/api/return_rates_info')
def return_rates_info(request):
    uploader = request.form.get("login")
    correction = True if request.form.get('correction') == 'true' else False
    file_received = request.files.get('mainFile')
    additional_file = request.files.get('bonusFile')
    rate_files = check_files(file_received)
    bonus_info = check_files(additional_file)

    def block_calculation_handler(file_data):
        status = None
        message = None
        if not check_databases(
            p_zatwierdzone, file_data['project_code'], file_data['date_for_allocation'])\
                or not check_databases(
                p_zatwierdzone_bonusy, file_data['project_code'], file_data['date_for_allocation']):
            status = 406
            message = response_text(
                406, file_data['project_data']['name'], file_data['date_for_allocation'])
            # return text(response_text(406, project_name, file_data['date_for_allocation']), 406)
        if not check_databases(p_do_zatwierdzenia, file_data['project_code'], file_data['date_for_allocation']) and not correction:
            status = 202
            message = response_text(
                202, file_data['project_data']['name'], file_data['date_for_allocation'])
        return {
            'status': status,
            'message': message
        }

    if rate_files and bonus_info:
        bad_extension = correct_extensions(
            rate_files['extension'], bonus_info['extension'])
        if not bad_extension:
            save_files(
                rate_files['body'], rate_files['original_name'], rate_files['extension'], uploader)
            save_files(
                bonus_info['body'], bonus_info['original_name'], bonus_info['extension'], uploader)
            base_file_data = read_file(
                rate_files['extension'], rate_files['body'], rate_files['original_name'], values['stawki'])
            bonus_file_data = read_file(
                bonus_info['extension'], bonus_info['body'], bonus_info['original_name'], values['dodatki'])
            block_calculation = block_calculation_handler(base_file_data)
            if block_calculation['status']:
                return text(block_calculation['message'], block_calculation['status'])

            if correction:
                remove_conflicting_records(
                    p_do_zatwierdzenia, base_file_data['date_for_allocation'], base_file_data['project_code'], uploader)
            money_data = calculate_base_rates(
                base_file_data['details'],
                base_file_data['date_for_allocation'],
                base_file_data['project_code'],
                base_file_data['project_data'],
                rate_files['original_name'])
            bonus_data = calculate_bonuses(
                bonus_file_data['details'],
                bonus_file_data['date_for_allocation'],
                bonus_file_data['project_code'],
                bonus_file_data['project_data'],
                bonus_info['original_name'])

            money_response = add_money(
                money_data['in_mocarz'], bonus_data['bonus_data'])
            response_json = {
                'money_data': json.dumps(money_response, ensure_ascii=False),
                'missing_rates': json.dumps(money_data['not_in_mocarz'], ensure_ascii=False),
            }
            missing_in_file = compare_mocarz_and_file(
                money_data['file_ids'], money_data['project_id'])
            response_json['missing_in_file'] = json.dumps(
                missing_in_file, ensure_ascii=False)
            return sanic_json(response_json)
        else:
            return sanic_json({"received": False, "success": False,
                              "message": f"Jeden z plików ma zły format! Powinno być: .csv lub .xlsx a jest .{bad_extension}"}, 403)
    elif rate_files:
        # try:
        if correct_extensions(rate_files['extension']):
            save_files(rate_files['body'], rate_files['original_name'],
                       rate_files['extension'], uploader)
            file_data = read_file(
                rate_files['extension'], rate_files['body'], rate_files['original_name'], values['stawki'])

            block_calculation = block_calculation_handler(file_data=file_data)
            if block_calculation['status']:
                return text(block_calculation['message'], block_calculation['status'])
            if correction:
                remove_conflicting_records(
                    p_do_zatwierdzenia, file_data['date_for_allocation'], file_data['project_code'], uploader)
            money_data = calculate_base_rates(
                file_data['details'],
                file_data['date_for_allocation'],
                file_data['project_code'],
                file_data['project_data'],
                rate_files['original_name'])

            money_details = money_data['in_mocarz']
            response_json = {
                # Łamanina z dumps/loads/dumps zapobiega zwracaniu przez json floatów z większą ilością miejsc po przecinku niż 2
                'money_data': json.dumps(json.loads(json.dumps(money_details), parse_float=lambda x: round(float(x), 2)), ensure_ascii=False),
                'missing_rates': json.dumps(
                    money_data['not_in_mocarz'], ensure_ascii=False),
            }

            missing_in_file = compare_mocarz_and_file(
                money_data['file_ids'], money_data['project_id'])
            response_json['missing_in_file'] = json.dumps(
                missing_in_file, ensure_ascii=False)
            response_json['missing_rates_id'] = money_data['details_id']
            return sanic_json(response_json, money_data['status'])
        else:
            raise SanicException(
                f"Zły format pliku! Powinno być: .csv a jest .{rate_files['extension']}", 422)
        # except Exception as e:
        #     return text(f'Shit is fucked: {e}')
    elif bonus_info:
        save_files(bonus_info['body'], bonus_info['original_name'],
                   bonus_info['extension'], uploader)
        bonus_file_data = read_file(
            bonus_info['extension'], bonus_info['body'], bonus_info['original_name'], values['dodatki'])
        block_calculation = block_calculation_handler(bonus_file_data)
        if block_calculation['status']:
            return text(block_calculation['message'], block_calculation['status'])

        response = calculate_bonuses(
            bonus_file_data['details'],
            bonus_file_data['date_for_allocation'],
            bonus_file_data['project_code'],
            bonus_file_data['project_data'],
            bonus_info['original_name'])
        response_details = response['bonus_data']


        if correction:
            cleaned_db = clean_bonuses(
                bonus_file_data['date_for_allocation'], bonus_file_data['project_code'], uploader)
            corrected_response = add_money(cleaned_db, response['bonus_data'])
            response_json = {
                'money_data': json.dumps(json.loads(json.dumps(corrected_response), parse_float=lambda x: round(float(x), 2)), ensure_ascii=False),
                'missing_rates': json.dumps(
                    [], ensure_ascii=False),
                'missing_in_file': json.dumps(
                    [], ensure_ascii=False),
            }
        else:
            response_json = {
                'money_data': json.dumps(json.loads(json.dumps(response_details), parse_float=lambda x: round(float(x), 2)), ensure_ascii=False),
                'missing_rates': json.dumps(
                    [], ensure_ascii=False),
                'missing_in_file': json.dumps(
                    [], ensure_ascii=False),

            }

        return sanic_json(response_json, response['status'])
    else:
        return text('Nie otrzymałem żadnych plików!', 404)


def check_benefits(period, type):
    query = select(p_benefity).where(
        p_benefity.c.okres_rozliczenia == period,
        p_benefity.c.rodzaj == type
    )
    with engine.begin() as conn:
        query_result = conn.execute(query).first()
    if query_result:
        return True
    else:
        return False


def clear_benefits(period, type):
    with engine.begin() as conn:
        conn.execute(delete(p_benefity).where(
            p_benefity.c.okres_rozliczenia == period,
            p_benefity.c.rodzaj == type
        )
        )


@file.post('/api/upload_benefits')
def upload_benefits(request):
    file_received = request.files.get('file')
    correction = True if request.form.get('correction') == 'true' else False
    osoba_wysylajaca = request.form.get('login')
    data_wyslania = datetime.now(tz=local_tz)
    try:
        header_df = pd.read_excel(file_received.body,
                                  nrows=3, header=None, usecols=range(2), names=['id', 'values'], index_col=False)

        okres_rozliczenia = header_df['values'].iloc[2]
        rodzaj_benefitu = header_df['values'].iloc[0]
        existing_benefit = check_benefits(okres_rozliczenia, rodzaj_benefitu)
        if existing_benefit and not correction:
            return text(f"Benefity typu {rodzaj_benefitu} za okres {okres_rozliczenia} już zostały załadowane do bazy danych! Kontynuacja oznacza usunięcie i zastąpienie już istniejących rekordów!", 202)

        if correction:
            clear_benefits(okres_rozliczenia, rodzaj_benefitu)

        df = pd.read_excel(file_received.body, header=4,
                           dtype=str).replace({np.nan: None})
        df['rodzaj'] = rodzaj_benefitu
        df['okres_rozliczenia'] = okres_rozliczenia

        benefit_dict = df.to_dict('records')
        materialized_people_url = f"https://{address}/v1/materialized_people/"
        materialized_people_request = session.get(
            url=materialized_people_url, verify=verify_val)
        materialized_people_response = materialized_people_request.json()

        mocarz_ids = []
        for each in benefit_dict:
            if each['mocarz_id'] not in mocarz_ids:
                mocarz_ids.append(each['mocarz_id'])
        materialized_people = [
            obj for obj in materialized_people_response if obj['mocarz_id'] in mocarz_ids]
        with engine.begin() as conn:
            for each in benefit_dict:
                for person in materialized_people:
                    if each['mocarz_id'] == person['mocarz_id']:
                        lokalizacja = person['operation_center']
                        person_request = session.get(
                            url=f"{person_url}/{each['mocarz_id'][3:]}", verify=verify_val)
                        person_response = person_request.json()
                        each['CO'] = person_response['operation_center']['name']
                        conn.execute(insert(p_benefity).values(
                            mocarz_id=each['mocarz_id'],
                            okres_rozliczenia=each['okres_rozliczenia'],
                            rodzaj=each['rodzaj'],
                            imie_i_nazwisko=each['imie_i_nazwisko'],
                            pesel=each['PESEL'],
                            centrum_operacyjne=lokalizacja,
                            kwota=each['kwota'],
                            komentarz=each['komentarz'],
                            osoba_wysylajaca=osoba_wysylajaca,
                            data_wyslania=data_wyslania
                        ))

        return text('Benefity zostały poprawnie załadowane!')
    except Exception as e:
        raise SanicException(
            f"Wygląda na to, że jest jakiś problem z załadowaniem benefitów. Szczegóły: {e}", 422)


def read_file(extension, body, file_name, file_type):
    missing = Missing()

    def get_excel_header_data(header_nr=None):
        data = pd.read_excel(body, sheet_name='LP', header=header_nr,
                             nrows=1, usecols=range(2), names=['id', 'values'], index_col=False)['values'].iloc[0]
        return data

    def get_csv_header_data(header_nr=None):
        data = pd.read_csv(StringIO(body.decode('utf-8')), header=header_nr,
                           nrows=1, usecols=range(2), names=['id', 'values'])['values'].iloc[0]
        return data
    try:
        if extension == 'xlsx':
            code = get_excel_header_data()
        else:
            code = get_csv_header_data()
        project_response_details = [obj for obj in project_response if
                                    obj['project_code'] == code]
        if (len(project_response_details) > 0):
            project_data = project_response_details[0]
        else:
            missing.projekt_kod_plik = code
            missing.problem = 'Taki projekt nie istnieje w Mocarzu'
            insert_mistakes(missing)
            raise SanicException(
                f"Projektu o kodzie {code} nie ma w Mocarzu", status_code=422)
        if extension == 'xlsx':
            # code = get_excel_header_data()
            okres_rozliczenia = get_excel_header_data(1)
            if file_type == values['stawki']:
                columns_to_use = ['data', 'mocarz_id', 'imie_i_nazwisko', 'PESEL', 'suma_godzin',
                                  'w_tym_nieEFE', 'w_tym_szkoleniowe', 'szkolenia_wstepne', 'wsparcie', 'uwagi']
            else:
                columns_to_use = ['mocarz_id', 'imie_i_nazwisko',
                                  'PESEL', 'kwota', 'kategoria', 'komentarz']

            read = pd.read_excel(body, header=4,
                                 sheet_name='LP', usecols=lambda x: x in columns_to_use).replace({np.nan: None})
            read['mocarz_id'] = read['mocarz_id'].str.strip()
            if 'suma_godzin' in read:
                # 'coerce' replaces non-numeric values with NaN
                read['suma_godzin'] = pd.to_numeric(
                    read['suma_godzin'], errors='coerce')
                read['suma_godzin'] = read['suma_godzin'].apply(
                    lambda x: float("{:.2f}".format(x)) if not np.isnan(x) else 0.0)
            data = read.to_dict('records')
            if file_type == values['stawki']:
                try:
                    for each in data:
                        each['data'] = each['data'].strftime("%Y-%m-%d")
                except KeyError:
                    raise SanicException(
                        f"W pliku brakuje potrzebnych kolumn. Upewnij się, że przypadkiem nie dodałeś/aś pliku z dodatkami w miejscu pliku dla stawek i że plik zawiera wszystkie niezbędne kolumny!", 422)
        else:
            code = get_csv_header_data()
            okres_rozliczenia = get_csv_header_data(1)
            dtypes = {
                'mocarz_id': 'category',
                'data': 'category',
                'imie_i_nazwisko': 'category',
                'PESEL': pd.Int64Dtype(),
                'suma_godzin': 'category',
                'w_tym_nieEFE': 'category',
                'w_tym_szkoleniowe': 'category',
                'uwagi': 'string',
            }
            if file_type == values['stawki']:
                fields = ['data', 'mocarz_id', 'imie_i_nazwisko', 'PESEL',
                          'suma_godzin', 'w_tym_nieEFE', 'w_tym_szkoleniowe', 'szkolenia_wstepne', 'wsparcie', 'uwagi']
            else:
                fields = ['mocarz_id', 'imie_i_nazwisko',
                          'PESEL', 'kwota', 'kategoria', 'komentarz']
            read = pd.read_csv(StringIO(body.decode(
                'utf-8')), dtype=dtypes, names=fields, header=4, index_col=False).replace({np.nan: None})
            read['mocarz_id'] = read['mocarz_id'].str.strip()
            if file_type == values['stawki']:
                read['w_tym_nieEFE'] = read['w_tym_nieEFE'].fillna("0,00")
                read['w_tym_szkoleniowe'] = read['w_tym_szkoleniowe'].fillna(
                    "0,00")
                read['szkolenia_wstepne'] = read['szkolenia_wstepne'].fillna(
                    "0,00")
                read['wsparcie'] = read['wsparcie'].fillna("0,00")
                # read['data'] = pd.to_datetime(read['data'], format='%d.%m.%Y').astype(str)
                try:
                    read['data'] = pd.to_datetime(
                        read['data'], format='%d.%m.%Y', errors='raise').astype(str)
                # do something
                except ValueError:
                    read['data'] = pd.to_datetime(
                        read['data'], format='%Y-%m-%d', errors='raise').astype(str)

                if 'suma_godzin' in read:
                    read['suma_godzin'] = read['suma_godzin'].apply(
                        lambda x: float(x.split()[0].replace(',', '.')) if isinstance(x, str) else x).astype(float)

                if 'kwota' in read:
                    read['kwota'] = read['kwota'].apply(
                        lambda x: float(x.split()[0].replace(',', '.')) if isinstance(x, str) else x).astype(float)

                if 'w_tym_nieEFE' in read:
                    read['w_tym_nieEFE'] = read['w_tym_nieEFE'].apply(
                        lambda x: float(x.split()[0].replace(',', '.')) if isinstance(x, str) else x).astype(float)
                if 'w_tym_szkoleniowe' in read:
                    read['w_tym_szkoleniowe'] = read['w_tym_szkoleniowe'].apply(
                        lambda x: float(x.split()[0].replace(',', '.')) if isinstance(x, str) else x).astype(float)
                if 'szkolenia_wstepne' in read:
                    read['szkolenia_wstepne'] = read['szkolenia_wstepne'].apply(
                        lambda x: float(x.split()[0].replace(',', '.')) if isinstance(x, str) else x).astype(float)
            else:
                if 'kwota' in read:
                    read['kwota'] = read['kwota'].apply(
                        lambda x: float(x.split()[0].replace(',', '.')) if isinstance(x, str) else x).astype(float)
                if 'data' in read:
                    raise SanicException("Zły plik", 422)
            data = read.to_dict('records')
        # date_for_allocation = header_info(body)['period'].split('-')
        return {
            'date_for_allocation': okres_rozliczenia,
            'project_code': code,
            'project_data': project_data,
            'details': data
        }
    except pd.errors.ParserError as pd_e:
        missing.problem = f"Problem z plikiem: {pd_e}"
        missing.nazwa_pliku = file_name
        insert_mistakes(missing)
        raise SanicException(f"Problem z parsowaniem pliku: {pd_e}", 422)
    except TypeError as t_e:
        missing.problem = f"Problem z plikiem: {t_e}"
        missing.nazwa_pliku = file_name
    except ValueError as v_e:
        missing.problem = f"Problem z plikiem: {v_e}"
        missing.nazwa_pliku = file_name
        raise SanicException(
            f"Niektóre kolumny zawierają niewłaściwe dane. Upewnij się, że przypadkiem nie dodałeś/aś pliku ze stawkami w miejscu pliku dla dodatków i że wszystkie kolumny zawierają właściwe dane!", 422)
    except Exception as e:
        missing.problem = f"Problem z plikiem: {e}"
        missing.nazwa_pliku = file_name
        insert_mistakes(missing)
        raise SanicException(f"Problem z plikiem: {e}", 422)


@file.post('/api/missing_ids_details')
def get_details(request):
    id = request.json['id']
    with engine.begin() as conn:
        details = conn.execute(select(p_bledy).where(
            p_bledy.c.missing_id == id)).fetchall()
    details_json = json.dumps([dict(d._mapping)
                              for d in details], default=str, ensure_ascii=False)
    return sanic_json(details_json)


# funkcja do usuwania rekordów które już istnieją w bazie danych (listy płac wysłane do zatwierdzenia)
# Sprawdza daną tabelę (p_do_zatwierdzenia) i usuwa z niej wszystkie rekordy dla danego projektu za dany okres czasu
# Funkcja powinna być tymczasowa, dopóki nie naprawi się funkcji correct_data
def remove_conflicting_records(table, date, project_code, deleter):
    trace_deletion(code=project_code, date=date, deleter=deleter,
                   reason='Ponowne wgranie wpliku z godzinami.')
    with engine.begin() as conn:
        conn.execute(
            delete(
                table
            ).where(
                table.c.okres_rozliczenia == date,
                table.c.project_code == project_code
            )
        )

# Ta funkcja zapobiega podwójnemu naliczaniu bonusów i zwracaniu niepoprawnych wartości podczas ponownego wysyłania pliku z bonusami
# W przeciwieństwie do remove_conflicting_records nie usuwa całego rekordu z bazy danych, ale pobiera go, parsuje i usuwa tylko informacje o bonusach
# Następnie wypłaty są ponownie przeliczane i zwracane do ponownego użytku


def clean_bonuses(date, code, uploader):
    with engine.begin() as conn:
        result = conn.execute(select(p_do_zatwierdzenia).where(
            p_do_zatwierdzenia.c.okres_rozliczenia == date,
            p_do_zatwierdzenia.c.project_code == code
        )).first()
    deleting_reason = f"Nowy plik z bonusami wgrany przez {uploader}. Informacje o bonusach zostały zastąpione."
    trace_deletion(code=code, date=date, deleter=uploader,
                   reason=deleting_reason)
    from_db = json.loads(result.dane)
    prev_bonus = from_db['total_bonus']
    prev_total = from_db['complete_total']
    from_db['total_bonus'] = 0
    new_total = float(prev_total) - float(prev_bonus)
    from_db['complete_total'] = new_total
    for db in from_db['details']:
        if db['bonusy']:
            prev_suma_bonusow = db['suma_bonusow']
            prev_total_salary = db['complete_salary']
            new_total_salary = float(prev_total_salary) - \
                float(prev_suma_bonusow)
            db['complete_salary'] = new_total_salary
            db['suma_bonusow'] = 0
            db['bonusy'] = []
    return from_db
# code, date, deleter, deleting_reason, rejection='N', rejection_reason = None


def trace_deletion(from_zatwierdzone=False, rejection='N', rejection_reason=None, **kwargs):
    def find_deletion_table(table):
        query = select(
            table.c.project_name,
            table.c.osoba_wysylajaca,
            table.c.data_wyslania,
        ).where(
            table.c.project_code == kwargs['code']
        ).where(
            table.c.okres_rozliczenia == kwargs['date']
        )
        return query
    if from_zatwierdzone:
        query_table = p_zatwierdzone
    else:
        query_table = p_do_zatwierdzenia

    with engine.begin() as conn:
        rejection_data = conn.execute(find_deletion_table(query_table)).first()
        if not rejection_data and from_zatwierdzone:
            rejection_data = conn.execute(
                find_deletion_table(p_zatwierdzone_bonusy)).first()
        conn.execute(insert(p_odrzucone).values(
            project_code=kwargs['code'],
            project_name=rejection_data.project_name,
            okres_rozliczenia=kwargs['date'],
            kto_wysylal=rejection_data.osoba_wysylajaca,
            data_wyslania=rejection_data.data_wyslania,
            kto_usunal=kwargs['deleter'],
            data_usuniecia=datetime.now(tz=local_tz),
            powod_usuniecia=kwargs['reason'],
            odrzucenie=rejection,
            powod_odrzucenia=rejection_reason
        ))
        return {'project': rejection_data.project_name,
                'wysylacz': rejection_data.osoba_wysylajaca}


def save_files(body, name, extension, uploader):
    if not os.path.exists(config["upload"]):
        os.makedirs(config["upload"])

    file_name_split = name.split(f".{extension}")
    file_name = f"{file_name_split[0]}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_upload_by_{uploader}"
    file_path = f"{config['upload']}/{file_name}.{extension}"
    with open(file_path, 'wb') as f:
        f.write(body)
        f.close()
