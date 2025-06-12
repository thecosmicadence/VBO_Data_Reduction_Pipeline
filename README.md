# VBO Data Reduction Pipeline (UAGS)

This repository contains a semi-automated data reduction pipeline tailored for the **Universal Astronomical Grating Spectrograph (UAGS)** at **Vainu Bappu Observatory (VBO)**. The pipeline is built using **Python**, **PyRAF**, and **DS9**, and facilitates batch CCD preprocessing and interactive spectral extraction.

## 🔧 Features

- Batch support for:
  - Bias subtraction
  - Flat field correction
  - Cosmic ray cleaning
  - Trimming based on user input
- Header-based gain and readnoise extraction
- Interactive aperture extraction
- Integration with **SAOImage DS9** for FITS visualization
- Terminal-driven but with scope for GUI development

## 🧰 Requirements

- Python 3
- IRAF & PyRAF (tested on legacy IRAF installations)
- SAOImage DS9
- Dependencies:
  - `pyfits` or `astropy.io.fits`
  - `pyds9`
  - `glob`
  - `numpy`

## 🚀 How to Use

To be updated soon...

## 📜 License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it with attribution.


