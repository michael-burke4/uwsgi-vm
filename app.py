from urllib.parse import parse_qs
from pathlib import Path
import vm

CSSPATH = "./style.css"



# Build a list representation of a cpu's stack. Zero indexed where
# the top of the stack is index 0.
def build_stack_list(cpu):
    stck = cpu.get_stack()
    stck.reverse()
    html = '<h5>Stack:</h5>'
    html += '<ol start="0">\n'
    for item in stck:
        html += '<li>%s</li>\n' % item
    html += '</ol>'
    return html

def build_register_table(cpu):
    return """
<table>
    <tr>
        <th>Register</th>
        <th>Value</th>
    </tr>
    <tr>
        <td>a</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>b</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>c</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>d</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>instruction pointer</th>
        <td>%d</th>
    </tr>
</table>""" % cpu.get_registers()

# https://stackoverflow.com/a/49564464
def load_file_to_str(path):
    return Path(path).read_text()

def build_head():
    return """
<head>
    <style>
    %s
    </style>
</head>
""" % load_file_to_str(CSSPATH)

def build_text_area(contents):
    return """
<body>
    <form action="/submit" method="post">
        <textarea name="message" rows="20" cols="50">%s</textarea>
        <br>
        <input type="submit" value="run">
    </form>
</body>
</html>
""" % contents

def run_program(text):
    program = text.splitlines()
    cpu = vm.Interpreter(program)
    cpu.run()
    return cpu.get_error_string() + "<br>" + build_register_table(cpu) + "<br>" + build_stack_list(cpu)

def handle_submit(env, page):
    body_len = int(env.get("CONTENT_LENGTH", 0))
    body = env["wsgi.input"].read(body_len).decode("UTF-8")
    msg = parse_qs(body).get('message')[0]
    page += build_text_area(msg)
    page += run_program(msg)
    return page

def application(env, start_response):
    page = '<html>'
    page += build_head()

    if env["REQUEST_METHOD"] == "POST" and env["PATH_INFO"] == '/submit':
        page += handle_submit(env, page)
    else:
        page += build_text_area("#insert your code here!")
    page += '</html>'
    start_response('200 OK', [('Content-Type','text/html')])
    return bytes(page, "UTF-8")
