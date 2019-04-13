#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as bs
import argparse
from sys import argv, exit
from socket import gaierror

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

try:
    groups = pull_groups(args.semester)
except gaierror as e:
    print(e)
    print("Error connecting to Lou's List")
    exit(1)

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

if not args.course:
    for cname in info:
        course = info[cname]
        print(" ******** {} ******** ".format(cname))
        print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format('ID', 'Num', 'Status', 'Occ', 'Instr', 'Time', 'Room'))
        for id in course:
            s = course[id]
            print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format(
                s["id"], s["num"], s["status"], s["occupancy"], s["instructor"],
                s["time"], s["room"]
                ))
else:
    if args.course not in info:
        print("Invalid course given")
        exit(1)

    c = info[args.course]
    print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format('ID', 'Num', 'Status', 'Occ', 'Instr', 'Time', 'Room'))
    for id in c:
        s = c[id]
        print("{:<8} {:<15} {:<20} {:<20} {:<20} {:<30} {:<10}".format(
            s["id"], s["num"], s["status"], s["occupancy"], s["instructor"],
            s["time"], s["room"]
            ))


# vim: set expandtab:ts=4:sw=4
