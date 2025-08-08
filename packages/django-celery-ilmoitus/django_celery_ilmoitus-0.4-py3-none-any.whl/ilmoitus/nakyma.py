import json

from asgiref.sync import sync_to_async

from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator

# Mikäli pistoke-paketti ei ole käytössä, käytetään Djangon vakio-
# näkymäluokkaa. Tällöin metodi `async def websocket` ei ole ongelma,
# sillä sitä ei tunnisteta HTTP-verbin toteutukseksi.
try:
  from pistoke.nakyma import WebsocketNakyma
  from pistoke import WebsocketProtokolla
except ImportError:
  # pylint: disable=ungrouped-imports
  from django.views.generic import View as WebsocketNakyma
  def WebsocketProtokolla(_f):
    return _f
  # except ImportError


class Ilmoitukset(WebsocketNakyma):

  bootstrap_luokat = {
    'debug': 'alert-info',
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-danger',
  }

  @staticmethod
  def viestikanava(session_key):
    from viestikanava import Viestikanava
    return Viestikanava(
      kanava='django.contrib.messages',
      alikanava=session_key,
    )
    # def viestikanava

  def _ilmoitus(self, ilmoitus):
    ''' Muodosta JSON-yhteensopiva sanoma ilmoituksen tiedoin. '''
    return {
      'level': ilmoitus.level,
      'message': ilmoitus.message,
      'tags': ' '.join((
        self.bootstrap_luokat.get(luokka, luokka)
        for luokka in ilmoitus.tags.split(' ')
      ))
    }
    # def _ilmoitus

  def get(self, request, *args, **kwargs):
    ''' Ajax-toteutus. Palauta JSON-sanoma kaikista ilmoituksista. '''
    # pylint: disable=unused-argument
    storage = messages.get_messages(request)
    return JsonResponse([
      self._ilmoitus(ilmoitus)
      for ilmoitus in storage
    ], safe=False)
    # def get

  @method_decorator(WebsocketProtokolla)
  async def websocket(self, request):
    '''
    Websocket-toteutus. Palauta ilmoituksia sitä mukaa, kun niitä tallennetaan.

    Vaatii pakettien asennuksen: celery-viestikanava, django-pistoke.
    '''
    async def laheta_ilmoitukset(signaali=None):
      ''' Lähetä kaikki olemassaolevat ilmoitukset selaimelle. '''
      # pylint: disable=unused-argument
      def hae_ilmoitukset():
        # pylint: disable=protected-access
        request.session._session_cache = request.session.load()
        request._messages = messages.storage.default_storage(request)
        for ilmoitus in request._messages:
          yield json.dumps(self._ilmoitus(ilmoitus))
        request._messages.update(None)
        request.session.save()
        # def hae_ilmoitukset
      for ilmoitus in await sync_to_async(lambda: list(hae_ilmoitukset()))():
        await request.send(ilmoitus)
        # for ilmoitus in await sync_to_async
      # async def laheta_ilmoitukset

    # Lähetä mahdolliset olemassaolevat ilmoitukset heti.
    await laheta_ilmoitukset()

    # Hae ja lähetä ilmoitukset aina, kun kanavan kautta saadaan signaali.
    async with self.viestikanava(request.session.session_key) as kanava:
      async for __ in kanava:
        await laheta_ilmoitukset()
      # async with Viestikanava

    # async def websocket

  # class Ilmoitukset
