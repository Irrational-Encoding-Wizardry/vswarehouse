from django import template

register = template.Library()


@register.filter("pystring")
def pystring(val):
    val = str(val)
    val = val.replace("\\", "\\\\")
    val = val.replace("'", "\\'")
    val = val.replace('"', '\\"')
    val = val.replace("\n", "\\n")
    val = val.replace("\f", "\\f")
    val = val.replace("\b", "\\b")
    val = val.replace("\r", "\\r")
    val = val.replace("\t", "\\t")
    val = val.encode("ascii", errors="backslashreplace").decode("ascii")
    return val
