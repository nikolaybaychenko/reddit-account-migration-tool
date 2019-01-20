import requests
import json

def get_access_token():
	response = requests.get('https://www.reddit.com/api/v1/access_token', 
		params={
			'grant_type': 'authorization_code',
			'code': 'rkbzRbg9ExkcVhbeh9Pj4UOO8E0',
			'redirect_uri': 'https://gitlab.com/nikolaychenko/reddit-account-migration-tool'
		}, 
		auth=('OdJwTlAGnx0C2A', 'H8duUYgi59H1gRhU7PlSgazxRBc')
	)
	return response.text

def get_srs(access_token):
	response = requests.get(
		'https://oauth.reddit.com/subreddits/mine/subscriber', 
		headers={'Authorization': 'Bearer ' + access_token}
	)
	get_srs_response(access_token)
	if response.status_code == 200:
		srs_json = json.loads(response.text)
		srs = []
		for sr in srs_json['data']['children']:
			srs.append(sr['data']['id'])
		return srs
	else:
		return None

def sub_srs(access_token, srs)
	return requests.post(
		'https://oauth.reddit.com/api/subscribe', 
		params={'Authorization': 'Bearer ' + access_token}, 
		headers={
			'action': 'sub',
			'skip_initial_defaults': 1,
			'sr': sr
		}
	)

def main():
	srs = get_srs('237179589904-O_3tELFgdZG1ura3IlSn4KsK3v0')
	sub_srs(srs)
	print(subreddits_ids)

main()
