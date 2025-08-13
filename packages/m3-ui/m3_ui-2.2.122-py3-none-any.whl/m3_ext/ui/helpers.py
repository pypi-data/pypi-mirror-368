# coding: utf-8
"""
Хелперы, которые помогают формировать пользовательский интерфейс
"""
from __future__ import absolute_import

from collections import Iterable
from pathlib import Path
from typing import Union

from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from m3 import M3JSONEncoder

from m3_ext.ui import render_template
from m3_ext.ui.protocols import HasTemplateGlobals
import six


def paginated_json_data(query, start=0, limit=25):
    if isinstance(query, QuerySet):
        try:
            total = query.count()
        except AttributeError:
            total = 0
    else:
        total = len(query)
    if start > 0 and limit < 1:
        data = list(query[start:])
    elif start >= 0 and limit > 0:
        data = list(query[start: start + limit])
    else:
        data = list(query)
    return M3JSONEncoder().encode({'rows': data, 'total': total})


def grid_json_data(query):
    """
    Выдает данные, упакованные в формате, пригодном для хаванья стором грида
    """
    return M3JSONEncoder().encode({'rows': list(query)})


def _render_globals(component):
    result = u''
    if component.template_globals:
        context = {'component': component, 'window': component}

        if isinstance(component.template_globals, six.string_types):
            result = render_template(component.template_globals, context)

        elif isinstance(component.template_globals, Iterable):
            result = mark_safe(u'\n'.join(
                render_template(template, context)
                for template in component.template_globals
            ))

    return result


def add_template_globals(component: HasTemplateGlobals, *templates: Union[str, Path]) -> None:
    """Добавляет новые шаблоны к компоненту."""

    str_templates = tuple(str(t) for t in templates)

    if component.template_globals:
        if isinstance(component.template_globals, tuple):
            component.template_globals += str_templates
        elif isinstance(component.template_globals, list):
            component.template_globals.extend(str_templates)
        elif isinstance(component.template_globals, str):
            component.template_globals = [
                component.template_globals,
                *str_templates,
            ]
    else:
        component.template_globals = list(templates)
