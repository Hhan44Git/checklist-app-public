cd C:\Users\janro\Documents\heroku-git\checklist-app
CALL venv\Scripts\activate
set FLASK_APP=main.py
set FLASK_DEBUG=1
flask run --host=0.0.0.0
PAUSE