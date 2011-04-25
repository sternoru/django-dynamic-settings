# -*- coding: utf-8 -*-

import pickle

from django import forms
from django.utils.translation import gettext as _
from django.utils import simplejson

from dynamicsettings import models
from dynamicsettings import settings

class SettingsForm(forms.ModelForm):
    """Form class which helps to validate
    a setting before it is saved in the database.
    Have a closer look to the clean() method to 
    find out more about the details when a setting
    is rejected to be saved
    """
    
    class Meta:
        model = models.Settings
        
    def clean_key(self):
        """
        Checks if the key is in settings. Used to avoid abuse of the
        form by enabling disabled form fields via firebug or similiar.
        """
        key = self.cleaned_data['key']
        try:
            settings.__getattr__(key)
        except AttributeError:
            raise forms.ValidationError(_("This key does not exists in the original settings."))
        return key
    
    def clean(self):
        """
        a) Check if the setting was originally from the submitted type.
        Used to avoid abuse of the form by enabling disabled form 
        fields via firebug or similiar.
        b) Try to convert the value according to submitted type.
        Raises ValidiationError when type and value are not fitting
        each other (eg. value can;t be converted to type).
        c) check if the resulting value was actually changed  (and
        not yet in the database)
        """
        error_message_tmpl = 'A setting from type %s must be set to %s.'
        key = self.cleaned_data['key']
        value = self.cleaned_data['value']
        value_type = self.cleaned_data['type']
        if settings.can_change(key) is False:
            raise forms.ValidationError(_("This setting can not be changed."))
        #a)
        original_type = type(settings.__getattr__(key)).__name__
        if original_type!='NoneType' and value_type!=original_type:
            raise forms.ValidationError(_("You can not change the type of a setting which was not NoneType before."))
        #b)
        if value_type == 'NoneType':
            if value!='None':
                raise forms.ValidationError(_(error_message_tmpl % ('NoneType', '"None"')))
            self.cleaned_data['value'] = None
        elif value_type == 'bool':
            if value!='True' and value!='False':
                raise forms.ValidationError(_(error_message_tmpl % ('bool', '"True" or "False"')))
            if value!='True':
                self.cleaned_data['value'] = True
            elif value!='False':
                self.cleaned_data['value'] = False
        elif value_type == 'int':
            try:
                self.cleaned_data['value'] = int(value)
            except ValueError:
                raise forms.ValidationError(_(error_message_tmpl % ('int or long', 'a number')))
        elif value_type == 'int':
            try:
                self.cleaned_data['value'] = float(value)
            except ValueError:
                raise forms.ValidationError(_(error_message_tmpl % ('float', 'a number')))
        elif value_type == 'str':
            self.cleaned_data['value'] = value
        elif value_type == 'unicode':
            self.cleaned_data['value'] = unicode(value)
        elif value_type in ['tuple', 'list', 'dict']:
            try:
                self.cleaned_data['value'] = value = simplejson.loads(value)
            except ValueError:
                raise forms.ValidationError(_(error_message_tmpl % ('tuple, list or dict', 'a valid JSON string')))
            if value_type == 'tuple' and type(value).__name__!='tuple':
                try:
                    if type(value).__name__ == 'dict':
                        raise TypeError
                    self.cleaned_data['value'] = tuple(value)
                except (ValueError, TypeError):
                    raise forms.ValidationError(_(error_message_tmpl % ('tuple', 'a valid JSON string representing an Array (leading "["and traling "]")')))
            elif value_type == 'list' and type(value).__name__!='list':
                try:
                    if type(value).__name__ == 'dict':
                        raise TypeError
                    self.cleaned_data['value'] = list(value)
                except (ValueError, TypeError):
                    raise forms.ValidationError(_(error_message_tmpl % ('list', 'a valid JSON string representing an Array (leading "["and traling "]")')))
            elif value_type == 'dict' and type(value).__name__!='dict':
                try:
                    if type(value).__name__ == 'list':
                        raise TypeError
                    self.cleaned_data['value'] = dict(value)
                except (ValueError, TypeError):
                    raise forms.ValidationError(_(error_message_tmpl % ('dict', 'a valid JSON string representing an Object (leading "{"and traling "}")')))
        #c)
        value = self.cleaned_data['value']
        if not settings.is_in_db(key) and value==settings.__getattr__(key):
            raise forms.ValidationError(_('To save a setting in the database the value must have been changed from its original value.'))
        
        return self.cleaned_data
    