from django import template
from django.template import loader

from crispy_forms.utils import TEMPLATE_PACK

register = template.Library()


@register.simple_tag(name='field')
def custom_field(field, **kwargs):
    """Use crispy_forms as a base template for custom fields for forms"""
    template_path = '%s/field.html' % TEMPLATE_PACK
    label = kwargs.get('label', True)
    context = {
        'field': field,
        'form_show_errors': True,
        'form_show_labels': bool(label)
    }
    if isinstance(label, str):
        field.label = label

    columns = kwargs.get('cols', False)
    if columns:
        label_width = kwargs.get('label_width', 4)
        context.update({
            'label_class': 'col-lg-{}'.format(label_width),
            'field_class': 'col-lg-{}'.format(12 - label_width)
        })
    if kwargs.get('inline'):
        context.update({
            'inline_class': 'inline'
        })
    if kwargs.get('datepicker'):
        context.update({
            'field_class': '{} {}'.format(context.get('field_class'), ' datepicker')
        })
    append = kwargs.get('append')
    if append:
        context.update({
            'crispy_appended_text': append
        })
        template_path = '%s/layout/prepended_appended_text.html' % TEMPLATE_PACK
    _template = loader.get_template(template_path)
    return _template.render(context)
