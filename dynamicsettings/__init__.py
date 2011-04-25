# -*- coding: utf-8 -*-

import pickle
import base64

from django.utils.functional import LazyObject
from django.utils import importlib
from django.core.cache import cache
from django.conf import settings as django_settings

from dynamicsettings import app_settings
from dynamicsettings import models

ALLOWED_TYPES = ['NoneType', 'bool', 'dict', 'list', 'tuple',
                 'float', 'int', 'unicode', 'str', 'long']


#using django's lazysettings approach to load the DynamcSettings lazily, so it
#will not trigger exceptions when syncdb or runserver
#see django.conf.LazySettings
class LazyDynamicSettings(LazyObject):
    """Lazy wrapper for DynamicSettings.
    """
    def _setup(self):
        self._wrapped = DynamicSettings()
    
    
class DynamicSettings(object):
    """A class which is handling the dynamic settings. 
    It is similiar to Django's own conf.settings Settings
    class, but also providing cached settings, setting and
    reseting a setting in the database, returning settings
    as a dict.
    """
    
    def __init__(self):
        self._settings_cache_key = 'dynamicsettings.settings'
        self._settings = cache.get(self._settings_cache_key)
        if self._settings is None:
            self._get_settings()
    
    def get(self, key, default=None):
        """Get a setting value for a partcular key (setting name).
        Works similiar to a dict's ``get`` method.
        
        Params:
            - ``key``: the name of setting
            - ``default`` (optional): a default value if the setting can not be
              retrieved, defaults to ``None``
              
        Returns:
            - the ``value`` of the setting if exists or the value
              specified in ``default``
        """
        return self._settings.get(key, default)
    
    def set(self, key, value, value_type=None):
        """Set a new value for a setting in the database. This
        is only possible for settings defined in 
        ``app_settings.DYNAMICSETTINGS_INCLUDE_SETTINGS``.
        If a setting is set to its original value it will not attempt to 
        save the "change" in the database (since its no real change).
        
        Params:
            - ``key``: the name of the setting
            - ``value``: new new value of the setting
            - ``value_type`` (optional): tne new type of the value, if omitted it will
              try to resolve the type from the value, should be a string
              representing the (Python) type of the setting (for examome
              'int', 'str', 'list' ...)
              
        Returns:
            - the new value of the setting
            
        Raises:
            - ``KeyError`` if the setting can not be set or is not allowed
              to set
        """
        if not value_type:
            value_type = type(value).__name__
        if self.can_change(key):
            dynamic_setting, is_new = models.Settings.objects.get_or_create(key=key)
            dynamic_setting.value = base64.b64encode(pickle.dumps(value))
            dynamic_setting.type = value_type
            dynamic_setting.save()
            #refresh the cache
            self._get_settings()
            return dynamic_setting.value
        raise KeyError('Setting "%s" can not be set in the database. If you want to change the setting add it to DYNAMICSETTINGS_INCLUDE_SETTINGS.' % key)
        
    def reset(self, key):
        """Reset the value of a setting saved in the database.
        Does not work for settings which are not saved in the database
        of course.
        
        Params:
            - ``key``: the name of the setting
            
        Returns:
            - a boolean: ``True`` on success, ``False`` if the setting
            could not be reset (either not allowed to reset or not saved
            in the database)
        """
        if self.can_change(key):
            try:
                dynamic_setting = models.Settings.objects.get(key=key)
                dynamic_setting.delete()
                self._get_settings()
                return True
            except models.Settings.DoesNotExist:
                return False
    
    def dict(self, keys=None):
        """Returns a dict representation of the settings
        where the key is the name of the setting and the value
        is its value.
        
        Params:
            - ``keys`` (optional):  a list of setting names (as strings)
              which should be included in the dict. If ommitted will show
              all settings.
        
        Returns:
            - a dict representing the settings
        """
        if keys is None:
            return self._settings
        new_dict = {}
        for key in keys:
            new_dict[key] = self.get(key)
        return new_dict
    
    def is_in_db(self, key):
        """Check if a setting for a given key is saved in the Database
        
        Params:
            - ``key``: the name of the setting
            
        Returns:
            - a boolean: ``True`` if setting is saved in the database,
              ``False`` otherwise
        """
        try:
            models.Settings.objects.get(key=key)
        except models.Settings.DoesNotExist:
            return False
        return True

    def can_change(self, key):
        """Check if a setting for a given key can be changed in the Database
        
        A setting can be change in the database if:
        a) its not in the global settings, but defined in the
        settings from DYNAMICSETTINGS_INCLUDE_MODULES
        OR 
        b) its defined in DYNAMICSETTINGS_INCLUDE_SETTINGS,
        even it is in the global settings
        
        Params:
            - ``key``: the name of the setting
            
        Returns:
            - a boolean: ``True`` if setting can be changed in the database,
              ``False`` otherwise
        """
        try:
            setting_value = self.__getattr__(key)
            if key in app_settings.DYNAMICSETTINGS_INCLUDE_SETTINGS:
                return True
        except AttributeError:
            return True
        return False
            
    def _get_settings(self):
        self._settings = self._combine_settings()
        cache.set(self._settings_cache_key , self._settings, app_settings.DYNAMICSETTINGS_CACHE_TIMEOUT)
    
    def _combine_settings(self):
        all_settings = {}
        external_modules = []
        #first get from global settings
        global_settings = django_settings._wrapped
        global_settings_dict = self._filter_settings(global_settings)
        all_settings.update(global_settings_dict)
        #second use app specific settings
        for module_name in app_settings.DYNAMICSETTINGS_INCLUDE_MODULES:
            settings_module = self._load_settings_module(module_name)
            if settings_module is not None:
                settings_dict = self._filter_settings(settings_module)
                all_settings.update(settings_dict)
        #and finally check within the db
        db_settings_dict = {}
        db_settings = models.Settings.objects.all()
        for db_setting in db_settings:
            db_settings_dict[db_setting.key] = pickle.loads(base64.b64decode(db_setting.value.strip()))
        all_settings.update(db_settings_dict)
        return all_settings
    
    def _load_settings_module(self, settings_module_string):
        settings_module = None
        try:
            settings_module = importlib.import_module(settings_module_string)
        except ImportError:
            pass
        return settings_module
        
    def _filter_settings(self, settings_module):
        settings = {}
        for setting_key, setting_value in settings_module.__dict__.iteritems():
            #ignore private settings and check if setting is simple type
            if type(setting_value).__name__ in ALLOWED_TYPES\
            and not setting_key.startswith('__') and setting_key.isupper():
               settings[setting_key] = setting_value
        return settings
    
    def __getattr__(self, key):
        if key not in self._settings:
            raise AttributeError('\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, key))
        return self._settings[key]

 
settings = LazyDynamicSettings()

