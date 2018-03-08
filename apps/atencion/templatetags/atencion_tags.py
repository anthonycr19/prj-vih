from django import template

register = template.Library()


@register.simple_tag(name='object_fk')
def get_object_from_choice(field):
    try:
        return field.field.queryset.get(pk=field.value())
    except:
        return ''
