import pandas as pd
import numpy as np
import cv2
import os
import math
import argparse
import os
from pathlib import Path
import glob

def locf_with_limit(series, max_consecutive_missing=30):
    # Create a boolean mask for missing values
    missing_mask = series.isnull()

    # Use a forward-fill method to fill the series
    filled_series = series.copy()
    filled_series.ffill(inplace=True)

    # Find the lengths of consecutive missing values
    consecutive_counts = missing_mask.astype(int).groupby((missing_mask != missing_mask.shift()).cumsum()).transform('sum')

    # Only retain the sections where consecutive missing values are less than the limit
    for start, count in consecutive_counts.iteritems():
        if count > max_consecutive_missing:
            # If the count of consecutive NaNs is greater than the limit, revert the fill
            filled_series[start:start + count] = series[start:start + count]

    return filled_series






color = (255, 255, 0)
# face_detector = dlib.get_frontal_face_detector()

def update_frame(xcoord, ycoord, frame, timestamp, aois):
    text = "away"
    frame = cv2.resize(frame, (960,540))
    if xcoord >= 0 and xcoord <= 960:
            text = "looking"   
            if ycoord < 0: ycoord = 0
            if ycoord > 540: ycoord = 540 
            cv2.circle(frame, (xcoord+960, ycoord), 15, color, 2)  



        
    cv2.putText(frame, text, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
    cv2.putText(frame, str(round(timestamp,0)), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)


def process_subject(videofile, task_file, csv_file, aoi_file):
        """

        """
    
        # Step 1: Read the CSV file
        df = pd.read_csv(csv_file)

        # Now you can proceed with imputing missing values
        imputed_x = locf_with_limit(df['X-coord'])
        imputed_y = locf_with_limit(df['Y-coord'])

        sub_file, ext = os.path.splitext(videofile)
        ret2 = True
        taskname = ""
        if task_file is not None:
            taskname = str(os.path.basename(task_file)[0:-4])
            if taskname in str(sub_file):
                taskname = ""
            else:
                taskname = "_" + taskname

        outfile = str(sub_file) + taskname + "_annotated2.mp4"                
        cap = cv2.VideoCapture(videofile)   # capturing the baby video from the given path
        fps = cap.get(5)

        frameval = math.ceil(fps) // 30 # downsamples videos to 30 fps
        if frameval < 1: frameval = 1
        if fps > 30: fps = 30

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        frame_shape = (960, 540)

        if task_file is not None:
            cap2 = cv2.VideoCapture(task_file)   # capturing the task video from the given path
            frame_shape = (1920, 540)
        out = cv2.VideoWriter(outfile, fourcc, fps, frame_shape)
        
        ret, frame = cap.read()
        height, width, _ = frame.shape
        resize = (height != 540 or width!=960)
        count = 0

        while (cap.isOpened()):
            ret, frame = cap.read()
            frameId = cap.get(1) #current frame number
            if (ret == False or ret2 == False):  
                break
            if (frameId % frameval == 0):
                xcoord = imputed_x[count]
                ycoord = imputed_y[count]
                count+=1
                time = cap.get(cv2.CAP_PROP_POS_MSEC)
                if resize: frame = cv2.resize(frame, (960,540))  
                
                # concat frames
                if task_file is not None:
                    ret2, frame2 = cap2.read()   
                    if ret2==False: break
                    frame2 = update_frame(xcoord, ycoord, frame2, time)
                    frame = cv2.hconcat([frame, frame2])
                    
                out.write(frame)
                
                cv2.waitKey(1)                         
                    
        cap.release()
        if task_file is not None:
            cap2.release()
        out.release()
        cv2.destroyAllWindows()
        df["X-coord"] = imputed_x
        df['Y-coord'] = imputed_y

        if aoi_file is not None:
            aois = pd.read_csv(aoi_file)
            for i in range(len(df)): 
                for j in range(len(aois)):
                    if df.loc[i, "X-coord"] in range(aois.loc[j, 'X1'],aois.loc[j, 'X2']) \
                        and df.loc[i, "Y-coord"] in range(aois.loc[j, 'Y1'],aois.loc[j, 'Y2']):
                        df.loc[i, "Tag"] = aois.loc[j, 'AOI']
                        break
        else:
            for i in range(len(df)):
                if df.loc[i, "X-coord"] in range(0,380):
                    df.loc[i, "Tag"] = "Left"
                elif df.loc[i, "X-coord"] in range(580,960):
                    df.loc[i, "Tag"] = "Right"

        csv_file = csv_file.replace('.csv', '2.csv')        
        df.to_csv(csv_file, index = False)

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
    parser.add_argument('--experiment_info', type=expFolder, help='directory with optional experiment info')
    args = parser.parse_args()
    return args



def main():
    cwd = os.path.abspath(os.path.dirname(__file__))
    
    # owlet_dir = os.path.abspath(os.path.join(cwd, "\OWLET"))
    # print(owlet_dir)
    
    args = parse_arguments()

    value = Path(args.subject_video)
    if not value.is_dir():
        subVideo = args.subject_video
        videos = [subVideo]
        subDir = os.path.dirname(subVideo) #args.subject_folder
        os.chdir(subDir)
    else:
        subDir = args.subject_video        
        os.chdir(subDir)
        videos = glob.glob('*.mp4') + glob.glob('*.mov')
        videos = [ x for x in videos if "annotated" not in x ]
        videos = [ x for x in videos if "calibration" not in x ]
        videos = [ x for x in videos if "original" not in x ]
        videos = [ x for x in videos if "Calibration" not in x ]

    csvFiles = glob.glob('*.mp4') + glob.glob('*.mov')
    csvFiles = [ x for x in csvFiles if "calibration" in x or "Calibration" in x ]


    for subVideo in videos:
        
        taskVideo, csvFile, aois, expDir, taskName = None, None, "", None, ""
        
        # contains optional experiment info (task video, aois, and stimulus/trial timing info)
        if args.experiment_info:
            expDir = args.experiment_info
            os.chdir(expDir)
            taskVideo = glob.glob('*.mp4') + glob.glob('*.mov')
            
            
            aois = glob.glob('*AOIs.csv')
            stim_file = glob.glob('*trials*csv')
            if len(taskVideo) != 1: 
                taskVideo = None
            else: 
                taskName = os.path.basename(os.path.normpath(expDir))
                taskName = str(taskName).lower()
            if len(aois) != 1: 
                aoi_file = None
            else: 
                aoi_file = os.path.abspath(os.path.join(expDir, aois[0]))
            # if len(stim_file) != 0: stim_file = None
            
        os.chdir(subDir)
        subVideo = os.path.basename(subVideo)
        subname , ext = os.path.splitext(subVideo)
        subname = str(subname).lower()

        csvFiles_tmp = [ x for x in csvFiles if str(subname) in x ]
        csvFiles_tmp = [ x for x in csvFiles_tmp if "calibration" not in x ]

        if taskName != "":
            csvFiles_tmp = [ x for x in csvFiles_tmp if taskName in x ]
            taskName = "_" + taskName
            subname = str(subname).replace(taskName, '')
            print(subname)

        if taskVideo is not None and len(taskVideo) == 1:
            taskVideo = os.path.abspath(os.path.join(expDir, taskVideo[0]))
        csvFile = os.path.abspath(os.path.join(subDir, csvFiles_tmp[0]))   
        process_subject(subVideo, taskVideo, csvFile, aoi_file)


if __name__ == '__main__':
    main()
   
    