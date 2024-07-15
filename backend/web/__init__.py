from sanic import Sanic
from sanic.worker.manager import WorkerManager
from .routes.file_routes import file
from .routes.projects_routes import projects
from .routes.user_routes import users
from .schedules.scheduled_actions import pack_and_send
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv


load_dotenv()



def create_app():
    scheduler = BackgroundScheduler(timezone='Europe/Warsaw')
    scheduler.start()
    WorkerManager.THRESHOLD = 1000
    app = Sanic("pierscien_backend")
    # Get the logger associated with your Sanic app   
    app.config.CORS_ORIGINS = '*'
    app.config.SECRET = os.environ.get('SAFETY_KEY')
    app.blueprint(file)
    app.blueprint(projects)
    app.blueprint(users)
    scheduler.add_job(pack_and_send, 'cron', minute=0, hour=0, day=10)

    return app
