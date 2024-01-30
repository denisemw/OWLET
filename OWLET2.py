#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 18:57:55 2022

@author: werchd01
"""
import sys
sys.path.append("eyetracker")
import OWLET_GUI
import os

def main():
    cwd = os.path.abspath(os.path.dirname(__file__))
    print(cwd)
    
    # owlet_dir = os.path.abspath(os.path.join(cwd, "\OWLET"))
    # print(owlet_dir)
    
    
    
    owlet_gui = OWLET_GUI.OWLET_Interface(cwd)    
    continue_running = True
    started = False
    while continue_running:  
        print(owlet_gui.started)
        owlet_gui.display_GUI()
        # if owlet_gui.started:
        #     owlet_gui.start_OWLET()
        continue_running = not(owlet_gui.user_quit)
    
if __name__ == '__main__':
    main()
   
    
   


