"""Shared placeholder body for pages Agents B and C have not landed yet.

Agents B and C may delete their use of this helper once their real page
modules exist; the module itself is harmless if left unused.
"""


def placeholder(ctx, title, subtitle, lines, cta=None):
    shell = ctx["shell"]
    paras = "".join('<p class="small mid">%s</p>' % line for line in lines)
    button = ""
    if cta:
        button = ('<a class="btn btn-secondary" href="%s" style="align-self:flex-start">'
                  '%s<span>%s</span></a>' % (cta[0], shell.icon("play", 15), cta[1]))
    return (
        shell.page_head(title, subtitle)
        + '<section class="panel"><div class="label">Not built yet</div>%s%s</section>'
        % (paras, button)
    )
