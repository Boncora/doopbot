import requests
import os
from pprint import pprint
from datetime import datetime
import time


def create_poll(options):
    strawpoll_api_key = os.getenv('STRAWPOLL_API_KEY')
    strawpoll_api_base = 'https://api.strawpoll.com/v3'
    headers = {
        'X-API-KEY': strawpoll_api_key
    }
    poll_options = [{'type': 'text', 'value': value} for value in options]
    payload = {
        "title": "🍕BATTLE!🍺",
        "poll_options": poll_options,
        "poll_config": {
            "is_private": False,
            "vote_type": "default",
            "allow_comments": True,
            "deadline_at": None,
            "duplication_checking": "ip",
            "number_of_winners": 1,
            "require_voter_names": True,
            "results_visibility": "always",
        },
        "type": "multiple_choice",
    }
    response = requests.post(f"{strawpoll_api_base}/polls", json=payload, headers=headers)
    if response:
        poll = response.json()
        return(poll["id"])
    else:
        return "Error creating strawpoll"

def get_results(id):
    strawpoll_api_key = os.getenv('STRAWPOLL_API_KEY')
    strawpoll_api_base = 'https://api.strawpoll.com/v3'
    headers = {
        'X-API-KEY': strawpoll_api_key
    }
    response = requests.get(f"{strawpoll_api_base}/polls/{id}/results", headers=headers)
    if response:
        results = response.json()
        return results
    else:
        return "Error retrieving strawpoll results"