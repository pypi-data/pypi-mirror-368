from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.filter(is_safe=True)
def display_predictor(predictor):
    out = "" # str(predictor.__class__.__name__) #"" # f'<h6 style="display:inline">{predictor.name}</h6>  '
    out = out + predictor.description
    out = out + "\n".join((out, '<table class="table align-items-center"><tbody>'))

    for key, val in predictor.conf.items():
        name = predictor.schema["properties"].get(key, {"name": key}).get("name", key)
        out = out + f"<tr><td>{name}</td><td><code>{val}</code></td><tr>"

    out = out + "</tbody></table>"
    return SafeString(out)

#register.filter("display_predictor", display_predictor)
