from sqlalchemy import create_engine, MetaData, Table
from dotenv import load_dotenv
import os
# from web.passes import google_pass

load_dotenv()

db_pass = os.environ.get('DB_PASSWORD')

engine = create_engine(
    f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{db_pass}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_DATABASE')}?charset=utf8mb4", echo=True)


# metadata = MetaData(engine)
metadata = MetaData(engine)

p_do_zatwierdzenia = Table('p_do_zatwierdzenia', metadata, autoload=True)
p_benefity = Table('p_benefity', metadata, autoload=True)
# p_do_zatwierdzenia = Table('p_do_zatwierdzenia_test', metadata, autoload=True)
p_zatwierdzone = Table('p_zatwierdzone', metadata, autoload=True)
p_zatwierdzone_json = Table('p_zatwierdzone_json', metadata, autoload=True)
p_anulowane_json = Table('p_anulowane_json', metadata, autoload=True)
p_zatwierdzone_bonusy = Table('p_zatwierdzone_bonusy', metadata, autoload=True)
p_odrzucone = Table('p_odrzucone', metadata, autoload=True)
p_zatwierdzacze = Table('p_zatwierdzacze', metadata, autoload=True)
p_users = Table('p_users', metadata, autoload=True)
p_bledy = Table('p_bledy', metadata, autoload=True)
p_track_logins = Table('p_track_logins', metadata, autoload=True)

