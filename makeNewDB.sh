#! /bin/bash
export FLASK_APP =app.py
flask db init # do this if you have not used the database locally yet
flask db migrate -m "change"
