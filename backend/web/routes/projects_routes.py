import os
import json
import requests
from dotenv import load_dotenv
import pytz
from itertools import groupby
from collections import defaultdict
from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic.exceptions import SanicException
from sqlalchemy import select, func, literal_column
from web.db_connection import engine, p_zatwierdzone_bonusy, p_zatwierdzone, p_benefity
from web.routes.file_routes import config, person_url, verify_val
# from web.passes import google_pass

load_dotenv()

projects = Blueprint('projects')

local_tz = pytz.timezone('Europe/Warsaw')
session = requests.Session()
user = os.environ.get('PIERSCIEN_USER')
password = os.environ.get('PIERSCIEN_PASS')
address = os.environ.get('PIERSCIEN_ADDRESS')
exclude = ['HQ', 'PRIMEBOT']
config['download'] = "./web/downloads"
config["data"] = "./web/data_files"

umowy_id = [2, 7]
umowy_z_zus_id = [3]


class Summary():
    def __init__(self) -> None:
        self.mocarz_id = ""
        self.bonus = False
        self.kwota_bonusu = 0.0
        self.umowy = []
        self.umowy_detale = []
        self.zmiana_umow = False


def get_zatwierdzone_info():
    zatwierdzone_query = select(
        p_zatwierdzone.c.project_code,
        p_zatwierdzone.c.okres_rozliczenia,
    ).group_by(
        p_zatwierdzone.c.project_code,
        p_zatwierdzone.c.okres_rozliczenia,
    )
    with engine.begin() as conn:
        zatwierdzone = conn.execute(zatwierdzone_query).fetchall()
    return zatwierdzone


def union_query(table, period=None):
    if not period:
        query = select(
            table.c.okres_rozliczenia
        )
    else:
        query = select(
            table.c.mocarz_id,
            table.c.kwota,
        ).where(
            table.c.okres_rozliczenia == period
        )
    return query


def grouped_query(date):
    query = select(
        p_zatwierdzone.c.mocarz_id,
        p_zatwierdzone.c.rodzaj_umowy,
        func.round(func.sum(p_zatwierdzone.c.suma_godzin),
                   2).label('godziny'),
        func.round(func.sum(p_zatwierdzone.c.kwota), 2).label('hajsy')
    ).where(
        p_zatwierdzone.c.okres_rozliczenia == date
    ).group_by(
        p_zatwierdzone.c.mocarz_id,
        p_zatwierdzone.c.rodzaj_umowy,
    ).having(
        func.sum(p_zatwierdzone.c.kwota) > 0
    )
    return query


def join_query(table, period):
    query = select(
        table.c.project_code,
        func.round(func.sum(table.c.kwota), 2).label('total_salary')
    ).select_from(table).where(
        table.c.okres_rozliczenia == period
    ).group_by(table.c.project_code)
    return query


