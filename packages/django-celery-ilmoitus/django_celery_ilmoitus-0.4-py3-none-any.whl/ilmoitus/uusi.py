from contextlib import contextmanager
from importlib import import_module

from django.conf import settings
from django.contrib.messages.storage import default_storage

from .nakyma import Ilmoitukset


@contextmanager
def tallenna_asynkroninen_ilmoitus(session_key):
  '''
  Kontekstikäsittelijä viestin lähettämiseen käyttäjälle HTTP-pyynnön
  ulkopuolelta, esim. asynkronisen tausta-ajon yhteydessä.

  Huomaa: tätä kontekstia ei tule käyttää silloin, kun viesti tallennetaan
  HTTP-pyynnön käsittelyn yhteydessä tälle samalle pyynnölle. Silloin tieto
  uudesta viestistä viedään Celery-kanavaan automaattisesti istunnon
  tallentamisen yhteydessä; tässä viety sama tieto aiheuttaa saman viestin
  näkymisen käyttäjälle kahdesti.
  '''
  # Hae käyttäjän istunto ja muodosta keinotekoinen HTTP-pyyntö.
  store = None
  try:
    class Pyynto:
      session = import_module(settings.SESSION_ENGINE).SessionStore(session_key)
    request = Pyynto()
    store = default_storage(request)
  finally:
    # Suoritetaan haluttu toiminto kontekstin sisällä, vaikka viestiajurin
    # muodostus epäonnistuisi. Tällöin `store` on `None`.
    try:
      yield store
    finally:
      if store is not None:
        # Pakota viestien ja istunnon tallennus,
        # sillä tavanomaista HTTP-paluusanomaa ei ole käytettävissä.
        store.update(None)
        request.session.save()

        # Lähetä Celery-viestikanavan kautta mahdolliselle, avoimelle
        # Websocket-yhteydelle tieto uudesta ilmoituksesta.
        Ilmoitukset.viestikanava(session_key).kirjoita_taustalla()
        # if store is not None
      # finally
    # finally
  # def tallenna_asynkroninen_ilmoitus
