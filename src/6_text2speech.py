#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Daily_NLP 
@File    ：6_text2speech.py
@IDE     ：PyCharm 
@Author  ：Logan
@Date    ：2023/11/27 上午1:36 
"""

import torch
from TTS.api import TTS
import time


def my_tts(script_text_output_path, script_speech_output_path):
    # Get device
    device = "cuda:0"

    # Init TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    speaker_source = '110006.wav'

    # Run TTS
    # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
    with open(script_text_output_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Text to speech to a file
    tts.tts_to_file(text=text, speaker_wav=speaker_source, language="zh-cn", file_path=script_speech_output_path)


def main():
    local_time = time.strftime("%Y-%m-%d", time.localtime())
    script_text_output_path = 'video_script/{}/outputs.txt'.format(local_time)
    script_speech_output_path = 'video_script/{}/outputs_{}.wav'.format(local_time, local_time)
    my_tts(script_text_output_path, script_speech_output_path)


if __name__ == '__main__':
    main()
