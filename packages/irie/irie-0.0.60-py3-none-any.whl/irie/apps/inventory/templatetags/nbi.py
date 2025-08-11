from django import template
register = template.Library()
    
@register.filter
def nbi(string):
    return string.split(" - ")[-1].lower()