import numpy as np
import subprocess as sp
from env.field_env import FieldEnv
from env.world import printWorld


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen. From http://code.activestate.com/recipes/134892/"""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchMacCarbon()
            except(AttributeError, ImportError):
                self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt #see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)


def getKey():
    inkey = _Getch()
    import sys
    for i in range(sys.maxsize):
        k=inkey()
        if k!='':break

    return k

mapper = {"w": 3, "a": 0, "s":1, "d":2}
env = FieldEnv()
while True:
    env.reset()
    tot = 0
    step = 0
    while True:
        obs, rew, done, _ = env.step(mapper[getKey()])
        step += 1
        tot += rew
        sp.call('clear',shell=True);
        printWorld(obs)
        print(f"Reward: {rew}")
        print(f"Total Reward: {tot}")
        print(f"Step: {step}")
        if (done):
           break
