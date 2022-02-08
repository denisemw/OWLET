# OWLET

<div id="top"></div>
<!--
*** 
*** 
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/denisemw/OWLET">
    <img src="owlet_logo.png" alt="OWLET" width="800" height="251">
  </a>

<h3 align="center">OWLET - an Open-Source Webcam-Linked Eye Tracker</h3>

  <p align="center">
    Thanks for checking out our software! OWLET is designed to process infant 
    gaze and looking behavior using webcam videos recorded on laptops or
    smartphones. If you use this software in your research, please cite us as:
    
    Werchan, D. M., Thomason, M. E., & Brito, N. H. (2022). OWLET: an 
    open-source, robust, and scalable method for infant webcam eye tracking.</h3>
    
        
 <br />
    <a href="https://github.com/denisemw/OWLET"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/denisemw/OWLET">View Demo</a>
    ·
    <a href="https://github.com/denisemw/OWLET/issues">Report Bug</a>
    ·
    <a href="https://github.com/denisemw/OWLET/issues">Request Feature</a>
  </p>
</div>




<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `denisemw`, `OWLET`, `DeniseWerchan`, `denise-werchan`, `email`, `email_client`, `OWLET`, `project_description`

<p align="right">(<a href="#top">back to top</a>)</p>



### Built in Python v. 3.8.8. With 

* [opencv]( https://pypi.org/project/opencv-python/)
* [dlib]( http://dlib.net)
* [numpy]( https://numpy.org/)
* [pandas]( https://pandas.pydata.org/)
* [scipy]( https://scipy.org/)
* [librosa]( https://librosa.org/doc/latest/index.html/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy of this software up and running follow these steps:

First, install the above packages using pip or conda install:
* opencv
  ```sh
  conda install opencv-python
  ```

Second, download or clone the repo:
   ```sh
   git clone https://github.com/denisemw/OWLET.git
   ```
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Below is an example of a processed eye tracking video.

<video width="816" height="230" controls>
      <source src=” https://github.com/denisemw/OWLET/demo.mp4” type=video/mp4>
 </video>

<p align="right">(<a href="#top">back to top</a>)</p>


<!—BEST PRACTICES AND HELPFUL TIPS -->
## Acknowledgments

OWLET works best with high quality videos, and some tips are shown below. In addition, you can alter videos in editing software (e.g., iMovie) to change the contrast/brightness or crop in on the subject’s face, which can improve performance for poor quality videos.

<a href="https://github.com/denisemw/OWLET">
    <img src="owlet_reqs.png" alt="Best Practices" width="800" height="251">
  </a>


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GNU General Public License v3.0. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Denise Werchan - [@DeniseWerchan](https://twitter.com/DeniseWerchan) – denise.werchan@nyulangone.org

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
[product-screenshot]: owlet_logo.png
![image](https://user-images.githubusercontent.com/7503173/153013523-5e52a65c-8a51-43c7-bf98-e526d7673d5f.png)
