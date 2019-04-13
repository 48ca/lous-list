from fbchat import Client
from fbchat.models import ThreadType

class MessengerNotifier:
    def __init__(self, **kwargs):
        self.email = kwargs['email']
        self.password = kwargs['password']
        self.client = Client(self.email, self.password)

    def notify(self, message):
        self.client.sendMessage(message, self.client.uid, thread_type=ThreadType.USER)

    def logout(self):
        self.client.logout()
