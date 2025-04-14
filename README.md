# OWLET

<div id="top"></div>
<!--
*** 
*** 
-->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/denisemw/OWLET">
    <img src="eyetracker/Images/owlet_logo.png" alt="OWLET" width="720" height="226">
  </a>

<div align="left">

<!-- ABOUT THE PROJECT -->
## About The Project

<p align = “left”>Thanks for checking out our software! OWLET is designed to process infant gaze and looking behavior using webcam videos recorded on laptops or smartphones. Instructions for downloading and running the source code for OWLET is below. In addition, a user guide, which describes options for processing gaze data with OWLET in more detail, can be found at: https://denisewerchan.com/owlet. If you use this software in your research, please cite as: 
  
```bash
Werchan, D. M., Thomason, M. E., & Brito, N. H. (2022). OWLET: An Automated, Open-Source Method for Infant Gaze Tracking using Smartphone and Webcam Recordings. Behavior Research Methods.
   ```
## How it works
OWLET analyzes pre-recorded webcam or smartphone videos to estimate where an infant was looking during a task. Here's what it does:
1. **Calibrates gaze**  
   - Uses default settings based on prior data (Werchan et al., 2023)  
   - Or, uses a custom calibration video of the infant looking left, right, up, and down (if provided)
2. **Estimates gaze for each frame**  
   - Determines where the infant was looking (x/y coordinates on the screen)
3. **Generates output**  
   - Saves a CSV file with gaze data for every frame  
   - Includes which part of the screen the infant looked at: `left`, `right`, or `away`

OWLET also includes optional features that allow you to:
- **Auto-detect task start time**  
  - Matches the audio in the infant’s video with the task video to find where the task begins
- **Integrate trial info**  
  - Links frame-by-frame gaze with trial start times (if a `trials.csv` file is provided)
- **Use custom AOIs**  
  - Tags gaze data using custom areas of interest (if an `AOIs.csv` file is provided)
- **Create an overlaid video to visualize gaze patterns**  
  - Combines the infant’s video with the task video and overlays gaze points on it

<!-- GETTING STARTED -->
## Set-up guide for Mac OS Users 

### ✅ Step 1: Clone the GitHub repository:
1. Open **Terminal** (Press ⌘ + Space, type “Terminal”, hit Enter).
2. Copy and paste this line and press Enter:
   ```sh
   git clone https://github.com/denisemw/OWLET.git
   ```
### ✅ Step 2: Install Homebrew (if you don’t already have it)
Homebrew is a package manager for Mac.
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
> When it's done, run:
```bash
brew doctor
```
Make sure it says "Your system is ready to brew."

### ✅ Step 3: Install system dependencies
These are tools that the Python packages need under the hood:
```bash
brew install cmake ffmpeg pkg-config
brew install libomp # Needed for `numba` and `scikit-learn` on some Macs
```
### ✅ Step 4: Install Python (if not already installed)
We recommend installing Python via Homebrew to avoid messing with the Mac system Python.
```bash
brew install python
```
### ✅ Step 5: Create and activate a virtual environment (recommended)
Create and activate a virtual environment to keep dependencies isolated:
```bash
python -m venv owlet_env
source owlet_env/bin/activate
```
### ✅ Step 6: Upgrade pip and install dependencies
We recommend using the 'requirements.txt' file to install dependencies:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
### 🧼 Optional: If Installation Fails
If you run into errors with `dlib`, run this:
```sh
brew install boost boost-python3
```
And then retry the install with:
```sh
pip install dlib
```

  <!-- RUNNING OWLET -->
  ## Running OWLET
You can use OWLET in two ways: with a simple graphical interface (GUI), or through the command line.
### Option 1: Run with the GUI (easiest)
Just run this command:
```bash
python OWLET.py
```
A window will pop up where you can select the folder with your subject videos. You can also optionally add task info like:
* The task video that was shown to the subject
* A file with trial start times
* A file with Areas of Interest (AOIs)

