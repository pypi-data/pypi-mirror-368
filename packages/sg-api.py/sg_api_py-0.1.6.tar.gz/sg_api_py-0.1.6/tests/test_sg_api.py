import pytest
from sg_api_py import characters, episodes

def test_characters():
    assert characters(1, 218, "title") == "Cho Sang-woo"
    assert characters(2, 215, "name") == "Unknown"
    assert characters(3, 100, "fate") == "{'status': 'Deceased', 'died': ['November 6, 2024', 'Sky Squid Game'], 'cause_of_death': 'Pushed off triangle pillar by Lee Myung-gi with pole and fell to death'}"

def test_episodes():
    assert episodes(1, 4, "title") == "Stick to the Team"
    assert episodes(2, 2, "episode_details") == "{'Season': '2', 'Episode': '2', 'Overall': '11'}"
    assert episodes(3, 5, "episode_information") == "{'Duration': '62 minutes', 'Air Date': 'June 27, 2025', 'Writer': 'Hwang Dong-hyuk', 'Director': 'Hwang Dong-hyuk'}"


