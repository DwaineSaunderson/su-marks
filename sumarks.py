#!/usr/bin/python3

import requests
from lxml import html
import getpass
import sys

session_requests = requests.session()


def auth_user(username, password):
    login_url = "https://sso-prod.sun.ac.za/cas/login? \
    TARGET=http://t2000-05.sun.ac.za/EksamenUitslae/EksUitslae.jsp"

    result = session_requests.get(login_url)

    tree = html.fromstring(result.text)
    login_token = list(set(tree.xpath("//input[@name='lt']/@value")))[0]
    execstr = list(set(tree.xpath("//input[@name='execution']/@value")))[0]

    payload = {
        "username": username,
        "password": password,
        "lt": login_token,
        "execution": execstr,
        "_eventId": "submit"
    }

    result = session_requests.post(
        login_url,
        data=payload,
        headers=dict(referer=login_url)
    )


def fetch_marks():

    url = "http://t2000-05.sun.ac.za/EksamenUitslae/EksUitslae.jsp"

    result = session_requests.get(
        url,
        headers=dict(referer=url)
    )

    tree = html.fromstring(result.text)
    table = tree.xpath("//table[2]")

    result = {}

    for i in range(2, len(table[0])):
        modname = table[0][i][1].text_content()
        modname = ' '.join(modname.split())
        modmark = table[0][i][4].text_content()
        modmark = ' '.join(modmark.split())
        if modmark == '':
            modmark = u"\u2022"
        modstatus = table[0][i][5].text_content()
        modstatus = ' '.join(modstatus.split())
        result[modname] = [modmark, modstatus]
    return result


def print_results(results_dict):
    for key, value in results_dict.items():
        print("{0} - {1}% - {2}".format(key, value[0], value[1]))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <Username>".format(sys.argv[0]))
        exit()
    username = sys.argv[1]
    password = getpass.getpass()
    auth_user(username, password)
    try:
        result = fetch_marks()
        print_results(result)
    except(IndexError):
        print("Parsing Error (Check Password?)")
        exit(1)
