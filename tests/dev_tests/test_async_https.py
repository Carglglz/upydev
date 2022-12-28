import ssl
import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file
from machine import Pin
import aiorepl

led = Pin(2, Pin.OUT)

app = Microdot()

htmldoc_color = """
<!DOCTYPE html>
<html>
    <head>
        <title>Microdot Example Page</title>
    </head>
    <body>
        <div>
            <h1>Microdot Example Page</h1>
            <p>Hello from Microdot colored {}!</p>
            <p><a href="/shutdown">Click to shutdown the server</a></p>
        </div>
    </body>
</html>
"""


@app.route("/")
async def index(request):
    return send_file("static/index.html")


@app.route("/shutdown")
async def shutdown(request):
    await request.app.shutdown()
    return "The server is shutting down..."


async def toggle_led():
    while True:
        led.value(not led.value())
        await asyncio.sleep(1)


repl = aiorepl.repl

sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sslctx.load_cert_chain("SSL_certificate7c9ebd3d9df4.der", "SSL_key7c9ebd3d9df4.pem")
app.run(
    host="192.168.1.84", port=4443, debug=True, ssl=sslctx, tasks=[repl, toggle_led]
)
