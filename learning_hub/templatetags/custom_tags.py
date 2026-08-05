from django import template
from django.urls import reverse

from learning_hub.models import Formation

register = template.Library()


def link_to_section(url_name, section_id):
    return reverse(url_name) + "#" + section_id


@register.simple_tag
def link_to_formation_section(url_name, formation_pk):
    return link_to_section(url_name, f"formation-{formation_pk}")


@register.simple_tag
def calculate_formation_workload(formation_id):
    formation = Formation.objects.get(pk=formation_id)
    workload = 0
    for course in formation.courses.all():
        workload += course.workload
    return workload
