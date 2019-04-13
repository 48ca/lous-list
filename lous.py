#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as bs
import argparse
from sys import argv, exit
from socket import gaierror
from time import sleep

from notifications.messenger import MessengerNotifier
from dotenv import load_dotenv
from os.path import join, dirname, exists
from os import environ, getenv

lous_list = "https://rabi.phys.virginia.edu/mySIS/CS2"
list_url =  "{}/{}".format(lous_list, "index.php")
page_url =  "{}/{}".format(lous_list, "page.php")

parser = argparse.ArgumentParser(description="CLI and notifier for Lou's list")
parser.add_argument('-g', '--group')
parser.add_argument('-c', '--course')
parser.add_argument('-s', '--semester', default=1198)
parser.add_argument('-n', '--notify', action='store_const', const=True, default=False)
args = parser.parse_args(argv[1:])

## Check if given group is valid

def pull_groups(sem):
    list_params = { "Semester": sem }
    r = requests.get(list_url, params = list_params)
    soup = bs(r.content, 'html.parser')
    groups = soup.select('td.IndexTable4')

    all_groups = []
    for g in groups:
        # This code is likely to break
        if g.a is not None and "Group" in g.a["href"]:
            l = g.a["href"].split("&")
            all_groups.append(l[-1].split("=")[1])

    return sorted(all_groups)

try:
    groups = pull_groups(args.semester)
except gaierror as e:
    print(e)
    print("Error connecting to Lou's List")
    exit(1)

if not args.group:
    for g in groups:
        print(g)
    exit(0)

if args.group not in groups:
    print("Group was not found in list of valid groups")
    for g in groups:
        print(g)
    exit(0)

## Pull course list and data

params = {
    "Semester": args.semester,
    "Type": "Group",
    "Group": args.group # e.g. STS, CompSci
}

def get_section_info(s):
    if not s.td:
        return None
    a = s.td.select_one('a.Link')
    if not a:
        return None

    tds = s.find_all('td')

    return {
        "id": a.text,
        "num": tds[1].text,
        "status": tds[3].text,
        "occupancy": tds[4].a.text,
        "instructor": tds[5].find('span').text,
        "time": tds[6].text,
        "room": tds[7].text
    }

def pull():
    r = requests.get(page_url, params = params)
    soup = bs(r.content, 'html.parser')
    courses = soup.select('tr > td.CourseNum')
    courses_info = {}
    for c in courses:
        name = c.span.text

        sections = soup.select('tr.S.{}'.format(name.replace(" ", "")))

        parsed_sections = [ get_section_info(s) for s in sections ]
        parsed_sections = list(filter(None.__ne__, parsed_sections))

        courses_info[c.span.text] = { s["id"]: s for s in parsed_sections }

    return courses_info

info = pull()

def print_course(course):
    print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format('ID', 'Num', 'Status', 'Occ', 'Instr', 'Time', 'Room'))
    for id in course:
        s = course[id]
        print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format(
            s["id"], s["num"], s["status"], s["occupancy"], s["instructor"],
            s["time"], s["room"]
            ))

if not args.course:
    for cname in info:
        course = info[cname]
        print(" ******** {} ******** ".format(cname))
        print_course(course)
    exit(0)

if args.course not in info:
    print("Invalid course given")
    exit(1)

new_c = info[args.course]
print_course(new_c)

if not args.notify:
    exit(0)

def notify(ids):
    print("Notifying about changes in IDs", ids)

    # Start messenger notifier
    fbm_settings = {
        'email': getenv("MESSENGER_EMAIL"),
        'password': getenv("MESSENGER_PASSWORD")
    }
    fbm = MessengerNotifier(**fbm_settings)
    fbm.notify("{}: {}".format(args.course, ids))
    fbm.logout()

def check_occ_diff(c1, c2):
    if c1.keys() != c2.keys():
        print("!!! Sections have changed!")
        return list(c2.keys())

    ids = []
    for id in c1:
        if c1[id]["occupancy"] != c2[id]["occupancy"]:
            ids.append(id)
            s = c2[id]
            print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format(
                s["id"], s["num"], s["status"], s["occupancy"], s["instructor"],
                s["time"], s["room"]
                ))
    return ids

dotenv_path = join(dirname(__file__), 'conf.env')
if not exists(dotenv_path):
    print("No conf.env found... loading example")
    dotenv_path = join(dirname(__file__), 'conf.env.example')
load_dotenv(dotenv_path)

old_c = new_c

try:
    while True:
        sleep(10)
        info = pull()
        new_c = info[args.course]
        ids = check_occ_diff(old_c, new_c)
        if len(ids) > 0:
            notify(ids)

        old_c = new_c
except KeyboardInterrupt:
    pass

# vim: set expandtab:ts=4:sw=4
