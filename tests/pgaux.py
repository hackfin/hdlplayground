import os
from IPython.display import Markdown
from IPython.display import HTML
import random

def generate(directory, files):
    txt, path = directory
    pre = os.getenv('JUPYTERHUB_SERVICE_PREFIX')

    s = "  * %s: [%s](%s/tree/work/%s)\n" % (txt, path, pre, path)


    if not pre:
        pre = ""

    for txt, fn in files:
        s += '\n  * %s: <a href="%s/edit/work/%s" target="_blank">%s</a>' % (txt, pre, fn, fn)

    return s

def hide_toggle(for_next=False):
    "Snippet taken from Ferrard@stackoverflow"
    
    this_cell = """$('div.cell.code_cell.rendered.selected')"""
    next_cell = this_cell + '.next()'

    toggle_text = 'Toggle show/hide'  # text shown on toggle link
    target_cell = this_cell  # target cell to control with toggle
    js_hide_current = ''  # bit of JS to permanently hide code in current cell (only when toggling next cell)

    if for_next:
        target_cell = next_cell
        toggle_text += ' next cell'
        js_hide_current = this_cell + '.find("div.input").hide();'

    js_f_name = 'code_toggle_{}'.format(str(random.randint(1,2**64)))

    html = """
        <script>
            function {f_name}() {{
                {cell_selector}.find('div.input').toggle();
            }}

            {js_hide_current}
        </script>

        <a href="javascript:{f_name}()">{toggle_text}</a>
    """.format(
        f_name=js_f_name,
        cell_selector=target_cell,
        js_hide_current=js_hide_current, 
        toggle_text=toggle_text
    )

    return HTML(html)