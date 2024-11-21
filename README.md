1. Install the actual Tesseract OCR engine:
   mac: brew install tesseract
   windows: https://github.com/madmaze/pytesseract/wiki/Tesseract-installation-on-Windows
   Run the installer (.exe file)
   Add the installation directory to your system PATH variable
   (e.g., C:\Program Files\Tesseract-OCR)
2. Installation process

- Create a venv and activate it.

```
python -m venv .venv
```

- Activate the new environment

```
source ./.venv/bin/activate
```

3. Install the require dependent libraries

```
pip install -r ./requirements.txt

or pip install pymupdf pdfplumber pytesseract etc..
```

4. Setup local env variables .env file (contact the developer or refer to ./config.py)

5. Run the app

```
python test_file_handler.py
```
