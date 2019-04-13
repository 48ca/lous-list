from twilio.rest import Client

class TwilioNotifier:
    def __init__(self, **kwargs):
        self.sid = kwargs['sid']
        self.token = kwargs['token']
        self.to = kwargs['to']
        self.fm = kwargs['fm']
        self.client = Client(self.sid, self.token)

    def notify(self, message):
        self.client.api.account.messages.create(
            to=self.to,
            from_=self.fm,
            body=message
        )
