#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:34:16 2022

@author: werchd01
"""

import sys
sys.path.append("/Users/werchd01/OWLET/eyetracker")

import argparse
import run_owlet
import os
from pathlib import Path
import glob

def videofile(value):
    if not (value.endswith('.mp4') or value.endswith('.mov') or value.endswith('.m4v')):
        raise argparse.ArgumentTypeError(
            'video file must be of type *.mp4, *.mov, or *.m4v')
    return value

def expFolder(value):
    value = Path(value)
    if not value.is_dir():
        raise argparse.ArgumentTypeError(
            'Filepath must point to a folder with experiment info')
    return value

def parse_arguments():
    parser = argparse.ArgumentParser(description='OWLET - Online Webcam Linked Eye Tracker')
    parser.add_argument('subject_video', type=videofile, help='subject video to be processed')
    parser.add_argument('--experiment_info', type=expFolder, help='directory with optional experiment info')
    parser.add_argument('--display_output', action='store_true', help='show annotated video online in a separate window')
    parser.add_argument('--override_audio_matching', action='store_true', help='Manually override audio matching when processing pre-cropped task videos')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    
    cwd = os.path.abspath(os.path.dirname(__file__))
    args = parse_arguments()
    owlet = run_owlet.OWLET()
    show_output = False
    stim_df = None
    # contains subject video (and calibration video if desired)
    subVideo = args.subject_video
    subDir = os.path.dirname(subVideo) #args.subject_folder
    
    taskVideo, calibVideo, aois, stim_file, expDir = None, None, "", None, None
    
    # contains optional experiment info (task video, aois, and stimulus/trial timing info)
    if args.experiment_info:
        expDir = args.experiment_info
        os.chdir(expDir)
        taskVideo = glob.glob('*.mp4') + glob.glob('*.mov')
        aois = glob.glob('*AOIs.csv')
        stim_file = glob.glob('*trials*csv')
        if len(taskVideo) == 0: taskVideo = None
        if len(aois) == 0: 
            aois = ""
        else: 
            aois = aois[0]
        if len(stim_file) == 0: stim_file = None
    

    os.chdir(subDir)
    subname , ext = os.path.splitext(subVideo)
    subname = os.path.basename(subname)
    # subname = str(subname)
    subname = subname.replace('_tasks', '')
    print(subname, subDir)

    calibVideo = glob.glob('*calibration*.mp4') + glob.glob('*Calibration*.mp4') + glob.glob('*calibration*.mov') + glob.glob('*Calibration*.mov')
    calibVideo = [ x for x in calibVideo if "annotated" not in x ]
    calibVideo = [ x for x in calibVideo if str(subname) in x ]
    print(calibVideo)

    if args.display_output:
        show_output = True
        
        
  
    if taskVideo is not None:
        experiment_name = os.path.basename(os.path.normpath(expDir))
        file_name = str(subDir) + '/' + str(subname) + "_" + str(experiment_name) + "_error_log" + ".txt"
        print(file_name)
    else:
        file_name =  str(subDir) + '/' + str(subname) + "_error_log" + ".txt"
        print(file_name)
    
    
    if stim_file is not None and len(stim_file) == 1:
        success, stim_df = owlet.read_stim_markers(os.path.join(expDir, stim_file[0]))
        
        if not success:
            print("Trial markers file must have 'Time' and 'Label' columns.")
            file = open(file_name, "w")
            file.write("Incorrect experiment info -- Trial markers file must have 'Time' and 'Label' columns.\n")
            file.close()
            raise AssertionError
    
    if calibVideo is not None and len(calibVideo) == 1:
        calibVideo = os.path.abspath(os.path.join(subDir, calibVideo[0]))
        print(calibVideo)
        owlet.calibrate_gaze(calibVideo, show_output, cwd)
    
        
    
    if taskVideo is not None and len(taskVideo) == 1:
        taskVideo = os.path.abspath(os.path.join(expDir, taskVideo[0]))
        if not args.override_audio_matching:
            found_match = owlet.match_audio(subVideo, taskVideo)
            if found_match == False:
                print("The task video was not found within the subject video. Processing halted.")
                file = open(file_name, "w")
                file.write("The task video was not found within the subject video. Processing halted..\n")
                file.close()
                exit()

    
    df = owlet.process_subject(cwd, subVideo, subDir, show_output, taskVideo, False)
    owlet.format_output(subVideo, taskVideo, subDir, expDir, df, aois, stim_df)
    
