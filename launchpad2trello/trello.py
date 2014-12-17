import logging
import re
import webbrowser

import requests
from requests_oauthlib import OAuth1


LOG = logging.getLogger(__name__)

CLIENT_NAME = 'launchpad2trello'
ENDPOINT = 'https://api.trello.com'
API_VERSION = '1'

# regular expression used for identifying tasks
TASK_RE = re.compile('^Bug ([0-9]+): ', re.MULTILINE)


def authorize(key, secret):
    url = 'https://api.trello.com/1/authorize'
    auth = OAuth1(key, secret)
    r = requests.Request(
        'GET', url, auth=auth, params={
            'key': key,
            'name': CLIENT_NAME,
            'expiration': 'never',
            'scope': 'read,write',
            'response_type': 'token'})
    prepared = r.prepare()
    webbrowser.open(prepared.url)
    print('Your web browser should be opening to authorize launchpad2trello '
          'to access Trello on your behalf. If not, follow the steps on:')
    print('')
    print('  %s' % prepared.url)
    print('')
    return raw_input('Enter your token: ')


def create_list(key, token, board_id, name, position=None):
    assert board_id
    assert 1 <= len(name) <= 16384
    assert position in (None, 'top', 'bottom') or isinstance(position, int)

    payload = {
        'name': name,
        'idBoard': board_id,
        'pos': position,
    }
    r = requests.post(
        'https://api.trello.com/1/lists',
        params={'key': key, 'token': token},
        data=payload)
    return r.body()['id']


def create_card(key, token, list_id, name, description, url):
    assert list_id
    assert 1 <= len(name) <= 16384
    assert 1 <= len(description) <= 16384
    assert url

    payload = {
        'idList': list_id,
        'name': name,
        'description': description,
        'urlSource': url,
    }
    r = requests.post(
        'https://api.trello.com/1/cards',
        params={'key': key, 'token': token},
        data=payload)
    return r.json()


def update_card_name(key, token, card_id, name):
    assert 1 <= len(name) <= 16384

    payload = {
        'value': name,
    }
    r = requests.put(
        'https://api.trello.com/1/cards/%s/name' % card_id,
        params={'key': key, 'token': token},
        data=payload)

    return r.json()


def update_card_list(key, token, card_id, list_id):
    assert card_id
    assert list_id

    payload = {
        'value': list_id,
    }
    r = requests.put(
        'https://api.trello.com/1/cards/%s/idList' % card_id,
        params={'key': key, 'token': token},
        data=payload)

    return r.json()


def update_card_label(key, token, card_id, label_color):
    assert card_id

    payload = {
        'value': label_color,
    }
    r = requests.put(
        'https://api.trello.com/1/cards/%s/labels' % card_id,
        params={'key': key, 'token': token},
        data=payload)

    return r.json()


def create_lists_as_necessary(key, token, board_id):
    # for some reason, the board ID from the website doesn't work consistently
    # as an API reference, so we need to retrieve the board ID from the API
    r = requests.get(
        'https://api.trello.com/1/boards/%s' % board_id,
        params={'key': key, 'token': token})
    board_id = r.json()['id']

    r = requests.get(
        'https://api.trello.com/1/boards/%s/lists' % board_id,
        params={'key': key, 'token': token})
    lists = r.json()

    lists_by_name = dict([(x['name'], x) for x in lists])

    def create_list_if_necessary(list_name):
        if list_name not in lists_by_name.keys():
            list_id = create_list(key, token, board_id, name=list_name)
            lists_by_name[list_name] = list_id

    create_list_if_necessary('Backlog')
    create_list_if_necessary('Approved')
    create_list_if_necessary('Doing')
    create_list_if_necessary('Dev Done')
    create_list_if_necessary('Released')

    return lists_by_name


def index_cards(key, token, board_id):
    # for some reason, the board ID from the website doesn't work consistently
    # as an API reference, so we need to retrieve the board ID from the API
    r = requests.get(
        'https://api.trello.com/1/boards/%s' % board_id,
        params={'key': key, 'token': token})
    board_id = r.json()['id']

    r = requests.get(
        'https://api.trello.com/1/boards/%s/cards' % board_id,
        params={'key': key, 'token': token})
    cards = r.json()

    cards_by_task_id = dict()
    for card in cards:
        re_match = re.search(TASK_RE, card['name'])
        if re_match:
            task_id = re_match.group(1)
            cards_by_task_id[task_id] = card

    return cards_by_task_id
