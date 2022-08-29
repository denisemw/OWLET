#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:34:16 2022

@author: werchd01
"""

import argparse
from run_owlet import OWLET
import os
from pathlib import Path
import sys
sys.path.append("eyetracker")


def videofile(value):
    print(value)
    if not (value.endswith('.mp4') or value.endswith('.mov') or value.endswith('.m4v')):
        raise argparse.ArgumentTypeError(
            'video file must be of type *.mp4, *.mov, or *.m4v')
    return value

def resultsfolder(value):
    value = Path(value)
    print(value)
    if not value.is_dir():
        raise argparse.ArgumentTypeError(
            'results filepath must point to a folder')
    return value

def csvfile(value):
    if not value.endswith('.csv'):
        raise argparse.ArgumentTypeError(
            'add_trial_markers argument must be of type *.csv')
    return value


def parse_arguments():
    parser = argparse.ArgumentParser(description='OWLET - Online Webcam Linked Eye Tracker')
    
    parser.add_argument('video', type=videofile, help='the subject video to process (path to video file.')
    
    parser.add_argument('results', type=resultsfolder, help='folder where results should be saved')

    parser.add_argument('--display_output', action='store_true', help='show annotated video online in a separate window')

    parser.add_argument('--add_trial_markers', type=str, help='csv file with "Time" and "Label" columns for stimulus/trial markers')
    
    parser.add_argument('--LR_tags', action='store_true', help="add tags for when baby is looking left or right (from the baby's perspective')")
    
    parser.add_argument('--LR_tags_flipped', action='store_true', help="add tags for when baby is looking left or right (from the screen's perspective)")

    parser.add_argument('--video_calib', type=videofile, help='select a video file to use for calibration.')
    
    parser.add_argument('--embedded_calib', action='store_true', help='use the subject video to calibrate OWLET.')

    parser.add_argument('--add_task_video', type=videofile, help='integrate a video of the task with the annotated subject video')
    
    parser.add_argument('--match_audio', action='store_true', help='find the task onset in the subject video by matching the audio')

    args = parser.parse_args()
    
    return args

    


if __name__ == '__main__':
    cwd = os.path.abspath(os.path.dirname(__file__))
    args = parse_arguments()
    owlet = OWLET()
    show_output = False            
    if args.display_output:
        show_output = True
  
    if args.add_trial_markers:
        success = owlet.read_stim_markers(args.add_trial_markers)
        if not success:
            print("Must specify a csv file with 'Time' and 'Label' columns.")
            raise AssertionError
        
    flip = False
    tag_lr = False
    
    if args.LR_tags:
        tag_lr = True
        
    if args.LR_tags_flipped:
        tag_lr = True
        flip = True
        
    calibrate = False
    calib_file = ""
    
    if args.video_calib:
        calibrate = True
        calib_file = args.video_calib
        
    if args.embedded_calib:
        calibrate = True
        calib_file = args.video
        
    task_file = ""
    add_taskvideo = False
    if args.add_task_video:
        task_file = args.add_task_video
        add_taskvideo = True
    
    
                
    if args.match_audio:
        if not add_taskvideo:
            print("Must specify a task video using the --add_task_video argument.")
            raise AssertionError
        
        found_match = owlet.match_audio(args.video, task_file)
        if found_match == False:
            print("no audio match found. Processing whole video instead")
            add_taskvideo = False

    if calibrate:
        owlet.calibrate_gaze(calib_file, show_output, cwd)
        
    results_folder = Path(args.results)
        
    owlet.process_subject(cwd, args.video, calib_file, str(args.results), \
                                          str(args.results), calibrate, show_output, \
                                              flip, tag_lr, add_taskvideo, task_file)
        
