# texter-adventure

A system for running a CYOA/text adventure type game through twilio, with a graph backend. This is a common use case, right?

## Instructions

- Install and start [Neo4j](http://neo4j.com/download/) and [ProstgreSQL](http://www.postgresql.org/download/).
- Create `dev-settings.ini` and `prod-settings.ini` with your development and production API keys from Twilio. The files should follow this format:
```
[twilio]
account_sid=XXXXXXXXXXXXXXXXXXXXXXXXXX
auth_token=XXXXXXXXXXXXXXXXXXX
sender=+12223334444
```
- Create your virtualenv and use `pip` to install `requirements.txt`
```
$ virtualenv .
$ source bin/activate
$ pip install -r requirements.txt
```
- Initialize the database. One way to do this:
```
$ python
>> from WebRunner import db
>> db.create_all()
```
- Populate a Neo4j graph with the game data, or use the `BuildFromScapple.py` script in `utilities/` to populate the graph from a [scapple](https://www.literatureandlatte.com/scapple.php) file.
- Run `WebRunner.py` and open `localhost:4000` in your browser
