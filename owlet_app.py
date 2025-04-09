import streamlit as st
from pathlib import Path
import os
import glob

# Import from your eyetracker package
from eyetracker import run_owlet, run_owlet_cnn

def get_task_files(task_path):
    task_video, aoi_file, stim_file = None, None, None
    if task_path:
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

# --- STREAMLIT UI ---
st.title("OWLET - Online Webcam Linked Eye Tracker")

subject_video = st.file_uploader("Upload Subject Video", type=["mp4", "mov"])
calib_video = st.file_uploader("Upload Calibration Video (optional)", type=["mp4", "mov"])
exp_folder = st.text_input("Experiment Info Folder (optional)")
use_cnn = st.radio("Face Detector Model", ["68-landmark", "CNN"]) == "CNN"
override_audio_matching = st.checkbox("Override Audio Matching")

if st.button("Run OWLET") and subject_video is not None:
    # Save uploaded files locally if needed
    subject_video_path = f"temp/{subject_video.name}"
    with open(subject_video_path, "wb") as f:
        f.write(subject_video.read())

    calib_video_path = None
    if calib_video:
        calib_video_path = f"temp/{calib_video.name}"
        with open(calib_video_path, "wb") as f:
            f.write(calib_video.read())

    # Run OWLET
    task_video, aoi_file, stim_file = get_task_files(exp_folder)

    owlet = run_owlet_cnn.OWLET_CNN() if use_cnn else run_owlet.OWLET()

    stim_df = None
    if stim_file:
        success, stim_df = owlet.read_stim_markers(stim_file)
        if not success:
            st.error("Stim file must have 'Time' and 'Label' columns.")
            st.stop()

    if calib_video_path:
        owlet.calibrate_gaze(calib_video_path, False)

    if not override_audio_matching:
        found_match = owlet.match_audio(subject_video_path, task_video)
        if not found_match:
            st.error("The task video was not found within the subject video. Processing halted.")
            st.stop()

    df, success = owlet.process_subject(subject_video_path, task_video)
    if success:
        owlet.format_output(subject_video_path, df, aoi_file, stim_df)
        st.success("Processing complete!")
    else:
        st.error("Processing failed.")
