# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.utils import simplejson
from django.conf import settings

from dynamicsettings import models
from dynamicsettings import settings as dynamic_settings
from dynamicsettings import app_settings


class DynamicSettingsViewsTestCase(TestCase):
    urls = 'dynamicsettings.urls'
    
    def setUp(self):
        #use a standard set of context processors, some custom
        #context processors might return something which is 
        #breaking the tests when the test is used with specific
        #url conf, example would be that ine context processor
        #is using a urlresolvers.revere functionality to retrieve data
        settings.TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth", 
            "django.core.context_processors.debug", 
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.request",
            "django.core.context_processors.csrf",
        )
        #set auth backend to default
        settings.AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
        self.staff = {'username': 'staff', 'email': 'staff@example.com', 'password': 'staffpassword'}
        self.normal = {'username': 'normal', 'email': 'normal@example.com', 'password': 'normalpassword'}
        staff_user = User.objects.create_user(self.staff['username'], self.staff['email'], self.staff['password'])
        normal_user = User.objects.create_user(self.normal['username'], self.normal['email'], self.normal['password'])
        staff_user.is_staff = True
        staff_user.save()
        #overwrite app settings
        app_settings.DYNAMICSETTINGS_INCLUDE_MODULES = ['dynamicsettings.tests.test_settings']
        app_settings.DYNAMICSETTINGS_INCLUDE_SETTINGS = [
             'TEST_SETTING1',
             'TEST_SETTING2',
             'TEST_SETTING3',
             'TEST_SETTING4',
             'TEST_SETTING5',
        ]
    
    def test_index_view_staff(self):
        logged_in = self.client.login(username=self.staff['username'], password=self.staff['password'])
        self.assertTrue(logged_in)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('dynamic_settings' in response.context)
        self.assertTrue('STATIC_URL' in response.context)
        self.assertTrue('settings_form_rendered' in response.context)
        #check against a couple random settings which should be present
        for setting_dict in response.context['dynamic_settings']:
            self.assertEqual(setting_dict['type'], type(dynamic_settings.__getattr__(setting_dict['key'])).__name__, msg=setting_dict['key'])
            self.assertEqual(setting_dict['in_db'], False, msg=setting_dict['key']) #should be False at this moment
            self.assertEqual(setting_dict['can_change'], dynamic_settings.can_change(setting_dict['key']), msg=setting_dict['key'])
        self.client.logout()
    
    def test_index_view_normal(self):
        logged_in = self.client.login(username=self.normal['username'], password=self.normal['password'])
        self.assertTrue(logged_in)
        response = self.client.get('/')
        #this should render the login page for the admin, though without redirecting
        self.assertEqual(response.status_code, 200)
        self.assertFalse('dynamic_settings' in response.context)
        self.assertFalse('settings_form_rendered' in response.context)
        self.client.logout()
    
    def test_set_view_staff(self):
        logged_in = self.client.login(username=self.staff['username'], password=self.staff['password'])
        self.assertTrue(logged_in)
        response = self.client.get('/set/')
        self.assertEqual(response.status_code, 405)
        
        #check first setting
        response = self.client.post('/set/', {'key': 'TEST_SETTING1', 'value': '42', 'type': 'int'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'success')
        self.assertEqual(content_json['value'], 42)
        self.assertEqual(content_json['type'], 'int')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING1'))
        #change to non int
        response = self.client.post('/set/', {'key': 'TEST_SETTING1', 'value': 'some random string', 'type': 'int'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING1'))
        #check that the old value is still saved
        self.assertEqual(dynamic_settings.TEST_SETTING1, 42)
        dynamic_settings.reset('TEST_SETTING1')
        self.assertFalse(dynamic_settings.is_in_db('TEST_SETTING1'))
        self.assertEqual(dynamic_settings.TEST_SETTING1, 73)
        
        #check second setting
        response = self.client.post('/set/', {'key': 'TEST_SETTING2', 'value': 'my_custom_string', 'type': 'str'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'success')
        self.assertEqual(content_json['value'], 'my_custom_string')
        self.assertEqual(content_json['type'], 'str')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING2'))
        #change to the type
        response = self.client.post('/set/', {'key': 'TEST_SETTING2', 'value': '123', 'type': 'int'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING2'))
        #check that the old value is still saved
        self.assertEqual(dynamic_settings.TEST_SETTING2, 'my_custom_string')
        dynamic_settings.reset('TEST_SETTING2')
        self.assertFalse(dynamic_settings.is_in_db('TEST_SETTING2'))
        self.assertEqual(dynamic_settings.TEST_SETTING2, 'a string')
        
        #check third setting
        response = self.client.post('/set/', {'key': 'TEST_SETTING3', 'value': '[4,5]', 'type': 'list'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'success')
        self.assertEqual(content_json['value'].replace('\n','').replace(' ',''), '[4,5]')
        self.assertEqual(content_json['type'], 'list')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING3'))
        #change the value to sth which doesnt look like a list
        response = self.client.post('/set/', {'key': 'TEST_SETTING3', 'value': '{"d": 123}', 'type': 'list'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING3'))
        #check that the old value is still saved
        self.assertEqual(dynamic_settings.TEST_SETTING3, [4, 5])
        dynamic_settings.reset('TEST_SETTING3')
        self.assertFalse(dynamic_settings.is_in_db('TEST_SETTING3'))
        self.assertEqual(dynamic_settings.TEST_SETTING3, [1, 2, 3])
        
        #check fourth setting
        response = self.client.post('/set/', {'key': 'TEST_SETTING4', 'value': '{"d": 123, "abc": "string", "l": []}', 'type': 'dict'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'success')
        self.assertEqual(content_json['type'], 'dict')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING4'))
        #change the value and type to something completely different
        response = self.client.post('/set/', {'key': 'TEST_SETTING4', 'value': '123', 'type': 'long'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING4'))
        #check that the old value is still saved
        self.assertEqual(dynamic_settings.TEST_SETTING4, {"d": 123, "abc": "string", "l": []})
        dynamic_settings.reset('TEST_SETTING4')
        self.assertFalse(dynamic_settings.is_in_db('TEST_SETTING4'))
        self.assertEqual(dynamic_settings.TEST_SETTING4, {'key': 'value', 'num': 3})
        
        #check last setting (NoneType - can be changed to anything)
        response = self.client.post('/set/', {'key': 'TEST_SETTING5', 'value': u'你好', 'type': 'unicode'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'success')
        self.assertEqual(content_json['value'], u'你好')
        self.assertEqual(content_json['type'], 'unicode')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING5'))
        #check to another type (once a type is set it should not change anymore)
        response = self.client.post('/set/', {'key': 'TEST_SETTING5', 'value': '300', 'type': 'int'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING5'))
        #change the type to list and value to something which doesnt look like a list
        response = self.client.post('/set/', {'key': 'TEST_SETTING5', 'value': '404', 'type': 'list'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertTrue(dynamic_settings.is_in_db('TEST_SETTING5'))
        #check that the old value is still saved
        self.assertEqual(dynamic_settings.TEST_SETTING5, u'你好')
        dynamic_settings.reset('TEST_SETTING5')
        self.assertFalse(dynamic_settings.is_in_db('TEST_SETTING5'))
        self.assertEqual(dynamic_settings.TEST_SETTING5, None)
        self.assertEqual(type(dynamic_settings.TEST_SETTING5).__name__, 'NoneType')
        
        self.client.logout()
    
    def test_set_view_normal(self):
        logged_in = self.client.login(username=self.normal['username'], password=self.normal['password'])
        self.assertTrue(logged_in)
        response = self.client.get('/set/')
        #attempt to log the user into admin
        self.assertEqual(response.status_code, 200)
        #even a post request should not succeed
        response = self.client.post('/set/', {'key': 'TEST_SETTING1', 'value': 'some random string', 'type': 'int'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(dynamic_settings.is_in_db('TEST_SETTING1'))
        self.assertEqual(dynamic_settings.TEST_SETTING1, 73)
        self.client.logout()
        #no need to test furhter settings
    
    def test_reset_view_staff(self):
        logged_in = self.client.login(username=self.staff['username'], password=self.staff['password'])
        self.assertTrue(logged_in)
        response = self.client.get('/reset/')
        self.assertEqual(response.status_code, 405)
        
        #set some setting
        dynamic_settings.set('TEST_SETTING1', 500, 'int')
        self.assertEqual(dynamic_settings.TEST_SETTING1, 500)
        response = self.client.post('/reset/', {'key': 'TEST_SETTING1'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'success')
        self.assertEqual(content_json['value'], 73)
        self.assertEqual(content_json['type'], 'int')
        self.assertEqual(dynamic_settings.TEST_SETTING1, 73)
        #call view without key
        response = self.client.post('/reset/')
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        #reset a key wjhich is already reseted
        response = self.client.post('/reset/', {'key': 'TEST_SETTING3'})
        self.assertEqual(response.status_code, 200)
        content_json = simplejson.loads(response.content)
        self.assertEqual(content_json['status'], 'error')
        self.assertEqual(dynamic_settings.TEST_SETTING1, 73)
        
        self.client.logout()
    
    def test_reset_view_normal(self):
        logged_in = self.client.login(username=self.normal['username'], password=self.normal['password'])
        self.assertTrue(logged_in)
        response = self.client.get('/reset/')
        #attempt to log the user into admin
        self.assertEqual(response.status_code, 200)
        
        dynamic_settings.set('TEST_SETTING1', 500, 'int')
        self.assertEqual(dynamic_settings.TEST_SETTING1, 500)
        response = self.client.post('/reset/', {'key': 'TEST_SETTING1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dynamic_settings.TEST_SETTING1, 500)
        dynamic_settings.reset('TEST_SETTING1')
        self.assertEqual(dynamic_settings.TEST_SETTING1, 73)
        
        self.client.logout()


