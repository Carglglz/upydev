# This module should be imported from REPL, not run from command line.
import socket
import uos
import network
import uwebsocket
import wss_helper
import _webrepl
import ssl
from binascii import hexlify
from machine import unique_id


key = None
cert = None
cadata = None
listen_s = None
client_s = None
websslrepl = False
ssl_auth = False
client_swr = None


def setup_conn(port, accept_handler):
    global listen_s, websslrepl, ssl_auth
    listen_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ai = socket.getaddrinfo("0.0.0.0", port)
    addr = ai[0][4]

    listen_s.bind(addr)
    listen_s.listen(1)
    if accept_handler:
        listen_s.setsockopt(socket.SOL_SOCKET, 20, accept_handler)
    for i in (network.AP_IF, network.STA_IF):
        iface = network.WLAN(i)
        if iface.active():
            if websslrepl:
                print("WebSecureREPL daemon started on wss://%s:%d" %
                      (iface.ifconfig()[0], port))
            else:
                print("WebREPL daemon started on ws://%s:%d" %
                      (iface.ifconfig()[0], port))
    return listen_s


def accept_conn(listen_sock):
    global client_s, key, cert, websslrepl, ssl_auth, client_swr, cadata
    cl, remote_addr = listen_sock.accept()
    prev = uos.dupterm(None)
    uos.dupterm(prev)
    if prev:
        print("\nConcurrent WebREPL connection from", remote_addr, "rejected")
        cl.close()
        return
    print("\nWebREPL connection from:", remote_addr)
    client_s = cl
    if websslrepl:
        if hasattr(uos, 'dupterm_notify'):
            cl.setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
        try:
            cl = ssl.wrap_socket(cl, server_side=True, key=key, cert=cert,
                                 cadata=cadata, cert_reqs=ssl.CERT_REQUIRED)
        except Exception:
            cl = ssl.wrap_socket(cl, server_side=True, key=key, cert=cert)
        wss_helper.server_handshake(cl, ssl=True)
    else:
        wss_helper.server_handshake(cl)
    ws = uwebsocket.websocket(cl, True)
    ws = _webrepl._webrepl(ws)
    cl.setblocking(False)
    # notify REPL on socket incoming data (ESP32/ESP8266-only)
    if not websslrepl:
        if hasattr(uos, 'dupterm_notify'):
            cl.setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
    uos.dupterm(ws)
    client_swr = cl


def stop():
    global listen_s, client_s
    uos.dupterm(None)
    if client_s:
        client_s.close()
    if listen_s:
        listen_s.close()


def start(port=8266, password=None, ssl=False, auth=False):
    global key, cert, websslrepl, ssl_auth, cadata
    if ssl:
        if auth:
            ssl_auth = True
        websslrepl = True
        port = 8833
        _key = 'SSL_key{}.der'.format(hexlify(unique_id()).decode())
        _cert = 'SSL_certificate{}.der'.format(hexlify(unique_id()).decode())
        try:
            with open(_key, 'rb') as keyfile:
                key = keyfile.read()
            with open(_cert, 'rb') as certfile:
                cert = certfile.read()
            cadata = b''

            if 'ROOT_CA_cert.pem' in uos.listdir():
                with open('ROOT_CA_cert.pem', 'rb') as host:
                    cadata += host.read()
            if not cadata:
                cadata = cert
        except Exception as e:
            print(e)
            print('No key or certificate found')
    else:
        websslrepl = False
    stop()
    if password is None:
        try:
            import webrepl_cfg
            _webrepl.password(webrepl_cfg.PASS)
            setup_conn(port, accept_conn)
            print("Started webrepl in normal mode")
        except Exception:
            print("WebREPL is not configured, run 'import webrepl_setup'")
    else:
        _webrepl.password(password)
        setup_conn(port, accept_conn)
        print("Started webrepl in manual override mode")


def start_foreground(port=8266):
    stop()
    s = setup_conn(port, None)
    accept_conn(s)


def set_ssl(flag_ssl=True, flag_auth=False):
    with open('ssl_config.py', 'wb') as sslconfig:
        sslconfig.write(b'from collections import namedtuple\n\n')
        sslconfig.write(b'SSL_CONF = namedtuple("SSLCONFIG", ("ssl", "auth"))\n')
        sslconfig.write(b'SSL = SSL_CONF({}, {})'.format(flag_ssl, flag_auth))