### Option 2: Run from the command line
Basic usage:
```sh
python OWLET.py --subject_video /path/to/subject/videos
```
If you also want to include task files (like a task video or AOIs), use:
  ```sh
   python OWLET.py /path/to/subject/videos --experiment_info /path/to/experiment/folder
   ```
Make sure the experiment folder contains your task video and/or CSV files (`trials.csv`, `AOIs.csv`)

<!-- OPTIONAL FILES -->
## Optional task files
OWLET lets you include extra files to help connect the gaze data with what was shown during the task. You can add the following files to an optional "task" folder:

1. **Task Video** (.mov or .mp4, max 30fps): If you include a video of the task, OWLET will overlay the infant’s gaze onto this video in the final annotated output.

2. **Trial Info CSV** (`trials.csv`): This file should have a `Time` column (start time of each trial or condition) and a `Labels` column (name of each trial/condition). OWLET uses this to organize gaze data by trial or condition.

3. **AOIs CSV** (`AOIs.csv`): Use this to define custom Areas of Interest (AOIs) on the task video. The file should have columns for `AOI`, `x1`, `y1`, `x2`, and `y2`, assuming a 960x540 resolution. If you don’t include this, OWLET will use default AOIs: Left, Right, and Away.

<!-- AUDIO MATCHING -->
## Audio matching
If you include a task video, OWLET will try to automatically match the audio in the task video to the audio in the subject video. This trims the start of the subject video to sync with the task, so you don’t have to edit it manually.

However, if OWLET can’t find an audio match (e.g., the task start is missing, there’s no sound, or background noise is too loud), it will skip processing that video.

To override optional audio matching, use the '--override_audio_matching' flag:
```sh
   python OWLET.py --subject_video /path/to/subject/videos --experiment_info /path/to/experiment/folder --override_audio_matching
```
<!-- USAGE EXAMPLES -->
## Usage
Below is an example of a Zoom video processed using OWLET:
<div align="center">
<h3 >OWLET Demo:</h3>
<a href="https://github.com/denisemw/OWLET">
    <img src="eyetracker/Images/demo.gif" alt="OWLET Demo">
  </a>
<div align="left">
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- BEST PRACTICES -->
## Best Practices and Helpful Tips

OWLET works best with high quality videos, and some tips are shown below. In addition, you can alter videos in editing software (e.g., iMovie) to change the contrast/brightness or crop in on the subject’s face, which can improve performance for poor quality videos. <br><br>
<div align="center">
<h3 >Tips for Recording Videos:</h3>
<a href="https://github.com/denisemw/OWLET/">
    <img src="eyetracker/Images/owlet_reqs.png" alt="Best Practices" width="360" height="432">
  </a>
<div align="left">
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the GNU General Public License v3.0. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Denise Werchan - [denisewerchan.com](https://denisewerchan.com) – [@DeniseWerchan](https://twitter.com/DeniseWerchan) – denise.werchan@nyulangone.org

Project Link: [https://github.com/denisemw/OWLET](https://github.com/denisemw/OWLET)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/denisemw/OWLET.svg?style=for-the-badge
[contributors-url]: https://github.com/denisemw/OWLET/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/denisemw/OWLET.svg?style=for-the-badge
[forks-url]: https://github.com/denisemw/OWLET/network/members
[stars-shield]: https://img.shields.io/github/stars/denisemw/OWLET.svg?style=for-the-badge
[stars-url]: https://github.com/denisemw/OWLET/stargazers
[issues-shield]: https://img.shields.io/github/issues/denisemw/OWLET.svg?style=for-the-badge
[issues-url]: https://github.com/denisemw/OWLET/issues
[license-shield]: https://img.shields.io/github/license/denisemw/OWLET.svg?style=for-the-badge
[license-url]: https://github.com/denisemw/OWLET/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/denise-werchan
[product-screenshot]: Images/owlet_logo.png
</p>
    
