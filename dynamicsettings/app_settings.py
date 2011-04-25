# -*- coding: utf-8 -*-

from django.conf import settings

#include which settings should be included for dynamicsettings
#a list or tuple of settings modules represented as string
"""Example:

``DYNAMICSETTINGS_INCLUDE_MODULES = ['myapp.app_settings', 'some_globals']``

*Notes*:

- ``myapp.app_settings`` should be an available module in myapp 
  (``myapp/app_settings.py``) somewhere in the project dir or 
  PYTHONPATH
- ``some_globals`` should be an available module either in the 
  project dir or somewhere in the PYTHONPATH: ``some_globals.py``


**Note**: if a settings module provided in DYNAMICSETTINGS_INCLUDE_MODULES is not 
available it will simple not load it and fail silently, continuing with the next provided module or stop. 
Also note that the an app does not necessarily need to be in INSTALLED_APPS setting to load 
its settings.
"""
DYNAMICSETTINGS_INCLUDE_MODULES = getattr(settings, 'DYNAMICSETTINGS_INCLUDE_MODULES', [])

"""Example:

``DYNAMICSETTINGS_INCLUDE_SETTINGS = ['MY_SETTING', 'DEFAULT_CACHE_DURATION']``

*Notes*:

- ``MY_SETTING`` or  ``DEFAULT_CACHE_DURATION`` should be an available setting name
  either the global django settings or in the ones provided in 
  DYNAMICSETTINGS_INCLUDE_MODULES

**Note**: if a setting provided in DYNAMICSETTINGS_INCLUDE_SETTINGS is not 
available it will raise an exception.
"""
DYNAMICSETTINGS_INCLUDE_SETTINGS = getattr(settings, 'DYNAMICSETTINGS_INCLUDE_SETTINGS', [])

DYNAMICSETTINGS_CACHE_TIMEOUT = getattr(settings, 'DYNAMICSETTINGS_CACHE_TIMEOUT', 300)
