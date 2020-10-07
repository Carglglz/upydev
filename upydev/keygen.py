

KEYGEN_HELP = """
> KEYGEN: Usage '$ upydev ACTION [opts]'
    ACTIONS:
        - gen_rsakey: To generate RSA-2048 bit key that will be shared with the device
                      (it is unique for each device) use -tfkey to send this key to the
                      device (use only if connected directly to the AP of the device or a
                      "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                      upload the key (it is stored in upydev.__path__) by USB/Serial connection.

        - rf_wrkey: To "refresh" the WebREPL password with a new random password derivated from
                    the RSA key previously generated. A token then is sent to the device to generate
                    the same password from the RSA key previously uploaded. This won't leave
                    any clues in the TCP Websocekts packages of the current WebREPL password.
                    (Only the token will be visible; check this using wireshark)
                    (This needs upysecrets.py)

        - sslgen_key: (This needs openssl available in $PATH)
                       To generate ECDSA key and a self-signed certificate to enable SSL sockets
                       This needs a passphrase, that will be required every time the key is loaded.
                       Use -tfkey to upload this key to the device
                       (use only if connected directly to the AP of the device or a
                       "secure" wifi e.g. local/home). If not connected to a "secure" wifi
                       upload the key (it is stored in upydev.__path__) by USB/Serial connection.
"""
