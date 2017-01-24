import time
from stem.control import Controller
from stem import Signal
import requests

from functools import wraps
import errno
import os
import signal
import subprocess
from subprocess import call

def restart_tor():
    # return
    call(['killall', '-9', 'firefox'])
    call(['killall', '-9', 'tor'])
    time.sleep(5)
    call(['sh', '-c', '"/home/oles/Desktop/Browser/start-tor-browser" --detach || ([ !  -x '
                                     '"/home/oles/Desktop/Browser/start-tor-browser" ] && "$(dirname "$*")"/Browser/start-tor-browser --detach)'])
    time.sleep(30)

restart_tor()

def retry(howmany, pause):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(howmany):
                try:
                    if timeout is not None:
                        time.sleep(pause)
                    return func(*args, **kwargs)
                except Exception as e:
                    print("exception {}, sleep: {}, try {} of {}".format(e, pause, _, howmany))

        return wrapper

    return decorator


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


@retry(10, 1)
def connect_to_tor():
    try:
        # controller = Controller.from_port(port=9151)
        # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "10.10.11.220", 9150)
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)
        socket.socket = socks.socksocket
        # controller.authenticate()
        # controller.signal(Signal.NEWNYM)
        # return controller
    except Exception as e:
        # if controller:
        #     controller.close()
        raise e


@timeout(300)
def get_page_via_tor(get_url):
    controller = None
    temp = None
    pid = None
    proc = None
    ret = ''
    try:
        # proc = subprocess.Popen(['/home/oles/Desktop/Browser/start-tor-browser'], shell=False)

        # The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
#         proc = subprocess.Popen('/home/oles/Desktop/Browser/start-tor-browser', stdout=subprocess.PIPE,
#                        shell=True, preexec_fn=os.setsid)

        # call(['/home/oles/Desktop/Browser/start-tor-browser', '--detach'])

        temp = socket.socket
        controller = connect_to_tor()
        # pid = proc.pid
        r = requests.get(get_url)
        ret = r.content
    except Exception as e:
        print("!!!{}!!!".format(e))
        raise e
    finally:
        if controller:
            controller.close()
        if temp:
            socket.socket = temp
        if proc:
            time.sleep(3)
            os.killpg(os.getpgid(proc.pid), signal.SIGQUIT)  # Send the signal to all the process groups
            # os.kill(pid, signal.SIGTERM)  # or signal.SIGKILL
            time.sleep(3)

    return ret


def get_page(url, bin=False):
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
            restart_tor()

            # with urllib.request.urlopen(url) as response:
            #     html = response.read()
            # return html.decode("utf-8")
    print("Give up getting url: `%s`. empty string returned" % (url,))
    return False
