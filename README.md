# Copium Automation Script

This project contains automation scripts designed to interact with a web-based quiz or assessment system. It uses optical character recognition (OCR) to read questions and answers from the screen and automatically selects answers based on predefined rules.

## Requirements

- Python 3.x
- Libraries:
  - pyautogui
  - pytesseract
  - Pillow (PIL)
  - pygetwindow
  - fuzzywuzzy

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/Arch3nemy7/copium-esport.git
   ```
2. Install the required libraries:
   ```sh
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR and specify its location in the config file.
   
## Usage

There are two main scripts:

1. `copium.py`: Basic version for single-run automation
2. `copium_hard.py`: Extended version for continuous automation

To run the basic version:
```sh
python copium.py
```

To run the extended version:
```sh
python copium_hard.py
```

## Disclaimer

This script is intended for educational purposes only. Use it responsibly and in compliance with the terms of service of the target application.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.