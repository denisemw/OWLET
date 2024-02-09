#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 12:00:47 2024

@author: werchd01
"""
import sys
import os
import librosa
import subprocess
from scipy import signal
import numpy as np
import glob
import argparse
from pathlib import Path

def videofile(value):

    return value


def taskvideo(value):
    if not (value.endswith('.mp4') or value.endswith('.mov') or value.endswith('.m4v')):
        raise argparse.ArgumentTypeError(
            'video file must be of type *.mp4, *.mov, or *.m4v')
    return value

def parse_arguments():
    parser = argparse.ArgumentParser(description='OWLET - Online Webcam Linked Eye Tracker')
    parser.add_argument('--video_dir', type=videofile, help='subject videos to crop')
    parser.add_argument('--task', type=taskvideo, help='task video')


def convert_video_to_audio_ffmpeg(video_file, cwd, output_ext="wav"):
    """Converts video to audio directly using `ffmpeg` command
    with the help of subprocess module"""
        
    ff_path = "ffmpeg/ffmpeg"
    if hasattr(sys, '_MEIPASS'):
       ffmpeg_path = os.path.join(sys._MEIPASS, ff_path)
    else:
       ffmpeg_path = os.path.join(cwd, ff_path)
        
    filename, ext = os.path.splitext(video_file)
    
    subprocess.call([ffmpeg_path, "-y", "-i", video_file, f"{filename}.{output_ext}"], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
    
    
def crop_video_ffmpeg(video_file, cwd, start, output_ext="mp4"):
    """Converts video to audio directly using `ffmpeg` command
    with the help of subprocess module"""
        
    ff_path = "ffmpeg/ffmpeg"
    if hasattr(sys, '_MEIPASS'):
       ffmpeg_path = os.path.join(sys._MEIPASS, ff_path)
    else:
       ffmpeg_path = os.path.join(cwd, ff_path)
        
    filename, ext = os.path.splitext(video_file)
    filename = filename.replace('_tasks', '')
    
    minutes = int(start / 1000 // 60)
    seconds = int(start / 1000 % 60)
    
    if seconds < 10:
        str_sec = "0" + str(seconds)
    else:
        str_sec = str(seconds)
    
    mystr = "00:0" + str(int(minutes)) + ":" + str_sec
    print(mystr)
    
    subprocess.call([ffmpeg_path, "-y", "-ss", mystr, "-i", video_file, f"{filename}.{output_ext}"], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
    

def find_offset(subject_audio, task_audio):
    """
    Returns the offset between the subject video and the start of the task
    based on matching the audio patterns using FFT and cross correlations
    
    Arguments:
        subject_audio (wav file): The audio file name of the subject audio
        task_audio (wav file): The audio file name of the task audio
        window (int): The window in which to search for a match within
        
    Returns:
        The time until the task begins in the subject video
    """
    y_within, sr_within = librosa.load(subject_audio, sr=None)
    y_find, sr_find = librosa.load(task_audio, sr=sr_within)

    c = signal.correlate(y_within, y_find, mode='valid', method='fft')
    peak = np.argmax(c)
    start = round(peak / sr_within, 2) * 1000
    sub_audio_length = 100000
    task_audio_length = 10000
    print(c[peak])
    
    if c[peak] < 60:
        start = -999
    end = start + (task_audio_length)

    return start, end, sub_audio_length, task_audio_length

def match_audio(sub, task, cwd):
    
    # try:

        convert_video_to_audio_ffmpeg(sub, cwd)
        # convert_video_to_audio_ffmpeg(task, cwd)
        
        subaudio = sub[0:-4] + ".wav" 
        # taskaudio = task[0:-4] + "wav" 
        found_match = False
        
        start, end, length, task_length = find_offset(subaudio, task)
        print(start, end, length, task_length)

        if start != -999:
            crop_video_ffmpeg(sub, cwd, start)
        os.remove(subaudio)
    #     return True
    # except:

    #     return False
    
    
def main():
    cwd = os.path.abspath(os.path.dirname(__file__))
    
    # owlet_dir = os.path.abspath(os.path.join(cwd, "\OWLET"))
    # print(owlet_dir)
    
    # args = parse_arguments()
    # print(args)
    subDir = "/Users/werchd01/Dropbox/ORCA/Subject_videos/Longitudinal/Attention_Noise/"
    taskVideo = "/Users/werchd01/Dropbox/ORCA/Subject_videos/Longitudinal/Attention_Noise/attn_noise_start.wav"
    # path = Path(taskVideo)
    # expDir = path.parent.absolute()
    # taskVid = os.path.abspath(os.path.join(expDir, taskVideo))
        # subDir = os.path.dirname(subVideo) #args.subject_folder
        
    os.chdir(subDir)
    
    
    videos = glob.glob('*.mp4') + glob.glob('*.mov')
    videos = [ x for x in videos if "annotated" not in x ]
    videos = [ x for x in videos if "calibration" not in x ]
    videos = [ x for x in videos if "Calibration" not in x ]
    
    for video in videos:
        match_audio(video, taskVideo, cwd)
        
if __name__ == '__main__':
    main()
   
    
        