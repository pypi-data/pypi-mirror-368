from django import template
register = template.Library()

@register.filter
def cvss_badge(score):
    try:
        s = float(score or 0)
    except (TypeError, ValueError):
        s = 0.0
    if s >= 9:
        cls = "bg-danger"
    elif s >= 7:
        cls = "bg-warning text-dark"
    elif s >= 4:
        cls = "bg-info"
    else:
        cls = "bg-success"
    return f'<span class="badge {cls}">{s:.1f}</span>'
