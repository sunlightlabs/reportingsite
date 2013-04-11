from django.template.loader import get_template
from django.template import Context, Template
from django.http import HttpResponse

def render_to_json(template_location, context):
    t = get_template(template_location)
    c = Context(context)
    rendered_template = t.render(c)
    response = HttpResponse(rendered_template)
    response['Content-Type']='application/json'
    return response