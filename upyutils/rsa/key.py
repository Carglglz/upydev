# -*- coding: utf-8 -*-
#
#  Copyright 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

try:
    import ujson as json
except:
    import json

import rsa.common
import rsa.core
from rsa.pem import load_pem

DEFAULT_EXPONENT = 65537


class AbstractKey(object):
    """Abstract superclass for private and public keys."""

    __slots__ = ('n', 'e')

    def __init__(self, n, e):
        self.n = n
        self.e = e


class PrivateKey(AbstractKey):

    __slots__ = ('n', 'e', 'd', 'p', 'q', 'exp1', 'exp2', 'coef')

    def __init__(self, n, e, d, p, q):
        AbstractKey.__init__(self, n, e)
        self.d = d
        self.p = p
        self.q = q

        # Calculate exponents and coefficient.
        self.exp1 = int(d % (p - 1))
        self.exp2 = int(d % (q - 1))
        self.coef = rsa.common.inverse(q, p)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return 'PrivateKey(%(n)i, %(e)i, %(d)i, %(p)i, %(q)i)' % self

    def __getstate__(self):
        """Returns the key as tuple for pickling."""
        return self.n, self.e, self.d, self.p, self.q, self.exp1, self.exp2, self.coef

    def __setstate__(self, state):
        """Sets the key from tuple."""
        self.n, self.e, self.d, self.p, self.q, self.exp1, self.exp2, self.coef = state

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, PrivateKey):
            return False

        return (self.n == other.n and
                self.e == other.e
                and self.d == other.d
                and self.p == other.p
                and self.q == other.q
                and self.exp1 == other.exp1
                and self.exp2 == other.exp2
                and self.coef == other.coef)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.n, self.e, self.d, self.p, self.q, self.exp1, self.exp2, self.coef))

    # Note that it doesn't use blinding to prevent side-channel attacks
    def encrypt(self, message):
        """Encrypts the message.
        :param message: the message to encrypt
        :type message: int
        :returns: the encrypted message
        :rtype: int
        """

        return rsa.core.encrypt_int(message, self.d, self.n)

    @classmethod
    def _load_pkcs1_der(cls, keyfile):
        """Loads a key in PKCS#1 DER format.
        :param keyfile: contents of a DER-encoded file that contains the private
            key.
        :type keyfile: bytes
        :return: a PrivateKey object
        First let's construct a DER encoded key:
        >>> import base64
        >>> b64der = 'MC4CAQACBQDeKYlRAgMBAAECBQDHn4npAgMA/icCAwDfxwIDANcXAgInbwIDAMZt'
        >>> der = base64.standard_b64decode(b64der)
        This loads the file:
        >>> PrivateKey._load_pkcs1_der(der)
        PrivateKey(3727264081, 65537, 3349121513, 65063, 57287)
        """

        from rsa.asn1 import Decoder
        decoder = Decoder()
        priv = decoder.decode(keyfile)

        # ASN.1 contents of DER encoded private key:
        #
        # RSAPrivateKey ::= SEQUENCE {
        #     version           Version,
        #     modulus           INTEGER,  -- n
        #     publicExponent    INTEGER,  -- e
        #     privateExponent   INTEGER,  -- d
        #     prime1            INTEGER,  -- p
        #     prime2            INTEGER,  -- q
        #     exponent1         INTEGER,  -- d mod (p-1)
        #     exponent2         INTEGER,  -- d mod (q-1)
        #     coefficient       INTEGER,  -- (inverse of q) mod p
        #     otherPrimeInfos   OtherPrimeInfos OPTIONAL
        # }

        if priv[0] != 0:
            raise ValueError('Unable to read this file, version %s != 0' % priv[0])

        key = cls(*priv[1:6])

        exp1, exp2, coef = priv[6:9]

        if (key.exp1, key.exp2, key.coef) != (exp1, exp2, coef):
            print('You have provided a malformed keyfile. Either the exponents '
                  'or the coefficient are incorrect. Using the correct values '
                  'instead.')

        return key

    @classmethod
    def _load_pkcs1_pem(cls, keyfile):
        """Loads a PKCS#1 PEM-encoded private key file.
        The contents of the file before the "-----BEGIN RSA PRIVATE KEY-----" and
        after the "-----END RSA PRIVATE KEY-----" lines is ignored.
        :param keyfile: contents of a PEM-encoded file that contains the private
            key.
        :type keyfile: bytes
        :return: a PrivateKey object
        """

        der = load_pem(keyfile, b'RSA PRIVATE KEY')
        return cls._load_pkcs1_der(der)


__all__ = ['PrivateKey']
