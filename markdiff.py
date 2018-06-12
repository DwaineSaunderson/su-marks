#!/usr/bin/python3

import sumarks
import json
import io
import getpass
import base64
import datetime

# No real security, just so that paswords aren't stored in plain text.
pass_enc_key = 'change_me'

def encode(clear, key=pass_enc_key):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(enc, key=pass_enc_key):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def markdiff(old, new):
    for key, value in new.items():
        try:
            if new[key][0] != old[key][0] or new[key][1] != old[key][1]:
                print("Mark for '{0}' Changed: {1} | {2} -> {3} | {4}.".format(key, old[key][0], old[key][1], new[key][0], new[key][1]))
        except(KeyError):
                print("Mark for '{0}' Added: {1} | {2}".format(key, new[key][0], new[key][1]))

if __name__ == "__main__":
    now = datetime.datetime.now()
    old_result = {}
    new_results = {}
    config = {}
    try:
        with open('config.json') as data_file:
            config = json.load(data_file)
            username = config['username']
            password = ''
            if config['save_pass']:
                password = decode(config['password'])
            else:
                password = getpass.getpass()
        sumarks.auth_user(username, password)
        new_results = sumarks.fetch_marks()

        print("Last Update: {}".format(config['last_update']))
        config['last_update'] = now.strftime("%d-%m-%Y %H:%M")

    except(FileNotFoundError):
        username = input("Username: ")
        password = getpass.getpass()
        storepass = input("Save Password? (Y/N) ").lower()
        while(storepass != 'y' and storepass != 'n'):
            storepass = input("Save Password? (Y/N) ").lower()
        if (storepass == 'y'):
            config = {"username": username, "save_pass": True, "password": encode(password), "last_update": now.strftime("%d-%m-%Y %H:%M")}
        else:
            config = {"username": username, "save_pass": False, "last_update": now.strftime("%d-%m-%Y %H:%M")}
        sumarks.auth_user(username, password)
        new_results = sumarks.fetch_marks()
    try:
        with open('results.json') as data_file:
            old_results = json.load(data_file)

    except(FileNotFoundError):
        old_results = {}

    markdiff(old_results, new_results)
    with io.open('config.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(config, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
        outfile.write(str(str_))

    with io.open('results.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(new_results, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
        outfile.write(str(str_))
