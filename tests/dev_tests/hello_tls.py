from microdot import Microdot
import ssl

app = Microdot()

htmldoc = """<!DOCTYPE html>
<html>
    <head>
        <title>Microdot Example Page</title>
    </head>
    <body>
        <div>
            <h1>Microdot Example Page</h1>
            <p>Hello from Microdot!</p>
            <p><a href="/shutdown">Click to shutdown the server</a></p>
        </div>
    </body>
</html>
"""


@app.route("/")
def hello(request):
    return htmldoc, 200, {"Content-Type": "text/html"}


@app.route("/shutdown")
def shutdown(request):
    request.app.shutdown()
    # return 'The server is shutting down...'


sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sslctx.load_cert_chain("SSL_certificate7c9ebd3d9df4.der", "SSL_key7c9ebd3d9df4.pem")
app.run(port=4443, debug=True, ssl=sslctx)
