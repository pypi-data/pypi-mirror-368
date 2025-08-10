import django.apps
from django.contrib import admin
from django import forms
from . import models

installed_models = django.apps.apps.get_models(
    include_auto_created=True, include_swapped=True
)
model_choices = [(
    f'{m._meta.app_label}.{m._meta.model_name}',
    f'{m._meta.app_label}.{m._meta.verbose_name}'
) for m in installed_models]


class LogConfigForm(forms.ModelForm):

    model = forms.ChoiceField(choices=model_choices)


class LogConfigFieldInLine(admin.TabularInline):

    model = models.LogConfigField


class LogConfigAdmin(admin.ModelAdmin):

    model = models.LogConfig
    list_display = ('model', 'ignore_errors', 'exclude_fields')
    search_fields = ('pk', 'model')
    list_filter = ['ignore_errors', 'exclude_fields']
    form = LogConfigForm
    inlines = [LogConfigFieldInLine]


class LogAdmin(admin.ModelAdmin):

    model = models.LogConfig
    list_display = (
        'model', 'field', 'object_id', 'log_date', 'old_value', 'new_value',
        'user', 'tenant'
    )
    search_fields = ('model', 'field', 'object_id', 'old_value')
    list_filter = ['model', 'tenant']


admin.site.register(models.LogConfig, LogConfigAdmin)
admin.site.register(models.Log, LogAdmin)
