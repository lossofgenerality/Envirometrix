from django.contrib import admin
from django import forms
import string
from .models import *


class DataStreamForm(forms.ModelForm):
     naming_scheme = forms.CharField(widget=forms.TextInput(
        attrs={'size': '100'}
        ))

class DataStreamAdmin(admin.ModelAdmin):
    form = DataStreamForm
    
    def save_model(self, request, obj, form, change):
        """
        Automatically update datasets and time start/end when saving changes.
        """
        instance = form.save(commit=False)
        if any([
            not hasattr(instance,'datasets'), 
            request.POST['datasets'] == u'',
            request.POST['datasets'] == u"[]"
            ]):
            instance.datasets = '['+',\n'.join([str(set) for set in instance.get_datasets()])+']'
            
        instance.update_datetimes()
        instance.save()
        return instance

admin.site.register(DataStream, DataStreamAdmin)
admin.site.register(FTPSource)
admin.site.register(MathematicaSource)