@projects.get('/api/get_summary/<date>/<co>')
def get_summary(request, date, co):
    session.auth = (user, password)
    # json_file = f"{config['data']}/data.json"
    try:
        if co == 'all':
            query_stawki = grouped_query(date)
            query_bonusy = union_query(p_zatwierdzone_bonusy, date)
            query_benefity = union_query(p_benefity, date)
        else:
            query_stawki = grouped_query(date).where(
                p_zatwierdzone.c.lokalizacja == co)
            query_bonusy = union_query(p_zatwierdzone_bonusy, date).where(
                p_zatwierdzone_bonusy.c.lokalizacja == co)
            query_benefity = union_query(p_benefity, date).where(
                p_benefity.c.centrum_operacyjne == co)
        umowy_url = f"https://{address}/v1/form_of_employment_dicts/"
        umowy_request = session.get(
            url=umowy_url, verify=False)
        umowy_response = umowy_request.json()
        umowy_zlecenia = [u['name']
                          for u in umowy_response if u['id'] in umowy_id]
        union = query_bonusy.union_all(query_benefity)
        total_query = select(
            union.c.mocarz_id,
            func.round(func.sum(union.c.kwota), 2).label('total_sum')
        ).select_from(union).group_by(union.c.mocarz_id)

        with engine.begin() as conn:
            zatwierdzone_stawki = conn.execute(query_stawki).fetchall()
            zatwierdzona_reszta = conn.execute(total_query).fetchall()

        lista_umow = []
        lista_dodatkow = []

        # funkcja sprawdz_kontrakty służy do przemielenia historii kontraktów danego konsultanta i zwrócenia odpowiedniej wartości jeśli były jakieś zmiany w danym okresie
        def sprawdz_kontrakty(kontrakty):
            # tworzymy zmienną "umowa" której domyślna wartość to "None"
            umowa = None
            # najpierw sortujemy tabelę z kontraktami po dacie ich rozpoczęcia, żeby ułatwić ich porównanie z interesującym nas okresem
            sorted_kontrakty = sorted(kontrakty, key=lambda d: d['start_date'])
            rodzaje_umow = []
            # następnie iterujemy przez posegrefowane kontrakty
            # na logikę: jeśli w dacie startu ALBO w dacie końca kontraktu z historii znajduje się interesujący nas okres (np. "2023-08") to znaczy, że zaszły w tym kontrakcie jakieś zmiany, którym trzeba się przyjrzeć
            # dla bezpieczeństwa przyjmujemy takie samo założenie w sytuacji w której np. ktoś pracował na umowie zlecenie od początku roku do miesiąca następującego po okresie, który nas interesuje (np. do "2023-09-01") i w międzyczasie nie miał wgranych żadnych stawek - same bonusy. W takim przypadku Pierścień nie wykryje, że w okresie, który nas interesuje konsultant miał inną, korzystniejszą umowę
            # dlatego na wszelki wypadek dodajemy do interesującego nas okresu jeden miesiąc
            split_date = date.split("-")
            date_year = int(split_date[0])
            date_month = int(split_date[1])
            next_month = str(
                date_month + 1).zfill(2) if date_month + 1 <= 12 else '01'
            next_year = str(
                date_year + 1) if date_month == 12 else str(date_year)
            next_date = f"{next_year}-{next_month}"

            # następnie iterujemy przez posortowane kontrakty i sprawdzamy, czy są w nich daty które pasują do jednego w dwóch utworzonych przez nas okresów
            for sk in sorted_kontrakty:
                if date in str(sk['start_date']) or date in str(sk['end_date']) or next_date in str(sk['start_date']) or next_date in str(sk['end_date']):
                    rodzaje_umow.append(sk['name'])

            # jeżeli interesujący nas okres nie występuje w żadnej z historycznych dat, wtedy kod ignoruje resztę działań i zwraca po prostu wartośc domyślną zmiennej
            if rodzaje_umow:
                # jeżeli okazuje się że dla interesujących nas okresów było więcej niż jedna zmiana, sprawdzamy czy którakolwiek ze zmienionych wtedy umów pasuje do umów zlecenie z Mocarza
                # umowy zlecenia są pobierane w oddzielnym requeście na początku procesowania danych z endpointu orm_of_employment_dicts
                # dla celów Pierścienia uznałem, że interesujące nas umowy to "Umowa zlecenie" (id umowy: 2) i "Uz zdrowotna" (id umowy: 7) zgodnie z wytycznymi PMa
                # jeżeli żadna z historycznych umów nie pasuje, dla umowy pozostaje domyślna wartość None
                if len(rodzaje_umow) > 1:
                    umowa = next(
                        (u for u in rodzaje_umow if u in umowy_zlecenia), None)
                else:
                    # jeśli w interesującym nas okresie była tylko jedna umowa (zakładam, że to tylko w wypadku kiedy jest np. start_date: "2023-08-01" a end_date:null, w każdym innym wypadku powinny być dodatkowe daty), automatycznie zwracamy wartośc tej umowy (bo obowiązywała ona w interesującym nas okresie)
                    umowa = rodzaje_umow[0]
            return umowa

        groups = defaultdict(list)
        for obj in zatwierdzone_stawki:
            groups[obj.mocarz_id].append(obj)

        for value in groups.values():
            summary = Summary()
            summary.mocarz_id = value[0].mocarz_id
            for v in value:
                summary.umowy.append(str(v.rodzaj_umowy).upper())
                summary.umowy_detale.append({
                    'umowa': v.rodzaj_umowy,
                    'suma': v.hajsy,
                    # 'stawka': v.stawka_za_dzien,
                    'liczba_godzin': v.godziny
                })

            # Poniżej usuwamy duplikaty z listy umów - bo może się okazać, że konsultant może mieć na kilku projektach różne rodzaje umowy z ZUS (np. umowa z ZUS bez wyrównania czy coś takiego)
            summary.umowy = list(dict.fromkeys(summary.umowy))
            if len(summary.umowy) > 1:
                summary.zmiana_umow = True
            lista_umow.append(vars(summary))

        for val in zatwierdzona_reszta:
            bonus_summary = Summary()
            bonus_summary.bonus = True
            bonus_summary.kwota_bonusu = val.total_sum
            bonus_summary.mocarz_id = val.mocarz_id
            lista_dodatkow.append(vars(bonus_summary))

        total_sum = []
        stawki_z_dodatkami_ids = []

        for d in lista_dodatkow:
            for u in lista_umow:
                if d['mocarz_id'] == u['mocarz_id']:
                    if u['zmiana_umow']:
                        zlecenie = next((umowa for umowa in u['umowy_detale'] if "ZUS" not in str(
                            umowa['umowa']).upper()), u['umowy_detale'][0])
                    else:
                        zlecenie = u['umowy_detale'][0]
                    zlecenie['suma'] += d['kwota_bonusu']
                    total_sum.append(u)
                    stawki_z_dodatkami_ids.append(u['mocarz_id'])
        stawki_z_dodatkami_ids = list(dict.fromkeys(stawki_z_dodatkami_ids))
        stawki_bez_dodatkow = [
            stawka for stawka in lista_umow if stawka['mocarz_id'] not in stawki_z_dodatkami_ids]
        dodatki_bez_stawek = [
            b for b in lista_dodatkow if b['mocarz_id'] not in stawki_z_dodatkami_ids]
        total_sum.extend(stawki_bez_dodatkow)
        total_sum.extend(dodatki_bez_stawek)
        id_list = [s['mocarz_id'] for s in total_sum]
        id_list = list(dict.fromkeys(id_list))
        materialized_people_url = f"https://{address}/v1/materialized_people/"
        materialized_people_request = session.get(
            url=materialized_people_url, verify=False)
        materialized_people_response = materialized_people_request.json()
        materialized_people = [
            obj for obj in materialized_people_response if obj['mocarz_id'] in id_list]
        summary_data = []
        for ts in total_sum:
            for person in materialized_people:
                if ts['mocarz_id'] == person['mocarz_id']:
                    if not ts['bonus']:
                        for u in ts['umowy_detale']:
                            zus = 'TAK' if 'ZUS' in str(
                                u['umowa']).upper() else '0'
                            lider = 'TAK' if "leader" in person['last_contract_title'].lower(
                            ) else '0'
                            summary_data.append({
                                'nazwisko': person['last_name'],
                                'imie': person['first_name'],
                                'zus': zus,
                                'lider': lider,
                                'pesel': person['pesel'],
                                'kwota_brutto': u['suma'],
                                'umowa': u['umowa'] if u['umowa'] else person['last_contract_employment_form']
                            })

                    else:
                        # ogariamy ludzi, którzy wg bazy danych za poprzedni miesiąc nie mieli wpisanych żadnych stawek, tylko dodatki/benefity
                        # sprawdzamy czy w endpoincie "/materialized_people" w polu ostatniej umowy jest wpisany ZUS
                        # jeśli tak, ustalamy że zus to "TAK" (tymczasowo)
                        zus = 'TAK' if 'zus' in person['last_contract_employment_form'].lower(
                        ) else '0'
                        # to samo z pozycją liderską - jeśli jego ostatnia nazwa stanowiska zawiera w sobie słowo "leader" to przypisujemy mu lidera
                        lider = 'TAK' if "leader" in person['last_contract_title'].lower(
                        ) else '0'
                        # dla każdej osoby odpalamy request do Mocarza do endpointu persons/ jako identyfikator używając ich mocarz ID
                        # mocarz ID trzeba najpierw "oczyścić" z przedrostka "VCC" żeby to działało
                        person_request = session.get(
                            url=f"{person_url}/{ts['mocarz_id'][3:]}", verify=verify_val)
                        # z endpointu persons danej osoby bierzemy tylko jego historię podpisanych umów
                        historia_kontraktow = person_request.json()[
                            'contract_set']
                        # używając pobranych kontraktów odpalamy funkcję sprawdź kontrakty
                        kontrakt_do_optimy = sprawdz_kontrakty(
                            historia_kontraktow)
                        if kontrakt_do_optimy:
                            zus = 'TAK' if 'zus' in kontrakt_do_optimy.lower() else '0'
                        # w zależności od tego co zwróci funkcja sprawdz_kontrakty do ostatecznej odpowiedzi ze strony serwera trafi inna wartość umowy:
                        # jeśli w funkcji sprawdz_kontrakty zostanie zwrócona wartość inna niż domyślne None, ta wartość będzie traktowana jako obowiązująca za dany okres umowa
                        # jeśli zwrócone zostanie None, jako obowiązująca umowa zostanie traktowane pole "last_contract_employment_form" z endpointu materialized_people w Mocarzu
                        summary_data.append({
                            'nazwisko': person['last_name'],
                            'imie': person['first_name'],
                            'zus': zus,
                            'lider': lider,
                            'pesel': person['pesel'],
                            'kwota_brutto': ts['kwota_bonusu'],
                            'umowa': kontrakt_do_optimy if kontrakt_do_optimy else person['last_contract_employment_form']
                        })

        sorted_summary = sorted(summary_data, key=lambda d: d['nazwisko'])
        return sanic_json(json.dumps(sorted_summary, ensure_ascii=False))
    except StopIteration:
        raise SanicException(f'Nie udało się pobrać podsumowania', 422)
    except Exception as e:
        raise SanicException(f'Nie udało się pobrać podsumowania - {e}', 422)


