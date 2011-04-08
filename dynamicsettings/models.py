

from django.db import models

class Settings(models.Model):
    key = models.CharField(max_length=255, unique=True, null=False, blank=False)
    value = models.TextField(null=False, blank=False)
    type = models.CharField(max_length=10, choices=(
        ('NoneType', 'NoneType'),
        ('bool', 'bool'),
        ('int', 'int'),
        ('long', 'long'),
        ('float', 'float'),
        ('str', 'str'),
        ('unicode', 'unicode'),
        ('list', 'list'),
        ('tuple', 'tuple'),
        ('dict', 'dict'),
    ), null=False, blank=False)
    
    class Meta:
        verbose_name_plural = "Settings"
    
    def __unicode__(self):
        return self.key
