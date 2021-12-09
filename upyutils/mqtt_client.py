#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-25T04:51:43+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T18:29:54+01:00


from umqtt.simple import MQTTClient
from machine import unique_id as id
from ubinascii import hexlify


class mqtt_client(MQTTClient):
    """
    MQTTClient subscribe and publish ready!
    """

    def __init__(self, client_id, server, port=0, user=None, password=None,
                 keepalive=0, ssl=False, ssl_params={}):
        self.topic = None
        if client_id is None:
            self.id = hexlify(id())
        else:
            self.id = client_id
        self.user = user
        self.broker_addrss = server
        self.passwd = password
        self.port = port
        super().__init__(self.id, self.broker_addrss, self.port,
                         user=self.user, password=self.passwd,
                         keepalive=keepalive, ssl=False, ssl_params={})

    def callback(self, topic, message):
        msg = message.decode('utf-8')
        print('Received in topic: ', topic)
        print(msg)

    def set_def_callback(self):
        super().set_callback(self.callback)

    def subs(self, topic):
        self.topic = topic
        super().subscribe(topic)

    def pub(self, payload, topic=None):
        if topic is None:
            super().publish(self.topic, payload)
        else:
            super().publish(topic, payload)
