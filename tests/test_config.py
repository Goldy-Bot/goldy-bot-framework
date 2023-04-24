import json
from . import Config

config = Config("./test_config.json")

def test_config_data():
    assert config.json_data == json.load(open("./test_config.json", mode="r"))

def test_config_first_value():
    assert config.get("owo") == "this is suppose to be owotastic!"

def test_config_nested_value():
    assert config.get("nested_owo", "damn_tested_again", "final_owo") == "damn it, you found me!"

def test_config_not_found_value():
    assert config.get("owo", "huh", "WHAT") is None

def test_config_not_found_set_value():
    assert config.get("owo", "huh", "WHAT", default_value="BRUH") == "BRUH"