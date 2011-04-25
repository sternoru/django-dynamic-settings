=======================
django-dynamicsettings
=======================

1. Requirements
:::::::::::::::::::::::::::::::::

At the moment *django-dynamic-settings* requires Python_ >2.5 and
Django_ >1.0 to run. If you use Django <1.3 you need to add the 
predecessor for django.contrib.staticfiles app: https://github.com/jezdez/django-staticfiles

2. Installation
:::::::::::::::::::::::::::::::::

Simply run:
::
    
    python setup.py install
    


You can also obtain django-dynamic-settings via:

::
    
    pip install django-dynamic-settings
    
or

::
    
    easy_install django-dynamic-settings
    


3. Setup
:::::::::::::::::::::::::::::::::

If you installed *django-dynamic-settings* you can already
use it like you are used to python modules. That lets you
make advantage of the internal caching for settings.

If you want to do more (save settings in the database,
check settings in the admin, run tests) you need to do the
following:

**1.** Put ``'dynamicsettings'`` into your ``INSTALLED_APPS``. Make sure
``django.contrib.admin`` (and requirements) is appearing in your 
``INSTALLED_APPS`` setting as well, since its used by
*django-dynamic-settings*:

::
    
    INSTALLED_APPS = (
        ...
        'django.contrib.sessions',
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.staticfiles', #django >1.3, for django <1.3 use 'staticfiles'
        ...
        'dynamicsettings',
        ...
    )
    

**2.** Add a url handler to handle the admin views of 
*django-dynamic-settings*. This is built-in into the standard
django admin, so you could add something like this:

::
    
    urlpatterns = patterns('', 
        ...
        url(r'^admin/settings/', include('dynamicsettings.urls')),
        url(r'^admin/', include(admin.site.urls)),
        ...
    )
    

3. Add settings:

If you have another app which has settings you want to include or 
your custom app is using *django-dynamic-settings* and has
some custom settings, you can include these modules to be handled
by *django-dynamic-settings*:

::
    
    DYNAMICSETTINGS_INCLUDE_MODULES = ['myapp.app_settings', 'globals']
    

In this case ``'myapp.app_settings'`` would be the string
representation of ``myapp.app_settings`` module which should
be available via your PYTHONPATH. The same goes for the
``'globals'`` module.
Now you can view the value of these settings within your 
admin interface as well.

If you also want to edit settings and save them in the database
you have to add the names of the settings which can be edited.
For example:

::
    
    DYNAMICSETTINGS_INCLUDE_SETTINGS = ['MY_SETTING', 'DEFAULT_CACHE_DURATION']
    

This would make ``MY_SETTING`` and ``DEFAULT_CACHE_DURATION``
editable in the database.

**Note**: App's which are not using *django-dynamic-settings* are not
affected by the changes. That includes for example Django itself.
It doesn't make much sense to change a setting in the database
via admin which is used internally by Django. It will simply have
no effect.

So the project or app which will make usage of *django-dynamic-settings*
great way of retrieving and setting the settings in the database
should use *django-dynamic-settings* instead of the usual way of
retrieving settings via ``from django.conf import settings``. See
the next section for usage examples.


4. Usage
:::::::::::::::::::::::::::::::::


*django-dynamic-settings* is used in a very similiar way you
usually would use your settings. Instead of using:

::
    
    from django.conf import settings
    

use

::
    
    from dynamicsettings import settings
    

After that you can use settings as you are used to. Examples:

::
    
    login_redirect_url = settings.LOGIN_REDIRECT_URL
    my_custom_setting = settings.MY_SETTING
    

    
Additionally you have access to the following methods:

- ``settings.get(key, default)``: Retrieve a setting for a
  particular name (``key``) or return the ``default`` 
  (``None`` if emitted). Works like the python built-in
  ``dict.get()`` method Example usage:

  ::
      
      login_redirect_url = settings.get('LOGIN_REDIRECT_URL', '/')
      my_custom_setting = settings.get('MY_SETTING)
      

- ``settings.set(key, value, type)``: This is setting a setting
  specified by ``key`` directly in the database without using the
  admin interface. ``value`` is the new value of the setting and
  ``type`` the python type. If ``type`` is not explicitly given
  it will try to resolve the type from the given `value``. Returns
  the new value if setting was successful. Raises
  KeyError if the setting is not allowed to be changed due to
  not defining it in ``DYNAMICSETTINGS_INCLUDE_SETTINGS``.
  Examples:

  ::
      
      login_redirect_url = settings.set('LOGIN_REDIRECT_URL', '/home/')
      my_custom_setting = settings.set('MY_SETTING', 73, 'int')
    

- ``settings.reset(key)``: If you saved a setting in the database you
  can reset it (giving the name of the setting) to its original value via
  this method. This method returns ``True`` if the reset was successful
  and ``False`` if not (setting wasn't saved to the database for example).
  Examples:
  
  ::  
      
      login_redirect_url = settings.set('LOGIN_REDIRECT_URL', '/home/')
      settings.reset('LOGIN_REDIRECT_URL')
      print settings.LOGIN_REDIRECT_URL
      

- ``settings.dict(keys)``: Returns a dict representation of the settings.
  If ``keys`` is ommitted all settings which are included into *django-dynamic-settings*
  are part of the dict. If you just want to retrieve particular settings
  you can provide names of the settings within ``keys`` (a list of strings).

- ``settings.is_in_db(key)``: Check if a particular setting given by
  its name (``key``) is saved in the db or not. Returns ``True`` if
  this is case, ``False`` otherwise.

- ``settings.can_change(key)``: Check if a particular setting given by
  its name (``key``) can be changed (and saved in the database). This
  returns ``True`` if the setting is provided in ``DYNAMICSETTINGS_INCLUDE_SETTINGS``,
  ``False`` otherwise.


5. Additional settings
:::::::::::::::::::::::::::::::::

Settings within *django-dynamic-settings* are cached in case you
are using Django's cache framework. To define the timeout for the
cached settings you can set ``DYNAMICSETTINGS_CACHE_TIMEOUT``:

::
    
    DYNAMICSETTINGS_CACHE_TIMEOUT = 60
    


.. _Python: http://www.python.org/
.. _Django: http://www.djangoproject.com/