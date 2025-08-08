import functools

from django.contrib.sessions.middleware import SessionMiddleware

from .nakyma import Ilmoitukset


@functools.wraps(SessionMiddleware.process_response)
def process_response(self, request, response):
  '''
  Lähetä Celery-viestikanavaan tieto istunnolle tallennetuista,
  mahdollisista uusista viesteistä.

  Huomaa, että tämä on tehtävä vasta istunnon tallentamisen jälkeen,
  jotta viestit ovat luettavissa (Websocket-pyynnöllä) silloin, kun
  viestikanavaa kuunteleva Celery-istunto saa tämän tiedon.
  '''
  # pylint: disable=protected-access
  response = process_response.__wrapped__(self, request, response)
  if hasattr(request, 'session') \
  and hasattr(request, '_messages') \
  and request._messages.added_new:
    Ilmoitukset.viestikanava(request.session.session_key).kirjoita_taustalla()
  return response


SessionMiddleware.process_response = process_response
