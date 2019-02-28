import requests
import requests.auth
import json
import random
import string
import urllib.parse

def print_auth_user_url(config_arr):
    auth_params = config_arr['auth_params']
    auth_params.update({
        'response_type': 'code',
        'state': random_word(12),
        'duration': 'permanent',
        'scope': 'mysubreddits'
    })
    auth_params_string = ''
    for key in auth_params:
        auth_params_string += key + '=' + auth_params[key] + '&'
    print(urllib.parse.urlunparse((
        'https',
        'reddit.com',
        '/api/v1/authorize',
        None,
        auth_params_string,
        None
    )))

def random_word(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def parse_auth_user_url(result_url):
    urllib.parse.urlsplit(result_url)
    urllib.parse.parse_qs(urllib.parse.urlsplit(result_url).query)
    return dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(result_url).query))

def get_access_token(code, auth_params):
    client_auth = requests.auth.HTTPBasicAuth(auth_params['client_id'], None)
    response = requests.post('https://www.reddit.com/api/v1/access_token',
        params={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': auth_params['redirect_uri']
        },
        auth=client_auth,
        headers={'User-agent': 'reddit-account-migration-tool_0.0.1'}
    )
    response_body = json.loads(response.text)
    print(response_body)
    if (response_body['error'] == 'invalid_grant'):
        print(response_body['error'])
        return None
    else:
        return response_body

#def refresh_access_token():
    # response = requests.get('https://www.reddit.com/api/v1/access_token',
    #     params={
    #         'grant_type': 'refresh_token',
    #         'refresh_token':
    #   },
    #     auth=('OdJwTlAGnx0C2A', 'H8duUYgi59H1gRhU7PlSgazxRBc')

# def get_srs(access_token):
#     response = requests.get(
#         'https://oauth.reddit.com/subreddits/mine/subscriber',
#         headers={'Authorization': 'Bearer ' + access_token}
#     )
#     get_srs_response(access_token)
#     if response.status_code == 200:
#         srs_json = json.loads(response.text)
#         srs = []
#         for sr in srs_json['data']['children']:
#             srs.append(sr['data']['id'])
#         return srs
#     else:
#         return None

# def sub_srs(access_token, srs):
#     return requests.post(
#         'https://oauth.reddit.com/api/subscribe',
#         params={'Authorization': 'Bearer ' + access_token},
#         headers={
#             'action': 'sub',
#             'skip_initial_defaults': 1,
#             'sr': sr
#         }
#     )

def read_config():
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
    return data

def main():
    config_arr = read_config()
    #print_auth_user_url(config_arr)
    auth_user_params = parse_auth_user_url(input("Copy URL up here ^ authorize the app and paste the result URL here: "))
    result = get_access_token(auth_user_params['code'], config_arr['auth_params'])
    print(result)

main()
