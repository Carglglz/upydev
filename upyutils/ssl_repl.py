from ssl_socket_client_server import SSL_socket_client_repl as SSL_REPL


def start(host):
    ssl_repl_serv = SSL_REPL(host)
    return ssl_repl_serv
