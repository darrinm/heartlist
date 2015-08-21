=== heartlist
Git URL:       git@heroku.com:heartlist.git
Owner Email:   darrin@massena.com
Region:        us
Repo Size:     116k
Slug Size:     30M
Stack:         cedar
Web URL:       https://heartlist.herokuapp.com/
===

RUN LOCALLY
- (one time) pip install -r requirements.txt
- source venv/bin/activate
- export HEARTLIST_CLIENT_SECRET=Beats client secret
- export HEARTLIST_CLIENT_ID=Beats client id
- foreman start

DEPLOY
- git push heroku master

(https://devcenter.heroku.com/articles/getting-started-with-python-o)

USAGE: GENERATE NEW HEARTLIST
- https://heartlist.herokuapp.com/authorize
