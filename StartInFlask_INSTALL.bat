cd
CALL venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=main.py
set FLASK_DEBUG=1
flask run --host=0.0.0.0
PAUSE