@projects.get('/api/get_dates')
def get_dates(request):
    query_zatwierdzone = union_query(p_zatwierdzone)
    query_bonusy = union_query(p_zatwierdzone_bonusy)
    query_benefity = union_query(p_benefity)
    union = query_zatwierdzone.union_all(query_bonusy, query_benefity)
    with engine.begin() as conn:
        result = conn.execute(union).fetchall()
    dates = list(dict.fromkeys([d.okres_rozliczenia for d in result]))
    dates.sort(reverse=True)
    result = json.dumps(
        dates, ensure_ascii=False)
    return sanic_json(result)


@projects.get('/api/get_projects/<date>')
def get_projects(request, date):
    def key_handler(d):
        return d['location']

    def benefit_query(rodzaj):
        query = select([p_benefity.c.centrum_operacyjne, func.sum(p_benefity.c.kwota).label('total_benefit')]).\
            where(p_benefity.c.rodzaj == rodzaj).\
            where(p_benefity.c.okres_rozliczenia == date).\
            group_by(p_benefity.c.centrum_operacyjne)
        return query

    def assign_benefits(project, table):
        total_benefit = 0.0
        for benefit in table:
            if project['name'] == benefit.centrum_operacyjne:
                total_benefit = benefit.total_benefit
        return total_benefit


    def find_projects(table):
        query = select(table.c.project_code).where(table.c.okres_rozliczenia == date
                                                        ).group_by(table.c.project_code
                                                                   ).order_by(table.c.project_code)
        return query

    with engine.begin() as conn:
        projekty_z_bazy = [p.project_code for p in conn.execute(find_projects(p_zatwierdzone)).fetchall()]
        projekty_z_bonusow = [pb.project_code for pb in conn.execute(find_projects(p_zatwierdzone_bonusy)).fetchall()]

    projekty_z_bazy.extend(projekty_z_bonusow)
    session.auth = (user, password)
    project_url = f"https://{address}/v1/projects/"
    project_request = session.get(url=project_url, verify=False)
    project_response = project_request.json()
    project_data = sorted(
        [obj for obj in project_response if obj['project_code'] in projekty_z_bazy and obj['location'] not in exclude], key=key_handler)
    project_dict = {}
    for key, value in groupby(project_data, key_handler):
        project_dict[key] = list(value)

    # Tworzenie zapytania dla subquery_t1
    subquery_t1 = select([p_zatwierdzone.c.project_code, func.sum(p_zatwierdzone.c.kwota).label('total_rbh'),
                          func.sum(p_zatwierdzone.c.koszt).label('total_cost'),
                          func.sum(p_zatwierdzone.c.kwota_z_kosztem).label('total_with_cost')
                          ]).\
        where(p_zatwierdzone.c.okres_rozliczenia == date).\
        group_by(p_zatwierdzone.c.project_code).\
        alias('t1')

    # Tworzenie zapytania dla subquery_t2
    subquery_t2 = select([p_zatwierdzone_bonusy.c.project_code, func.sum(p_zatwierdzone_bonusy.c.kwota).label('total_bonus')]).\
        where(p_zatwierdzone_bonusy.c.okres_rozliczenia == date).\
        group_by(p_zatwierdzone_bonusy.c.project_code).\
        alias('t2')

    # Tworzenie głównego zapytania
    def create_joined_query(jt1, jt2):
        query = select([
            jt1.c.project_code,
            func.coalesce(subquery_t1.c.total_rbh,
                          literal_column('0.0')).label('total_rbh'),
            func.coalesce(subquery_t1.c.total_cost,
                          literal_column('0.0')).label('total_cost'),
            func.coalesce(subquery_t2.c.total_bonus,
                          literal_column('0.0')).label('total_bonus')
        ]).\
            select_from(jt1).\
            outerjoin(jt2, jt2.c.project_code ==
                      jt1.c.project_code)
        return query
    with engine.begin() as conn:
        total_result = conn.execute(create_joined_query(
            subquery_t1, subquery_t2)).fetchall()
        total_result_2 = conn.execute(create_joined_query(
            subquery_t2, subquery_t1)).fetchall()
        total_result.extend(total_result_2)
        print(total_result)
        total_result = list(dict.fromkeys(total_result))
        total_luxmed = conn.execute(
            benefit_query('luxmed')
        ).fetchall()
        total_multisport = conn.execute(
            benefit_query('multisport')
        ).fetchall()
        total_mgm = conn.execute(
            benefit_query('mgm')
        ).fetchall()
    info = [str(d['project_code']) for d in total_result]
    new_result = {}
    for row in total_result:
        new_result[row.project_code] = {
            'total_rbh': row.total_rbh,
            'total_cost': row.total_cost,
            'total_bonus': row.total_bonus,
            'total_salary': round(float(row.total_rbh) + float(row.total_bonus), 2)
        }
    project_table = []
    combined_salary = 0.0
    for location, value in project_dict.items():
        response = {}
        zatwierdzone = []
        zatwierdzone_details = []
        # total_salary = 0.0
        total_rbh = 0.0
        total_cost = 0.0
        total_bonuses = 0.0
        for project in value:
            if project['project_code'] in info:
                zatwierdzone.append(project['project_code'])
                for key, item in new_result.items():
                    if key == project['project_code']:
                        rbh = round(float(item['total_rbh']), 2)
                        bonuses = round(float(item['total_bonus']), 2)
                        cost = round(float(item['total_cost']), 2)
                        zatwierdzone_details.append({
                            'project_code': project['project_code'],
                            'project_name': project['name'],
                            'rbh': rbh,
                            'bonuses': bonuses,
                            'cost': cost,
                            'total': rbh + cost + bonuses
                        })
                        # total_salary += float(item['total_salary'])
                        total_rbh += float(item['total_rbh'])
                        total_cost += float(item['total_cost'])
                        total_bonuses += float(item['total_bonus'])

            else:
                project['zatwierdzony'] = False
        response['name'] = location
        response['total'] = len(value)
        response['zatwierdzone'] = len(zatwierdzone)
        response['zatwierdzone_details'] = zatwierdzone_details
        response['percentage'] = round(
            (response['zatwierdzone'] / response['total']) * 100)
        response['total_rbh'] = round(total_rbh, 2)
        response['total_cost'] = round(total_cost, 2)
        response['total_bonuses'] = round(total_bonuses, 2)
        response['total_salary'] = 0.0
        project_table.append(response)
    for project in project_table:
        total_project_salary = 0.0
        luxmed = round(assign_benefits(project, total_luxmed), 2)
        multisport = round(assign_benefits(project, total_multisport), 2)
        mgm = round(assign_benefits(project, total_mgm), 2)
        project['total_luxmed'] = luxmed
        project['total_multisport'] = multisport
        project['total_mgm'] = mgm
        total_project_salary = project['total_rbh'] + project['total_cost'] +\
            project['total_bonuses'] + luxmed + \
            multisport + mgm
        project['total_salary'] = round(total_project_salary, 2)
        combined_salary += total_project_salary
    response_dict = {
        'projects': project_table,
        'combined': round(combined_salary, 2)
    }
    return sanic_json(json.dumps(json.loads(json.dumps(response_dict), parse_float=lambda x: round(float(x), 2)), ensure_ascii=False))
