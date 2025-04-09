#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 18:57:55 2022

@author: werchd01
"""
import sys
sys.path.append("eyetracker")
from eyetracker import OWLET_GUI
import os
import argparse
from eyetracker import run_owlet
from eyetracker import run_owlet_cnn
import os
from pathlib import Path
import glob


def videofile(value):
    return value

def expFolder(value):
    value = Path(value)
#    if not value.is_dir():
 #       raise argparse.ArgumentTypeError(
  #          'Filepath must point to a folder with experiment info')
    return value

def parse_arguments():
    parser = argparse.ArgumentParser(description='OWLET - Online Webcam Linked Eye Tracker')
    parser.add_argument('--subject_video', type=videofile, help='subject video to be processed')
    parser.add_argument('--calib_video', default = '', type=videofile, help='subject video to be processed')
    parser.add_argument('--experiment_info', default='', type=expFolder, help='directory with optional experiment info')
    parser.add_argument('--display_output', action='store_true', help='show annotated video online in a separate window')
    parser.add_argument('--override_audio_matching', action='store_true', help='Manually override audio matching when processing pre-cropped task videos')
    parser.add_argument('--cnn',  action='store_true', help='Manually override audio matching when processing pre-cropped task videos')

    args = parser.parse_args()
    return args

def get_task_files(task_path):
    task_video, aoi_file, stim_file = None, None, None
    if task_path != '':
        taskVideos = glob.glob(os.path.join(task_path, '*.mp4'))
        aoi_files = glob.glob(os.path.join(task_path, '*AOIS*csv'))
        stim_files = glob.glob(os.path.join(task_path, '*trials*csv')) 
        
        if len(taskVideos) == 1: 
            task_video = taskVideos[0]
        if len(aoi_files) == 1: 
            aoi_file = aoi_files[0]
        if len(stim_files) == 1: 
            stim_file = stim_files[0]
    return task_video, aoi_file, stim_file

def main():
    args = parse_arguments()
    subject_video, calib_video, study_info = '', '', ''
    calib, override_audio_matching, cnn = False, False, False
    ### If arguments are not specified, ask for them from the user
    if len(sys.argv) == 1:
        subject_video = input("Enter the name of the subject video you would like to process").lower().strip()
        calib = input("Is there a calibration video you would like to use? (y/n)").lower().strip() == 'y'
        if calib:
            calib_video = input("Enter the name of the calibration video").lower().strip()
        use_study_info = input("Would you like to integrate experiment information with the output? (y/n)").lower().strip() == 'y'
        if use_study_info:
            study_info = input("Enter the directory of the experiment information: ").lower().strip() == 'y'
            print('TODO')
        if study_info != '':
            override_audio_matching = input("Do you want to find the task start by matching audio? (y/n): ").lower().strip() == 'y'
        cnn = input("Which face detector model would you like to use: \n (1) 68-landmark model \n (2) CNN model").lower().strip() == '2'

    else:
        subject_video = args.subject_video
        calib = args.calib_video != ''
        if calib:
            calib_video = args.calib
        study_info = args.experiment_info
        if args.override_audio_matching:
            override_audio_matching = True
        if args.cnn:
            cnn = True
    task_video, aoi_file, stim_file = get_task_files(study_info)
        

    if cnn: 
        owlet = run_owlet_cnn.OWLET_CNN()
        print("cnn")
    else: owlet = run_owlet.OWLET()

    success = False
    stim_df = None
    if stim_file is not None: 
        success, stim_df = owlet.read_stim_markers(stim_file)
    if not success:
        print("Trial markers file must have 'Time' and 'Label' columns.")
                    
    if calib_video != '':
        owlet.calibrate_gaze(calib_video, False)
    
    if not override_audio_matching:
        found_match = owlet.match_audio(subject_video, task_video)
        if found_match == False:
            print("The task video was not found within the subject video. Processing halted.")
            exit()
    

    df, success = owlet.process_subject(subject_video, task_video)
    if success: owlet.format_output(subject_video, df, aoi_file, stim_df)
    
if __name__ == '__main__':
    main()
   
    
   


