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

<p align = “left”>Thanks for checking out our software! OWLET is designed to process infant gaze and looking behavior using webcam videos recorded on laptops or smartphones. If you use this software in your research, please cite as: <br><br> Werchan, D. M., Thomason, M. E., & Brito, N. H. (2022). OWLET: An Automated, Open-Source Method for Infant Gaze Tracking using Smartphone and Webcam Recordings. Behavior Research Methods. <br><br> Instructions for downloading and running the source code for OWLET is below. In addition, a beta version of a MacOS app to run OWLET through a user interface can be found at: [https://denisewerchan.com/owlet](https://denisewerchan.com/owlet)</p>
  
  

<p align="right">(<a href="#top">back to top</a>)</p>

### User Guide
<p align = “left”>A user guide for OWLET, which describes options for processing gaze data with OWLET in more detail, can be found at: [https://denisewerchan.com/owlet](https://denisewerchan.com/owlet)</p>  

### OWLET was built using Python v. 3.8.8. with 

* [opencv]( https://pypi.org/project/opencv-python/)
* [dlib]( http://dlib.net)
* [numpy]( https://numpy.org/)
* [pandas]( https://pandas.pydata.org/)
* [scipy]( https://scipy.org/)
* [librosa]( https://librosa.org/doc/latest/index.html/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy of this software up and running, first clone this repository:

   ```sh
   git clone https://github.com/denisemw/OWLET.git
   ```
Second, navigate to the OWLET directory and create a virtual environment. Install Anaconda if needed, then create an environment using the owlet_environment.yml file in this repository:
  
   ```sh
   conda env create -n owlet_env -f owlet_environment.yml
   ```
Then, activate the environment:
  
   ```sh
   conda activate owlet_env
   ```
<p align="right">(<a href="#top">back to top</a>)</p>
  
  <!-- RUNNING OWLET -->
## Running OWLET
  
To run OWLET using the default calibration settings:
  
  ```sh
   python owlet.py /path/to/subject/video.mp4 path/to/results/folder
   ```
  
To run OWLET using a recorded calibration video for the subject:
  
  ```sh
   python owlet.py /path/to/subject/video.mp4 path/to/results/folder --video_calib /path/to/calibration/video.mp4
   ```
  
If the calibration is embedded at the beginning of the subject video, use:
  
  ```sh
   python owlet.py /path/to/subject/video.mp4 path/to/results/folder --embedded_calib
   ```
  
 To display the annotated video output while OWLET is running:
  
  ```sh
   python owlet.py /path/to/subject/video.mp4 path/to/results/folder --display_output
   ```
  
To see descriptions of all command line options, use:
  ```sh
   python owlet.py --help
   ```
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Below is an example of a Zoom video processed using OWLET.<br><br>
  
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
    
