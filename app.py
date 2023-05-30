from urllib.parse import parse_qs

TEXTAREA="""
<body>
    <form action="/submit" method="post">
        <textarea name="message" rows="8" cols="50"></textarea>
        <br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
"""

def application(env, start_response):
    page = TEXTAREA

    if env["REQUEST_METHOD"] == "POST" and env["PATH_INFO"] == '/submit':
        print(int(env.get("CONTENT_LENGTH", 0)))
        body_len = int(env.get("CONTENT_LENGTH", 0))
        body = env["wsgi.input"].read(body_len).decode("UTF-8")
        msg = parse_qs(body).get('message')[0]
        page += msg
    start_response('200 OK', [('Content-Type','text/html')])
    return bytes(page, "UTF-8")
