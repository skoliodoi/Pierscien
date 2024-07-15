from web.routes.file_routes import config, yag
import os
import shutil


def pack_and_send():
    receivers = []
    cc_users = []
    if os.path.exists(config["upload"]):
        attachment = shutil.make_archive('test', 'zip', config['upload'])
        yag.send(receivers=receivers, cc=cc_users, contents='W załączniku pliki wrzucone do Pierścienia', subject='Pliki wrzucone do Pierścienia', attachments=attachment)
        shutil.rmtree(config['upload'])
        os.remove(attachment)