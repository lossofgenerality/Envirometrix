from django.contrib import admin
from django import forms
from .models import *
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django_ace import AceWidget
from django.forms import widgets
import os
from .tests import *


def test_random(modeladmin, request, queryset):
    for obj in queryset:
        run_random(obj)
test_random.short_description = 'Run with random values'

def test_static(modeladmin, request, queryset):
    for obj in queryset:
        run_static(obj)
test_static.short_description = 'Run with static values'

def make_live(modeladmin, request, queryset):
    queryset.update(draft=False)
make_live.short_description = 'Make public'

def make_draft(modeladmin, request, queryset):
    queryset.update(draft=True)
make_draft.short_description = 'Make private'


class MathematicaWidget(forms.TextInput):
    def __init__(self, attrs=None):
        super(MathematicaWidget, self).__init__(attrs)


class MathematicaSessionForm(forms.ModelForm):
    description = forms.CharField(widget=forms.TextInput(
        attrs={'size': '100'}
        ))
        
class MathematicaSessionAdmin(admin.ModelAdmin):
    #form = MathematicaSessionForm
    list_per_page = 100
    fields = [
        'name',
        'description',
        'draft',
        'mathematica_script',
        'extra_args',
        (
            'data_streams',
            'dataset_test'
        )
        ]
    list_display = (
        'name',
        'draft',
        'description',
        )
    actions = [test_random, test_static, make_live, make_draft]

    def save_model(self, request, obj, form, change): 
        instance = form.save(commit=False)
        if not hasattr(instance,'user'):
            instance.user = request.user
            
        instance.save(start_session=False, extra_args={}, user=request.user)
        return instance

admin.site.register(MathematicaSession, MathematicaSessionAdmin)













class MathematicaPackageForm(forms.ModelForm):
    
        def clean_file(self):
            if self.cleaned_data['file'].name.endswith('.m'):
                return self.cleaned_data['file']
            else:
                raise forms.ValidationError('This file is not a valid Mathematica package')
                
        class Meta:
            model = MathematicaPackage
            
class MathematicaPackageAdmin(admin.ModelAdmin):
    form = MathematicaPackageForm
    list_per_page = 100
    fields = [
        'name',
        'description',
        'file',
        'extra_args',
        'data_streams'
        ]
    list_display = (
        'name',
        'description',
        'file',
        'extra_args',
        )

    def save_model(self, request, obj, form, change): 
        instance = form.save(commit=False)
        if not hasattr(instance,'user'):
            instance.user = request.user
            
        instance.save(start_package=False, extra_args={}, user=request.user)
        return instance

admin.site.register(MathematicaPackage, MathematicaPackageAdmin)


class PythonScriptForm(forms.ModelForm):
                
        class Meta:
            model = PythonScript
            

class PythonScriptAdmin(admin.ModelAdmin):
    form = PythonScriptForm
    fields = ('name', 'code', 'periodic', 'extra_args', 'data_streams',)        

    def save_model(self, request, obj, form, change): 
        instance = form.save(commit=False)
        if not hasattr(instance,'user'):
            instance.user = request.user
        instance.save()
        return instance

admin.site.register(PythonScript, PythonScriptAdmin)