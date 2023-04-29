# checklist-app-public
A simple Flask App abused as DesktopApp, which has a Trade Overview for Binance Futures API and a technical indicator Checklist for multiple timeframes.

Installation for Windows 10:

1) A python installtion is required. Version 3.11.2 was used for the development.

2) Create the Virtual Environments (venv) folder within the main folder:
- Within a cmd window: py -3 -m venv venv

3) StartInFlask_INSTALL.bat for "automatic" install of Flask and the Requirements. Close cmd window afterwards.

4) Start with StartChecklist.bat

If problem: https://flask.palletsprojects.com/en/2.2.x/installation/#virtual-environments

5) You need to create an API for Binance Futures and whitelist the IP if you want to use trade overview. Default is set for BTCBUSD-Perpetual Futures.

Feel free to modify and use any of that Spaghetti code for your own liking.
