#!/usr/bin/env python3

from notifications.messenger import MessengerNotifier
from dotenv import load_dotenv
from os.path import join, dirname, exists
from os import environ, getenv

dotenv_path = join(dirname(__file__), 'conf.env')
if not exists(dotenv_path):
    print("No conf.env found... loading example")
    dotenv_path = join(dirname(__file__), 'conf.env.example')
load_dotenv(dotenv_path)

fbm_settings = {
    'email': getenv("MESSENGER_EMAIL"),
    'password': getenv("MESSENGER_PASSWORD")
}

fbm = MessengerNotifier(**fbm_settings)
fbm.notify("{}: {}".format("Test", "Notification"))
fbm.logout()
