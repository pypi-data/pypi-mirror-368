<div align='center'>
	<img src=logo.png width=150>
</div>

<h1 align='center'>SpeechCapture</h1>

An easy to use library for recording and saving speech audio

<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About the Project
SpeechCapture is a Python library made to simplify the complex process of recording and saving your voice automatically from Python code.

### Features
<ul>
	<li>Automatic stop on silence</li>
	<li>Customizable silence threshold</li>
	<li>Dynamically adjust threshold based on surrounding noise</li>
	<li>Pausing and resuming recording</li>
	<li>Saving audio as .WAV at any time</li>
	<li>Recording in background threads</li>
	<li>Simultaneous recordings</li>
	<li>Stopping at any time</li>
</ul>

## Getting Started
### Prerequisites
To use SpeechCapture, you will need the following installed:
- Python 3.8 or higher

### Installation
To install, simply run in your terminal:
```bash
$ pip install speechcapture
```
Once you have installed the package, do not forget to import:
```py
import speechcapture
```
You can now start using SpeechCapture (example usage below)

<hr>

#### **PyAudio**
If installation of PyAudio, a required dependancy, fails, try running the following commands: <br>

**MacOS**
```bash
$ brew install portaudio
$ pip install pyaudio
```

**Ubuntu/Linux**
```bash
$ sudo apt install portaudio19-dev
$ pip install pyaudio
```

 ## Usage
 ```py
import speechcapture as sc

file_path = 'output.wav'

r = sc.Recorder(file_path)

r.adjust_for_ambient_noise()

r.max_seconds_of_silence = 3

r.record()
 ```

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Bilal Darwish - <a href='mailto:darwish.b.bilal@gmail.com'>darwish.b.bilal@gmail.com</a> <br>

Source Code and Issues: https://github.com/bdarwish/speechcapture/

## Acknowledgments
Dependencies:
- [PyAudio](https://pypi.org/project/PyAudio/)
- [NumPy](https://pypi.org/project/numpy/)