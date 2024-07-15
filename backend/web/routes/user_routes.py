import os
import requests
from ldap3 import Server, Connection, ALL, NTLM
from ldap3.core.exceptions import LDAPBindError, LDAPUnknownAuthenticationMethodError
from dotenv import load_dotenv
from sanic.response import json as sanic_json, text
from sanic.exceptions import Unauthorized, NotFound, BadRequest
from sqlalchemy import select, insert
from sanic import Blueprint
from sanic.exceptions import BadRequest
from web.routes.file_routes import person_url, yag
from web.db_connection import engine, p_users, p_track_logins
from datetime import datetime
import pytz

load_dotenv()


users = Blueprint('users')

server_uri = 'ldap://192.168.100.2'

server = Server(server_uri, get_info=ALL)
local_tz = pytz.timezone('Europe/Warsaw')
class User():
  def __init__(self) -> None:
    self.mocarz_id = None
    self.imie = None
    self.nazwisko = None
    self.login = None
    self.mail = None
    self.access = None
    self.co = "Niepotrzebne, można zignorować"
    

@users.post('/api/check_user')
def check_user(request):
    data = request.json
    # print(user_nameuser)
    try:
      conn = Connection(server, f"vcc\\{data['login']}", data["password"], authentication=NTLM, auto_bind=True)
      
      select_query = select(p_users).where(
        p_users.c.login == data['login']
      )

      track_login_query = insert(
        p_track_logins
      ).values(
        login = data['login'],
        czas_logowania = datetime.now(tz=local_tz)
      )

      with engine.begin() as conn:
        db_user = conn.execute(select_query).first()
        
      if db_user:
        with engine.begin() as conn:
          conn.execute(track_login_query)
        response_text = {
          'access': db_user.access,
          'name': db_user.imie
          }
        return sanic_json(response_text)
      else:
        response_text = "Wygląda na to, że nie masz dostępu do Pierścienia."
        raise Unauthorized(response_text)
    except LDAPBindError:
      response_text = f"Wpisane dane dla użytkownika \"{data['login']}\" są niepoprawne. Proszę, spróbuj jeszcze raz i upewnij się, że podane dane logowania są poprawne!"
      raise NotFound(response_text)
    except LDAPUnknownAuthenticationMethodError:
      response_text = f"Dane logowania niekompletne"
      raise BadRequest(response_text)
    
@users.post('/api/request_access')
def request_access(request):
  receivers = []
  session = requests.Session()
  login = request.json['login']
  req_access = request.json['access']
  user = os.environ.get('PIERSCIEN_USER')
  address = os.environ.get('PIERSCIEN_ADDRESS')
  password = os.environ.get('PIERSCIEN_PASS')
  session.auth = (user, password)
  try:
    user = User()
    person_request = session.get(url=f"{person_url}/", verify=False)
    person_response = person_request.json()
    person_details = [user for user in person_response if
                                  str(user['login']).lower() == str(login).lower()]
    person = person_details[0]
    if req_access == 'zatwierdzacz':
      co_url = f"https://{address}/v1/center_operation_dicts/{person['operation_center']}"
      co_request = session.get(url=co_url, verify=False)
      co_response = co_request.json()
      user.co = co_response['name']

    user.imie = person['first_name']
    user.nazwisko = person['last_name']
    user.mocarz_id = f"VCC{str(person['id']).zfill(5)}"
    user.login = login
    user.mail = person['mail_teams_priv']
    user.access = req_access
    content = f"""Cześć,
    Dostajesz tę wiadomość, bo jeden z użytkowników zażyczył sobie dostępu do Pierścienia. 
    Dane użytkownika:
    Imię: {user.imie}
    Nazwisko: {user.nazwisko}
    Login: {user.login}
    Mocarz ID: {user.mocarz_id}
    Adres e-mail: {user.mail}
    Wymagany dostęp: {user.access}
    Lokalizacja (opcjonalnie): {user.co}

    Pozdrawiam serdecznie,
    Robot
    """
    yag.send(to=receivers, subject=f"{user.imie} {user.nazwisko} ({user.login}) chce dostępu do Pierścienia!", contents=content)
    return text('Got it', 200)
  except Exception as e:
    raise BadRequest(f"Coś poszło nie tak! {e}")