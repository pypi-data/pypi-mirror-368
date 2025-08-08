# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


TALLENNUS = 'django.contrib.messages.storage.session.SessionStorage'


class Ilmoitus(AppConfig):
  name = 'ilmoitus'

  def ready(self):
    if settings.MESSAGE_STORAGE != TALLENNUS:
      raise ImproperlyConfigured(
        f'Ilmoitusten asynkroninen tallennus edellyttää istuntopohjaista'
        f' tallennusta:\n'
        f'settings.MESSAGE_STORAGE != {TALLENNUS}'
      )
    from ilmoitus import viestit  # pylint: disable=unused-import
    # def ready

  # class Ilmoitus
