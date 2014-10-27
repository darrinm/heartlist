# FYI
# - playlists are limited to 500 tracks
# - at least 125 tracks can be added to the playlist with a single PUT

import os, requests, urllib, json
from flask import Flask, redirect, request

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config.from_envvar('HEARTLIST_CONFIG', silent=True)

CLIENT_ID = os.environ['HEARTLIST_CLIENT_ID']
CLIENT_SECRET = os.environ['HEARTLIST_CLIENT_SECRET']

@app.route('/')
def heartlist():
	return 'Welcome to Heartlist!'

@app.route('/authorize')
def authorize():
	callback_uri = urllib.quote(app.config['BEATS_AUTHORIZE_CALLBACK_URI'])
	return redirect('https://partner.api.beatsmusic.com/v1/oauth2/authorize?response_type=code&redirect_uri=%s&client_id=%s' % (callback_uri, CLIENT_ID))

@app.route('/beats-callback')
def beats_callback():
	# Retrieve the authorization code.

	authorization_code = request.args.get('code')
	if not authorization_code:
		return 'beats-callback error: %s' % request.args.get('error')
	#return 'beats-callback code: %s' % code

	# Get an access token.

	args = {
		'client_secret': CLIENT_SECRET, 
		'client_id': CLIENT_ID, 
		'redirect_uri': app.config['BEATS_AUTHORIZE_CALLBACK_URI'],
		'code': authorization_code,
		'grant_type': 'authorization_code'
	}
	response = requests.post('https://partner.api.beatsmusic.com/v1/oauth2/token', args)
	if response.status_code != 200:
		return 'beats-callback token request error %d, %s' % (response.status_code, str(response.text))

	result = json.loads(response.text)
	access_token = result['access_token']

	# Get the user's id.

	response = requests.get('https://partner.api.beatsmusic.com/v1/api/me', headers= { 'Authorization': 'Bearer %s' % access_token })
	if response.status_code != 200:
		return 'beats-callback user id request error %d, %s' % (response.status_code, str(response.text))

	rpc = json.loads(response.text)
	result = rpc['result']
	user_id = result['user_context']

	# Get the user's rated items.
	# TODO: loop to get them all

	response = requests.get('https://partner.api.beatsmusic.com/v1/api/users/%s/ratings?access_token=%s&limit=200' % (user_id, access_token))
	if response.status_code != 200:
		return 'beats-callback ratings request error %d, %s' % (response.status_code, str(response.text))
	rpc = json.loads(response.text)
	data = rpc['data']

	# Make a list of hearted track ids.

	track_ids = []
	for rating_item in data:
		rating = rating_item['rating']
		if rating != 1:
			continue
		ref_type = rating_item['rated']['ref_type']
		if ref_type != 'track':
			# TODO: album, playlist
			continue
		track_id = rating_item['rated']['id']
		track_ids.append(track_id)

	#s = s + 'rating: %s, type: %s, id: %s<br>' % (rating, ref_type, track_id)
	#s = s + 'rating: %s, type: %s, id: %s, <img src="https://partner.api.beatsmusic.com/v1/api/tracks/%s/images/default?client_id=%s"><br>' % (rating['rating'], rating['rated']['ref_type'], id, id, CLIENT_ID)
	#return s

	# Create a Heartlist playlist.
	# TODO: be mindful of the 500 item limit

	response = requests.post('https://partner.api.beatsmusic.com/v1/api/playlists?name=Heartlist&access_token=%s&access=private' % access_token)
	if response.status_code != 200:
		return 'beats-callback create playlist error %d, %s' % (response.status_code, str(response.text))
	# TODO: error handling
	rpc = json.loads(response.text)

	data = rpc['data']
	playlist_id = data['id']

	# Add all the tracks to the Heartlist.

	tracks = '&'.join(['track_ids=%s' % track_id for track_id in track_ids])

	response = requests.put('https://partner.api.beatsmusic.com/v1/api/playlists/%s/tracks?%s&access_token=%s' % (playlist_id, tracks, access_token))
	# TODO: error handling

	return response.text
