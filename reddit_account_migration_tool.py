import requests
import requests.auth
import json
import random
import string
import urllib.parse
import datetime
import os
import os.path
import time

USER_1 = 'USER_1'
USER_2 = 'USER_2'
INPUT_URL_TYPE_EXPORT = 'EXPORT DATA FROM'
INPUT_URL_TYPE_IMPORT = 'IMPORT DATA TO'
SCOPE_MYSUBREDDITS = 'mysubreddits'
SCOPE_SUBSCRIBE = 'subscribe'
REQUEST_DELAY_SECONDS = 3
GET_SUB_LIMIT = 1000

def auth_user(user, input_url_type, config_arr, permission_scope):
    print_auth_user_url(config_arr, permission_scope)
    auth_params_user = parse_auth_user_url(
        input_auth_user_url(input_url_type)
    )
    acceess_token_response_user = get_access_token(
        auth_params_user['code'],
        config_arr['auth_params'],
        user
    )
    if acceess_token_response_user == None:
        return None
    return {user: {**auth_params_user, **acceess_token_response_user}}

def print_auth_user_url(config_arr, permission_scope):
    auth_params = config_arr['auth_params']
    auth_params.update({
        'response_type': 'code',
        'state': random_word(12),
        'duration': 'temporary',
        'scope': permission_scope
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

def input_auth_user_url(type):
    return input('Open URL up here ^ '
    + 'in a browser to authorize the app for your Reddit user which you '
    + 'would like to ' + type + '. After successeful authorization, '
    + 'paste the result URL here: ')

def random_word(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def parse_auth_user_url(result_url):
    urllib.parse.urlsplit(result_url)
    urllib.parse.parse_qs(urllib.parse.urlsplit(result_url).query)
    return dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(result_url).query))

def get_access_token(code, auth_params, user):
    print('Requesting access token for ' + user)
    time.sleep(REQUEST_DELAY_SECONDS)
    client_auth = requests.auth.HTTPBasicAuth(auth_params['client_id'], None)
    response = requests.post('https://www.reddit.com/api/v1/access_token',
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': auth_params['redirect_uri']
        },
        auth = client_auth,
        headers = {'User-agent': 'reddit-account-migration-tool_0.0.1'}
    )
    response_body = json.loads(response.text)
    response_body
    if 'error' in response_body:
        print(response_body['error'])
        return None
    else:
        response_body['timestamp_created'] = datetime.datetime.now().timestamp()
        return response_body

def store_user_access_data(data):
    print('Storing access data in user_access_data.json')
    with open('user_access_data.json', 'w') as outfile:
        json.dump(data, outfile)

def read_user_acess_data():
    print('Reading user access data from user_access_data.json')
    if os.path.isfile('user_access_data.json') == True:
        with open('user_access_data.json', 'r') as json_file:
            data = json.load(json_file)
        return data
    return None

def get_srs(access_token):
    print('Requesting subscribed subreddits')
    time.sleep(REQUEST_DELAY_SECONDS)
    response = requests.get(
        'https://oauth.reddit.com/subreddits/mine/subscriber',
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'User-agent': 'reddit-account-migration-tool_0.0.1'
        },
        params = {
            'limit': GET_SUB_LIMIT
        }
    )
    if response.status_code == 200:
        srs_json = json.loads(response.text)
        srs = []
        for sr in srs_json['data']['children']:
            srs.append(sr['data']['name'])
        return srs
    elif response.status_code == 401:
        os.remove('user_access_data.json')
        print('You user access data seems to be invalidated.'
        + ' Try to run this script again.')
    else:
        print('Something unexpected happened, sorry :( '
        + '\nresponse: ' + response.text)
        return None

def sub_srs(access_token, srs):
    print('Subscribing to subreddits')
    time.sleep(REQUEST_DELAY_SECONDS)
    srs = ','.join(srs)
    return requests.post(
        'https://oauth.reddit.com/api/subscribe',
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'User-agent': 'reddit-account-migration-tool_0.0.1'
        },
        params = {
            'action': 'sub',
            'skip_initial_defaults': '1',
            'sr': srs
        }
    )

def read_config():
    print('Reading app config from config.json')
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
    return data

def main():
    config_arr = read_config()
    user_access_data = read_user_acess_data()
    if user_access_data == None:
        auth_data_user_1 = auth_user(
            USER_1,
            INPUT_URL_TYPE_EXPORT,
            config_arr,
            SCOPE_MYSUBREDDITS
        )
        if auth_data_user_1 == None:
            return 1
        auth_data_user_2 = auth_user(
            USER_2,
            INPUT_URL_TYPE_IMPORT,
            config_arr,
            SCOPE_SUBSCRIBE
        )
        if auth_data_user_2 == None:
            return 1
        user_access_data = {**auth_data_user_1, **auth_data_user_2}
        store_user_access_data(user_access_data)

    srs = get_srs(user_access_data[USER_1]['access_token'])
    if srs == None:
        return 1
    sub_srs_reponse = sub_srs(user_access_data[USER_2]['access_token'], srs)
    if (sub_srs_reponse.status_code):
        print('Great success! Check subs on your second account.')
    else:
        print ('Something wrong happened, here is the response from Reddit API: '
        + sub_srs_reponse)

    return 1

main()
