from __future__ import annotations

import re
from django.contrib.gis.admin import GISModelAdmin, TabularInline, StackedInline, display, register
from django.db.models import Field, Model
from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from import_export.admin import ImportExportMixin


class ModelAdmin(ImportExportMixin, GISModelAdmin): # type: ignore
    gis_widget_kwargs = {'attrs': {'default_lat': 43.30, 'default_lon': 5.37}}

    def save_model(self, request: HttpRequest, obj: Model, form: ModelForm, change: bool):
        field: Field
        for field in obj._meta.fields:
            # Transform blank values to null values
            if field.null:
                value = getattr(obj, field.attname, None)
                if value == '':
                    setattr(obj, field.attname, None)

            # Set default inserted_by and updated_by value
            if not field.editable:
                if change: # UPDATE
                    if field.name == 'updated_by':
                        setattr(obj, field.attname, request.user.pk)
                else: # INSERT
                    if field.name == 'inserted_by' or field.name == 'updated_by':
                        setattr(obj, field.attname, request.user.pk)
        
        super().save_model(request, obj, form, change)


def admin_url(model: type[Model]|str|Model):
    """
    Get admin URL of the given model.
    
    Reference: https://docs.djangoproject.com/en/5.1/ref/contrib/admin/#reversing-admin-urls
    """
    pk = None
    if isinstance(model, (type,Model)):
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        if isinstance(model, Model):
            pk = model.pk
    else:
        m = re.match(r'^([a-z0-9_]+)[\._]([a-z0-9_]+)$', model, re.IGNORECASE)
        if m:
            app_label = m[1]
            model_name = m[2]
        else:
            raise ValueError(f"Invalid model type string: {model}")

    prefix = 'admin:%s_%s' % (app_label, model_name)
    if pk is None:
        return reverse(f'{prefix}_changelist')
    else:
        return reverse(f'{prefix}_change', args=[pk])


__all__ = ('ModelAdmin', 'admin_url',
           # Shortcuts
           'TabularInline', 'StackedInline', 'display', 'register',)
