
#for now in views

from django import shortcuts
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import simplejson
from django import http
from django.core.context_processors import csrf as csrf_processor
from django import template
from django.utils.translation import ugettext as _

from dynamicsettings import models
from dynamicsettings import forms
from dynamicsettings import settings

"""
class DynamicSettingsForm(forms.ModelForm):
    GOOGLE_ACCOUNT_PASSWORD = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = models.DynamicSettings
"""

@staff_member_required
def dynamicsettings_index(request):
    keys = [key for key in settings.dict()]
    keys.sort()
    res = []
    for key in keys:  
        value = settings.get(key)
        if isinstance(value, (list, tuple, dict)):
            value = simplejson.dumps(value, indent=4)
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
        'settings': res,
        'STATIC_URL': settings.STATIC_URL,
        'settings_form_rendered': settings_form_rendered,
    }
    content_dict.update(csrf_processor(request))
    return shortcuts.render_to_response('dynamicsettings/settings.html', content_dict)

@staff_member_required
def dynamicsettings_set(request):
    """
    Handles the post request
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
                'form': settings_form_rendered
            })
        return http.HttpResponse(simplejson.dumps(response_dict, indent=4), mimetype="text/plain")
    raise http.Http404

@staff_member_required
def dynamicsettings_reset(request):
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
    raise http.Http404
