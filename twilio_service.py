from twilio.rest import Client
from config import Config

class TwilioService:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

    def send_sms(self, to, from_, body):
        message = self.client.messages.create(
            body=body,
            from_=from_,
            to=to
        )
        return message.sid

    def make_call(self, to, from_, url):
        call = self.client.calls.create(
            to=to,
            from_=from_,
            url=url
        )
        return call.sid

    def lookup_number(self, number):
        return self.client.lookups.phone_numbers(number).fetch(type="carrier")
