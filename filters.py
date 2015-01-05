from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget, AdminDateWidget
from django.db import models
from django.utils.translation import ugettext as _

class StringForm(forms.Form):
    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        extra_params = kwargs.pop('extra_params')
        super(StringForm, self).__init__(*args, **kwargs)

        self.fields['%s__contains' % field_name] = forms.CharField(
            label='', widget=AdminTextInputWidget(
                attrs={'placeholder': _('Search text')}), localize=True,
            required=False)

        for par, val in extra_params.items():
            if val:
                self.fields[par] = forms.CharField(
                    label='', widget=AdminTextInputWidget(
                        attrs={'style':'display:none;','value':val}), localize=True,
                        required=False)


class StringFilter(admin.filters.FieldListFilter):
    template = 'daterange_filter/filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        extra_params = request.GET.dict()
        self.lookup_string = '{}__contains'.format(field_path)
        extra_params.pop(self.lookup_string, {})
        self.extra_params = extra_params
        super(StringFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_string]

    def get_form(self, request):
        return StringForm(data=self.used_parameters,
                          field_name=self.field_path,
                          extra_params=self.extra_params)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))
            return queryset.filter(**filter_params)
        else:
            return queryset

class DateRangeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        extra_params = kwargs.pop('extra_params')
        super(DateRangeForm, self).__init__(*args, **kwargs)

        self.fields['%s__gte' % field_name] = forms.DateField(
            label='', widget=AdminDateWidget(
                attrs={'placeholder': _('From date')}), localize=True,
            required=False)

        self.fields['%s__lte' % field_name] = forms.DateField(
            label='', widget=AdminDateWidget(
                attrs={'placeholder': _('To date')}), localize=True,
            required=False)

        for par, val in extra_params.items():
            if val:
                self.fields[par] = forms.CharField(label='',
                                               widget=AdminTextInputWidget(attrs={'style':'display:none;','value':val}),
                                               localize=True,
                                               required=False)

class DateRangeFilter(admin.filters.FieldListFilter):
    template = 'daterange_filter/filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_upto = '%s__lte' % field_path
        extra_params = request.GET.dict()
        extra_params.pop(self.lookup_kwarg_since, None)
        extra_params.pop(self.lookup_kwarg_upto, None)
        self.extra_params = extra_params
        super(DateRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_upto]

    def get_form(self, request):
        return DateRangeForm(data=self.used_parameters,
                             field_name=self.field_path,
                             extra_params=self.extra_params)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))
            return queryset.filter(**filter_params)
        else:
            return queryset

admin.filters.FieldListFilter.register(
    lambda f: isinstance(f, models.TextField), StringFilter)
admin.filters.FieldListFilter.register(
    lambda f: isinstance(f, models.DateField), DateRangeFilter)



#Copyright 2014-present lossofgenerality.com