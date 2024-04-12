#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 11:04:53 2022

@author: werchd01
"""
import sys
print(sys.path)
#from owlet import OWLET
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import tkinter.font as font
from run_owlet import OWLET
from pathlib import Path
import webbrowser
import glob


class OWLET_Interface(object):
    
    def __init__(self, cwd):
        """Returns the frame with pupils highlighted"""
        
        self.show_output = False
        self.stim_df = None
        # contains subject video (and calibration video if desired)
        self.subVideo = None
        self.subDir = "Select folder"
        self.videos = None
        self.started = False
        self.override_audio_matching = False
        self.audio_state = 'disabled'
        self.user_quit = False
        
        self.taskVideo, self.calibVideo, self.aois, self.stim_file, self.expDir = None, None, "", None, "Select folder"

        
        self.videofile = None
        self.cwd = cwd
        self.calibrate = True
        self.calibVideos = None
        self.running = False
        self.dir = str(Path.home())

        self.run_button_state = 'disabled'
        self.info_text = """
        Thanks for checking out our software! OWLET is designed to process infant gaze 
        and looking behavior using videos recorded on laptops or smartphones."""
        self.info_text2 = "Copyright (C) 2022 Denise M. Werchan, PhD."
    
    
        self.cite_text = """
        If you use this software in your research, please cite as:"""
        self.cite_text2 = """Werchan, D. M., Thomason, M. E., & Brito, N. H. (2022). OWLET: An Automated, Open-Source 
        Method for Infant Gaze Tracking using Smartphone and Webcam Recordings. Behavior Research Methods.
        """
    
        self.license_text = """
            This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License.
            You should have received a copy of the License along with this program.  If not, see https://www.gnu.org/licenses/.
    
            This program is distributed in the hope that it will be useful, but without any warranty or implied warranty. See 
            the General Public License for more details.
    
        """
        

    def display_GUI(self):    
     
        def on_closing():
            self.user_quit = True
            window.destroy()
                    
            # browse1
            ## subject folder - gets all task files and calibration files in selected folder
        def browse_sub_folder():
            folder_selected = filedialog.askdirectory(initialdir = self.dir) 
            os.chdir(folder_selected)
            self.subDir = folder_selected
            path = Path(folder_selected)
            self.dir = path.parent.absolute()

            self.videos = glob.glob('*.mp4') + glob.glob('*.mov')
            self.videos = [ x for x in self.videos if "annotated" not in x ]
            self.videos = [ x for x in self.videos if "calibration" not in x ]
            self.videos = [ x for x in self.videos if "Calibration" not in x ]
            
            
            self.calibVideos = glob.glob('*.mp4') + glob.glob('*.mov')
            # print(self.calibVideos) 
            self.calibVideos = [ x for x in self.calibVideos if "calibration" in x or "Calibration" in x ]
            # self.calibVideos = [ x for x in self.calibVideos if "Calibration" in x ]
            print(self.calibVideos)
            if folder_selected == "":
                folder_selected = "Select folder"

            new_txt = folder_selected.rsplit('/', 1)[-1]
            # print(new_txt)
            # global btn1
            btn1['text'] = new_txt
            myfunction()
        
    
        # results folder
        def browse_exp_folder():
            folder_selected = filedialog.askdirectory(initialdir = self.dir) 
            self.expDir = folder_selected
            os.chdir(folder_selected)
            self.taskVideo = glob.glob('*.mp4') + glob.glob('*.mov')
            # print("task video", self.taskVideo)
            self.aois = glob.glob('*AOIs.csv')
            self.stim_file = glob.glob('*trials*csv')
            if len(self.taskVideo) == 0: self.taskVideo = None
            if len(self.aois) == 0: 
                self.aois = ""
            else: 
                self.aois = self.aois[0]
            if len(self.stim_file) == 0: self.stim_file = None
            
            new_txt = self.expDir.rsplit('/', 1)[-1]
            # global btn3
            btn3['text'] = new_txt
            myfunction()
            can_override_audio()
            
        def match_audio_checkbox():
            self.override_audio_matching = override_audio_matching.get()
            
        
         
        def open_popup():
            
            f = font.Font(family = "Avenir", weight = "bold", size = 14)
            top= tk.Toplevel(window)
            top.title("About OWLET")   
            top.configure(bg = "#3E4149")

            # panel = tk.Label (top, image = img2, bg = "#3E4149")
            # panel.grid(row=0)
        
            lbl1 = tk.Label(top, text=self.info_text2, bg = "#3E4149", fg="white", font=('Avenir 14'))
            lbl1.grid(row=2)
            
            lbl5 = tk.Label(top, text=self.info_text, bg = "#3E4149",  fg="white", font=('Avenir 14'))
            lbl5['font'] = f
            lbl5.grid(row=1)
            
            lbl3 = tk.Label(top, text=self.cite_text, bg = "#3E4149", font=('Avenir 14'), fg = "white")
            lbl3.grid(row=3)
            
            lbl4 = tk.Label(top, text=self.cite_text2, bg = "#3E4149", font=('Arial 12'), fg = "white")
            lbl4.grid(row=4)
            
            lbl2 = tk.Label(top, text=self.license_text, bg = "#3E4149", font=('Arial 11'), fg="grey")
            lbl2.grid(row=5)
            
        def open_userguide():
            webbrowser.open("https://www.denisewerchan.com/owlet")
            
        

        
        def run_OWLET():
            # run_button['text'] = "Processing..."
            print("self.videos ", self.videos)
            
            for video in self.videos:
                
                owlet = OWLET()
                # print(video, self.taskVideo)
                task = None
                subname , ext = os.path.splitext(video)
                subname = subname.lstrip()
                # subname = os.path.basename(video)
                self.subVideo = os.path.abspath(os.path.join(self.subDir, video))

    
                cab = [ x for x in self.calibVideos if str(subname) in x ]

                file_name =  str(self.subDir) + '/' + str(subname) + "_error_log" + ".txt"   
                if self.taskVideo == "Select folder": self.taskVideo = None
                
                if self.stim_file is not None and len(self.stim_file) == 1:
                    success, self.stim_df = owlet.read_stim_markers(os.path.join(self.expDir, self.stim_file[0]))
                    
                    if not success:
                        print("Trial markers file must have 'Time' and 'Label' columns.")
                        file = open(file_name, "w")
                        file.write("Incorrect experiment info -- Trial markers file must have 'Time' and 'Label' columns.\n")
                        file.close()
                        raise AssertionError
                if cab is not None and len(cab) == 1:
                    print("Calibrating ", str(subname))
                    cab = os.path.abspath(os.path.join(self.subDir, cab[0]))
                    owlet.calibrate_gaze(cab, False, self.cwd)
                
                    
                found_match = True
                if self.taskVideo is not None and len(self.taskVideo) == 1:
                    task = os.path.abspath(os.path.join(self.expDir, self.taskVideo[0]))
                    experiment_name = os.path.basename(os.path.normpath(self.expDir))
                    file_name = str(self.subDir) + '/' + str(subname) + "_" + str(experiment_name) + "_error_log" + ".txt"
                    
                    if not self.override_audio_matching:
                        found_match = owlet.match_audio(self.subVideo, task, self.cwd)
                        print("found match ", found_match)
                        if found_match == False:
                            print("The task video was not found within the subject video. Processing halted.")

                            
                            file = open(file_name, "w")
                            file.write("The task video was not found within the subject video. Processing halted..\n")
                            file.close()
                            continue
                
                os.chdir(self.subDir)
                # if found_match == True:
                df = owlet.process_subject(self.cwd, video, self.subDir, False, task, False)
                owlet.format_output(video, task, self.subDir, self.expDir, df, self.aois, self.stim_df)
                # message = message + str(subname) + " finished\n"
                # showMessage(message)
            tk.messagebox.showinfo(title="Processing finished.", message=("Results saved in " + str(self.subDir)))
            
            

            # elif audio_var.get() == 1:
            #     found_match = self.owlet.match_audio(self.videofile, self.task_file)
            #     if found_match == False:
            #         tk.messagebox.showerror("Error", "Error: could not find audio match with task video")
            #         audio_var.set(0)
            #         self.audio_var = 0
            #         self.task_file = "Select file"
            #         task_btn["text"] = self.task_file
            #         self.add_taskvideo = 0
            #         audio_checkbox['state'] = tk.DISABLED
            #     else:
            #         if self.show_output:
            #             window.destroy()
            #         else:
            #             if self.calibrate:
            #                 run_calibration()
            #             start_owlet()

                
        # def match_audio_checkbox():
        #     self.audio_var = audio_var.get()

            
        def myfunction(*args):
            text1 = btn1['text']
            
            if text1 == "Select folder" or text1 == "":
                run_button.config(state='disabled')
                self.run_button_state = 'disabled'
            else:
                run_button.config(state='normal')
                self.run_button_state = 'normal'
                
        def can_override_audio(*args):
            text1 = btn3['text']
            
            if text1 == "Select folder" or text1 == "":
                audio_checkbox.config(state='disabled')
                self.audio_state = 'disabled'
            else:
                audio_checkbox.config(state='normal')
                self.audio_state = 'normal'
            

        try:
            window = tk.Tk()
            window.title("OWLET baby eye tracker")
            window.grid_columnconfigure(0, weight=2, uniform="fred")
            window.grid_columnconfigure(1, weight=1, uniform="fred")
            window.grid_columnconfigure(2, weight=1, uniform="fred")
            window.grid_columnconfigure(3, weight=1, uniform="fred")
            window.grid_columnconfigure(4, weight=1, uniform="fred")
            window.grid_columnconfigure(5, weight=2, uniform="fred")
            window.geometry("%dx%d+%d+%d" % (600, 500,0, 0))    
            # window.attributes('-topmost',False)
            window.eval('tk::PlaceWindow . center')
    
            window.update()
            # window.attributes('-topmost', False)
            f = font.Font(weight = "normal", size = 14)
            
            img_dir = os.path.join(self.cwd , "icons", "owlet_a1.png")
            
            lblblank2 = tk.Label(window, text=" ", bg = "#DBEFF9", fg="white")
            lblblank2.grid(row = 0, columnspan = 4)
            
            img = ImageTk.PhotoImage(Image.open(img_dir))
            panel = tk.Label (window, image = img) 
            panel.configure(bg = "#DBEFF9")
            panel.grid(row=1, columnspan=6)
            
            window.configure(bg = "#DBEFF9")
            
            # img_dir2 = os.path.join(self.cwd , "icons", "owlet_a2.png")
            # img2 = ImageTk.PhotoImage(Image.open(img_dir2))
    
    
            # lbl_output = tk.Label(window, text="Please select videos to process", bg = "#3E4149", fg="#5F9EB3")
            # lbl_output['font'] = f
            # lbl_output.grid(row = 1, columnspan = 7)
            
            lbl1 = tk.Label(window, text="Subject videos:", justify="right", anchor="e")
            lbl1['font'] = f
            lbl1.configure(bg = "#DBEFF9", fg="#7F7F7F")
            lbl1.grid(sticky = 'e', column=0, columnspan = 3, row=2)
            
            btn1_text = self.subDir.rsplit('/', 1)[-1]
            btn1 = tk.Button(window, text=btn1_text, highlightbackground = '#DBEFF9', fg = 'black', command=browse_sub_folder)
            btn1.grid(sticky = "w", column=3,columnspan = 3,  row=2)
            # btn1['font'] = f
        
            
          
            lbl3 = tk.Label(window, text="Task files (optional): ", justify="right", anchor="e")
            lbl3['font'] = f
    
            lbl3.configure(bg = "#DBEFF9",  fg="#7F7F7F")
            lbl3.grid(sticky = 'e', column=0, columnspan = 3, row=3)
            
            btn3_text = self.expDir.rsplit('/', 1)[-1]
            btn3 = tk.Button(window, text=btn3_text, highlightbackground = '#DBEFF9', fg = 'black', command=browse_exp_folder)
            btn3.grid(sticky = "w", column=3, columnspan = 3, row=3)
            
            lblblank = tk.Label(window, text=" ", bg = "#DBEFF9", fg="white")
            lblblank.grid(row = 5, columnspan = 6)
            
            
          
            override_audio_matching = tk.IntVar()
            override_audio_matching.set(self.override_audio_matching)
            audio_state = self.audio_state
            audio_checkbox = tk.Checkbutton(window, text = "Override audio pattern matching",  variable = override_audio_matching, disabledforeground='#d6d6d6',fg="#cdcdcd",
                                onvalue=1, offvalue=0, bg = "#DBEFF9", state=audio_state, command=match_audio_checkbox)
            audio_checkbox.grid(column = 0, columnspan=6, row = 4)
            
    
            
            
            
            # lblblank2 = tk.Label(window, text=" ", bg = "#3E4149", fg="white")
            # lblblank2.grid(row = 16, columnspan = 4)
            
        
            run_button = tk.Button(window, text="Run OWLET", highlightbackground = '#DBEFF9', fg = 'black', 
                                   disabledforeground = "grey", command=run_OWLET, state=self.run_button_state)
            run_button.grid(columnspan=6, row=17)
            
            lblblank2 = tk.Label(window, text=" ", bg = "#DBEFF9", fg="white")
            lblblank2.grid(row = 18, columnspan = 4)
        
            menubar = tk.Menu(window)
            window.config(menu=menubar)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="About", command = open_popup)
            filemenu.add_command(label="User guide", command = open_userguide)
            filemenu.add_command(label="Exit", command = window.destroy)
            menubar.add_cascade(label="OWLET", menu=filemenu) 
            
            window.protocol("WM_DELETE_WINDOW", on_closing)
            window.mainloop()
        
        except Exception as e:
            tk.messagebox.showerror(title = "Exception raised",message = str(e))
        
    def start_OWLET(self):
        print(self.videos)
        for video in self.videos:
            
            owlet = OWLET()
            print(video)
            subname , ext = os.path.splitext(video)
           # print(subname)
            subname = os.path.basename(video)
            self.subVideo = os.path.abspath(os.path.join(self.subDir, video))
            # subname = str(subname)

            calibVideo = [ x for x in self.calibVideos if str(subname) in x ]
             
            file_name =  str(self.subDir) + '/' + str(subname) + "_error_log" + ".txt"   
            if self.taskVideo == "Select folder": self.taskVideo = None
            
            if self.stim_file is not None and len(self.stim_file) == 1:
                success, self.stim_df = owlet.read_stim_markers(os.path.join(self.expDir, self.stim_file[0]))
                
                if not success:
                    print("Trial markers file must have 'Time' and 'Label' columns.")
                    file = open(file_name, "w")
                    file.write("Incorrect experiment info -- Trial markers file must have 'Time' and 'Label' columns.\n")
                    file.close()
                    raise AssertionError
           # print(calibVideo)
            if calibVideo is not None and len(calibVideo) == 1:
                calibVideo = os.path.abspath(os.path.join(self.subDir, calibVideo[0]))
                owlet.calibrate_gaze(calibVideo, False, self.cwd)
            
                
            
            if self.taskVideo is not None and len(self.taskVideo) == 1:
                self.taskVideo = os.path.abspath(os.path.join(self.expDir, self.taskVideo[0]))
                experiment_name = os.path.basename(os.path.normpath(self.expDir))
                error_log_file = str(self.subDir) + '/' + str(subname) + "_" + str(experiment_name) + "_error_log" + ".txt"
                # print(file_name)
                if not self.override_audio_matching:
                    found_match = owlet.match_audio(self.subVideo, self.taskVideo, self.cwd)
                    print("found match = ", found_match)
                    if found_match == False:
                        print("The task video was not found within the subject video. Processing halted.")
                        file = open(error_log_file, "w")
                        file.write("The task video was not found within the subject video. Processing halted..\n")
                        file.close()
                        exit()
            
       
            df = owlet.process_subject(cwd = self.cwd, videofile = video, subDir = self.subDir, show_output = False, task_file = self.taskVideo, calib=False)
            owlet.format_output(video, self.taskVideo, self.subDir, self.expDir, df, self.aois, self.stim_df)
    
    
        






        
    
