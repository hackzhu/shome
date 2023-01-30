#!/usr/bin/env python

import snowboydecoder
import os


class Awake():
    def __init__(self, model, sensitivity=0.5, sleep_time=0.03):
        self.model = model
        self.sensitivity = sensitivity
        self.sleep_time = sleep_time

    def run(self):
        print('listening...')
        detector = snowboydecoder.HotwordDetector(
            self.model, sensitivity=self.sensitivity)
        detector.start(
            detected_callback=snowboydecoder.play_audio_file, sleep_time=self.sleep_time)
        detector.terminate()


# 测试
if __name__ == "__main__":
    xiaopi = Awake(os.path.dirname(os.path.abspath(__file__)) + '/xiaopi.pmdl')
    xiaopi.run()
