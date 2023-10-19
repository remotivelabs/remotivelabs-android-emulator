# Remotive Labs and Android Emulator

This is a set of Python scripts to redirect data from Remotive Labs broker to AAOS emulator.

## Setup

Make sure to install the dependencies.

```bash
pip install -r requirements.txt
```

## Run

For the script that sends location data to the emulator include the credentials from the broker:
```bash
python3 br_location_to_emu.py --url $URL --x_api_key $KEY --signal LATITUDE --signal LONGITUDE
```

## Documentation
Check docs/build/html/index.html for further details regarding this project.


