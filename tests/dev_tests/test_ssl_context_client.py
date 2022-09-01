import socket
import ssl
import time
import binascii


# This certificate was obtained from micropython.org using openssl:
# $ openssl s_client -showcerts -connect micropython.org:443 </dev/null 2>/dev/null
# The certificate is from Let's Encrypt:
# 1 s:/C=US/O=Let's Encrypt/CN=R3
#   i:/C=US/O=Internet Security Research Group/CN=ISRG Root X1
# Validity
#            Not Before: Sep  4 00:00:00 2020 GMT
#            Not After : Sep 15 16:00:00 2025 GMT
# Copy PEM content to a file (certmpy.pem) and convert to DER e.g.
# $ openssl x509 -in certmpy.pem -out certmpy.der -outform DER
# Then convert to hex format, eg using binascii.hexlify(data).

ca_cert_chain = binascii.unhexlify(
    b"30820516308202fea003020102021100912b084acf0c18a753f6d62e25a75f5a300d06092a864886"
    b"f70d01010b0500304f310b300906035504061302555331293027060355040a1320496e7465726e65"
    b"742053656375726974792052657365617263682047726f7570311530130603550403130c49535247"
    b"20526f6f74205831301e170d3230303930343030303030305a170d3235303931353136303030305a"
    b"3032310b300906035504061302555331163014060355040a130d4c6574277320456e637279707431"
    b"0b300906035504031302523330820122300d06092a864886f70d01010105000382010f003082010a"
    b"0282010100bb021528ccf6a094d30f12ec8d5592c3f882f199a67a4288a75d26aab52bb9c54cb1af"
    b"8e6bf975c8a3d70f4794145535578c9ea8a23919f5823c42a94e6ef53bc32edb8dc0b05cf35938e7"
    b"edcf69f05a0b1bbec094242587fa3771b313e71cace19befdbe43b45524596a9c153ce34c852eeb5"
    b"aeed8fde6070e2a554abb66d0e97a540346b2bd3bc66eb66347cfa6b8b8f572999f830175dba726f"
    b"fb81c5add286583d17c7e709bbf12bf786dcc1da715dd446e3ccad25c188bc60677566b3f118f7a2"
    b"5ce653ff3a88b647a5ff1318ea9809773f9d53f9cf01e5f5a6701714af63a4ff99b3939ddc53a706"
    b"fe48851da169ae2575bb13cc5203f5ed51a18bdb150203010001a382010830820104300e0603551d"
    b"0f0101ff040403020186301d0603551d250416301406082b0601050507030206082b060105050703"
    b"0130120603551d130101ff040830060101ff020100301d0603551d0e04160414142eb317b75856cb"
    b"ae500940e61faf9d8b14c2c6301f0603551d2304183016801479b459e67bb6e5e40173800888c81a"
    b"58f6e99b6e303206082b0601050507010104263024302206082b060105050730028616687474703a"
    b"2f2f78312e692e6c656e63722e6f72672f30270603551d1f0420301e301ca01aa018861668747470"
    b"3a2f2f78312e632e6c656e63722e6f72672f30220603551d20041b30193008060667810c01020130"
    b"0d060b2b0601040182df13010101300d06092a864886f70d01010b0500038202010085ca4e473ea3"
    b"f7854485bcd56778b29863ad754d1e963d336572542d81a0eac3edf820bf5fccb77000b76e3bf65e"
    b"94dee4209fa6ef8bb203e7a2b5163c91ceb4ed3902e77c258a47e6656e3f46f4d9f0ce942bee54ce"
    b"12bc8c274bb8c1982fa2afcd71914a08b7c8b8237b042d08f908573e83d904330a472178098227c3"
    b"2ac89bb9ce5cf264c8c0be79c04f8e6d440c5e92bb2ef78b10e1e81d4429db5920ed63b921f81226"
    b"949357a01d6504c10a22ae100d4397a1181f7ee0e08637b55ab1bd30bf876e2b2aff214e1b05c3f5"
    b"1897f05eacc3a5b86af02ebc3b33b9ee4bdeccfce4af840b863fc0554336f668e136176a8e99d1ff"
    b"a540a734b7c0d063393539756ef2ba76c89302e9a94b6c17ce0c02d9bd81fb9fb768d40665b3823d"
    b"7753f88e7903ad0a3107752a43d8559772c4290ef7c45d4ec8ae468430d7f2855f18a179bbe75e70"
    b"8b07e18693c3b98fdc6171252aafdfed255052688b92dce5d6b5e3da7dd0876c842131ae82f5fbb9"
    b"abc889173de14ce5380ef6bd2bbd968114ebd5db3d20a77e59d3e2f858f95bb848cdfe5c4f1629fe"
    b"1e5523afc811b08dea7c9390172ffdaca20947463ff0e9b0b7ff284d6832d6675e1e69a393b8f59d"
    b"8b2f0bd25243a66f3257654d3281df3853855d7e5d6629eab8dde495b5cdb5561242cdc44ec62538"
    b"44506decce005518fee94964d44eca979cb45bc073a8abb847c2"
)


def main(tdiff=False):

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # context.verify_mode = ssl.CERT_REQUIRED # enabled by default with
    # PROTOCOL_TLS_CLIENT

    assert context.verify_mode == ssl.CERT_REQUIRED

    # context.check_hostname = True  # enabled by default with
    # PROTOCOL_TLS_CLIENT
    # print(context.get_ciphers())

    # context.load_verify_locations(cafile='certmpy.der') # not sure how to
    # implement a external file
    # in a testd
    # context.ctx.set_ciphers('TLS-RSA-WITH-AES-256-CBC-SHA')
    context.load_verify_locations(cadata=ca_cert_chain)

    context.load_default_certs()  # not implemented in MicroPython just a mock, needed
    # in CPython to load issuer CA too,
    # otherwise verification fails.

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = socket.getaddrinfo("micropython.org", 443)[0][-1]

    # CPython can wrap the socket even if not connected yet.
    # ssl_sock = context.wrap_socket(s, server_hostname='micropython.org')
    # ssl_sock.connect(addr)

    # MicroPython needs to connect first, CPython can do this too.
    s.connect(addr)
    # server_hostname must match CN (Common Name) in the certificate
    # presented by the server
    if tdiff:
        t0 = time.ticks_us()
    ssl_sock = context.wrap_socket(s, server_hostname="micropython.org")
    if tdiff:
        delta = time.ticks_diff(time.ticks_us(), t0)
        print(f"HANDSHAKE Time = {delta/1000:6.3f} ms")
    ssl_sock.write(b"GET / HTTP/1.0\r\n\r\n")
    resp = ssl_sock.read(17)
    # print(ssl_sock.cipher())
    # print(ssl_sock.getpeercert(True))
    ssl_sock.close()
    if not tdiff:
        return resp
    else:
        return (delta/1e6) # seconds
