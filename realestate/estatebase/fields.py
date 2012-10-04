from django.db import models
from django.core.validators import RegexValidator
from south.modelsinspector import add_introspection_rules
from django import forms
from selectable.forms.widgets import AutoComboboxSelectWidget
from django.forms.widgets import TextInput
from django.forms.fields import MultiValueField, CharField
from selectable.forms.fields import AutoComboboxSelectMultipleField

class MinMaxField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 25)
        kwargs['blank'] = kwargs.get('blank', True)
        kwargs['null'] = kwargs.get('null', True)
        super(MinMaxField, self).__init__(*args, **kwargs)
        validators = []
        validators.append(RegexValidator(regex=r"^(?P<oper>\>|\<)(?P<n>\d+)$"))
        validators.append(RegexValidator(regex=r"^(?P<n1>\d+)\-(?P<n2>\d+)$"))
        validators.append(RegexValidator(regex=r"^(?P<n>\d+)$"))
        self.default_validators = validators

add_introspection_rules([], ["^estatebase\.fields\.MinMaxField"])

class ComplexFieldWidget(forms.MultiWidget):
    def __init__(self, lookup_class, attrs=None):                
        widgets = (AutoComboboxSelectWidget(lookup_class), TextInput(attrs={'class':'number-input'}))
        super(ComplexFieldWidget, self).__init__(widgets, attrs)
    def decompress(self, value):
        if value:            
            return value
        return [None, None] 

class ComplexField(MultiValueField):    
    def __init__(self, lookup_class, *args, **kwargs):
        self.widget = ComplexFieldWidget(lookup_class=lookup_class)        
        fields = []
        fields.append(AutoComboboxSelectMultipleField(
            lookup_class=lookup_class,            
            required=False,
            )
         )        
        fields.append(CharField())        
        super(ComplexField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:                        
            return data_list
        return [None, None]