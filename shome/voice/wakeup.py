#!/usr/bin/env python

import snowboydecoder
import os

tmpdir = os.path.join(os.getcwd(), 'tmp')
try:
    os.mkdir(tmpdir)
except OSError:
    pass

path = os.path.dirname(os.path.abspath(__file__))
initword = os.path.join(path, 'resources', 'xiaopi.pmdl')
word = os.path.join(tmpdir, 'wakeup.pmdl')
try:
    os.system('cp -n ' + initword + ' ' + word)
except:
    pass

dingfile = os.path.join(path, 'resources', 'ding.wav')


class Wakeup():
    def __init__(self, model, sensitivity=0.5):
        self.model = model
        self.sensitivity = sensitivity

    def listen(self):
        print('listening...')
        detector = snowboydecoder.HotwordDetector(
            self.model, sensitivity=self.sensitivity)
        detector.start(detected_callback=self.callback)
        detector.terminate()

    def callback(self):
        snowboydecoder.play_audio_file(fname=dingfile)
        # TODO 树莓派连接SU-10A


if __name__ == "__main__":
    xiaopi = Wakeup(word)
    xiaopi.listen()
