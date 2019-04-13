#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as bs
import argparse
from sys import argv, exit

lous_list = "https://rabi.phys.virginia.edu/mySIS/CS2"
list_url =  "{}/{}".format(lous_list, "index.php")
page_url =  "{}/{}".format(lous_list, "page.php")

parser = argparse.ArgumentParser(description="CLI and notifier for Lou's list")
parser.add_argument('-g', '--group')
parser.add_argument('-c', '--course')
parser.add_argument('-s', '--semester', default=1198)
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

groups = pull_groups(args.semester)

if not args.group:
    print(groups)
    exit(0)

if args.group not in groups:
    print("Group was not found in list of valid groups")
    print(groups)
    exit(0)

## Pull course list and data

params = {
    "Semester": args.semester,
    "Type": "Group",
    "Group": args.group # e.g. STS, CompSci
}

def get_section_info(s):
    ret = {}
    if not s.td:
        return None
    a = s.td.select_one('a.Link')
    if not a:
        return None

    print("Found ", a.text)

    ret["id"] = a.text

def pull():
    r = requests.get(page_url, params = params)
    soup = bs(r.content, 'html.parser')
    courses = soup.select('tr > td.CourseNum')
    courses_info = {}
    for c in courses:
        name = c.span.text
        print(name)

        sections = soup.select('tr.S.{}'.format(name.replace(" ", "")))

        parsed_sections = [ get_section_info(s) for s in sections ]

        courses_info[c.span.text] = { }

pull()


# vim: set expandtab:ts=4:sw=4
