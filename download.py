import time
from stem.control import Controller
from stem import Signal
import requests

from functools import wraps
import errno
import os
import signal


import socks
import socket

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


@timeout(300)
def get_page_via_tor(get_url):
    controller = None
    temp = None
    try:
        controller = Controller.from_port(port=9151)
        temp = socket.socket
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)
        socket.socket = socks.socksocket
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        r = requests.get(get_url)
        ret = r.content
    except Exception as e:
        if temp:
            socket.socket = temp
        if controller:
            controller.close()
        raise e

    socket.socket = temp
    if controller:
        controller.close()
    return ret


def get_page(url, bin = False):
    trying = 1
    maxtry = 10
    while trying <= maxtry:
        try:
            print('page requested `%s`' % (url,))
            ret = get_page_via_tor(url)
            print('page given')
            return ret if bin else ret.decode("utf-8")
        except Exception as e:
            print("Error `%s` getting url `%s`, trying `%s` of `%s`" % (e, url, trying, maxtry))
            trying += 1
            time.sleep(1)

            # with urllib.request.urlopen(url) as response:
            #     html = response.read()
            # return html.decode("utf-8")
    print("Give up getting url: `%s`. empty string returned" % (url,))
    return False
