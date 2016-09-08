# coding: utf-8

import signal
import time

from tornado import ioloop, web
from sockjs.tornado import SockJSRouter

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from main.tornado_sockjs import TornadoSockJS

server_settings = {
    "xheaders" : True,
}


class Command(BaseCommand):
    args = '[host:port_number]'
    help = 'Starts the Tornado SockJS server.'

    def sig_handler(self, sig, frame):
        ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        io_loop = ioloop.IOLoop.instance()
        io_loop.add_timeout(time.time() + 2, io_loop.stop)

    def handle(self, *args, **options):
        if len(args) == 1:
            try:
                host, port = args[0].split(':')
                port = int(port)
            except ValueError:
                raise CommandError('Invalid host:port specified')
        else:
            host = '127.0.0.1'
            port = 8888

        print "Start Tornado SockJS server at: %s:%s" % (host, port)

        router = SockJSRouter(TornadoSockJS, "/tornado")
        app = web.Application(router.urls)
        app.listen(port, **server_settings)

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

        ioloop.IOLoop.instance().start()
