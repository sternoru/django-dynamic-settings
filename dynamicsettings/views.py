# -*- coding: utf-8 -*-

from django import shortcuts
from django import forms
from django.utils import simplejson
from django import http
from django.core.context_processors import csrf as csrf_processor
from django import template
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _

from dynamicsettings import models
from dynamicsettings import forms
from dynamicsettings import settings

@staff_member_required
def dynamicsettings_index(request):
    """Renders a template in the admin to show a list of settings. 
    
    Params:
        - ``request``: a django http request object
        
    Returns:
        - a rendered template with the following variables
          defined in its response dict
              - ``dynamic_settings``: a list of settings represented
              as dict's with:
                  -  ``key`` - the name of the setting
                  - ``value`` - the value of the setting
                  - ``is_db`` - a boolean indicating if the setting is saved in the db or not
                  - ``type`` - the (Python) type of the setting as its string representation
                  - ``can_change`` - a boolean indicating if the setting can be saved in the database or not
            - ``settings_form_rendered``: rendered html of ``forms.SettingsForm``
    """
    keys = [key for key in settings.dict()]
    keys.sort()
    res = []
    for key in keys:  
        value = settings.get(key)
        if isinstance(value, (list, tuple, dict)):
            try:
                value = simplejson.dumps(value, indent=4)
            except TypeError:
                value = 'Not a serializable object'
        res.append({
            'key': key,
            'value': value,
            'in_db': settings.is_in_db(key),
            'type': type(settings.get(key)).__name__,
            'can_change': settings.can_change(key),
        })
    res.sort(key=lambda e: e['can_change'], reverse=True)
    form_dict =  {'settings_form': forms.SettingsForm()}
    form_dict.update(csrf_processor(request))
    settings_form_rendered = template.loader.render_to_string('dynamicsettings/settings_form.html', form_dict)
    content_dict = {
        'dynamic_settings': res,
        'settings_form_rendered': settings_form_rendered,
    }
    return shortcuts.render_to_response('dynamicsettings/settings.html', content_dict,
                                        context_instance=template.RequestContext(request))

@staff_member_required
def dynamicsettings_set(request):
    """A view to handle the POST request to 
    set a setting in the database
    
    Params:
        - ``request``: a django http request object
        
    Returns:
        - a response as JSON including the following fields:
            - ``status``: "success" if the setting was saved in
               the database, "error" in other cases
            - on success:
                - ``value``: the new value of the setting (which is
                  saved in the database)
                - ``type``: the new type of the setting, can only differ
                   from the original type if it was ``NoneType``
            - on error:
                - ``message``: the message describing the error
                - ``form``: the validated form rendered in a template
                  (will show the error in the form)
    """
    if request.method=='POST':
        response_dict = {}
        settings_form = forms.SettingsForm(request.POST)
        if settings_form.is_valid():
            form_data = settings_form.cleaned_data
            changed = settings.set(form_data['key'], form_data['value'], form_data['type'])
            if changed is True:
                value = settings.__getattr__(form_data['key'])
                if isinstance(value, (list, tuple, dict)):
                    value = simplejson.dumps(value, indent=4)
                response_dict.update({
                    'status': 'success',
                    'value': value,
                    'type': form_data['type'],
                })
        else:
            form_dict = {'settings_form': settings_form}
            form_dict.update(csrf_processor(request))
            settings_form_rendered = template.loader.render_to_string('dynamicsettings/settings_form.html', form_dict)
            response_dict.update({
                'status': 'error',
                'message': settings_form.errors['__all__'],
                'form': settings_form_rendered
            })
        return http.HttpResponse(simplejson.dumps(response_dict, indent=4), mimetype="text/plain")
    return http.HttpResponseNotAllowed(['GET', 'PUT', 'DELETE', 'HEAD', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH'])

@staff_member_required
def dynamicsettings_reset(request):
    """A view to handle the POST request to 
    reset a setting in the database
    
    Params:
        - ``request``: a django http request object
        
    Returns:
        - a response as JSON including the following fields:
            - ``status``: "success" if the setting was reset in
               the database, "error" in other cases
            - on success:
                - ``value``: the original value of the setting (which is
                  not saved in the database)
                - ``type``: the original type of the setting
            - on error:
                - ``message``: the message describing the error
    """
    if request.method=='POST':
        key = request.POST.get('key', None)
        if key is None:
            response_dict = {
                'status': 'error',
                'message': _('No variable "key" in POST request.'),
            }
        else:
            reset_success = settings.reset(key)
            if reset_success is True:
                value = settings.__getattr__(key)
                if isinstance(value, (list, tuple, dict)):
                    value = simplejson.dumps(value, indent=4)
                response_dict = {
                    'status': 'success',
                    'value': value,
                    'type': type(settings.get(key)).__name__,
                }
            else:
                response_dict = {
                    'status': 'error',
                    'message': _('The setting "%s" is not saved in the database or can not be reseted.' % request.POST['key']),
                }
        return http.HttpResponse(simplejson.dumps(response_dict, indent=4), mimetype="text/plain")
    return http.HttpResponseNotAllowed(['GET', 'PUT', 'DELETE', 'HEAD', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH'])
