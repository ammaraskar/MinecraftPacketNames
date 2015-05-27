import re
from bs4 import BeautifulSoup
import requests
import sys
import json
import collections


def main():
    versions_page = requests.get("http://wiki.vg/Protocol_version_numbers")
    versions_page = BeautifulSoup(versions_page.text)

    tables = versions_page.find_all("table", attrs="wikitable")
    
    post_netty = tables[0]
    pre_netty = tables[1]

    post_netty_links = []
    pre_netty_links = []

    packets = {"postNetty": collections.OrderedDict(), "preNetty": collections.OrderedDict()}
    
    for row in post_netty.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 3:
            continue
        # filter out rows where the link to the protocol page isn't there
        if not cells[2].a:
            continue

        version_number = cells[1].get_text().strip()
        link = cells[2].a.get('href')

        post_netty_links.append((link, version_number))

    
    for row in pre_netty.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 4:
            continue
        # filter out rows where the link to the protocol page isn't there
        if not cells[2].a:
            continue

        version_number = cells[1].get_text().strip()
        link = cells[2].a.get('href')

        pre_netty_links.append((link, version_number))
        


    for i, (link, version_number) in enumerate(post_netty_links):
        print("Scraping " + str(i + 1) + " of " + str(len(post_netty_links)) + " post netty pages")
        packets["postNetty"][version_number] = scrape_post_netty(link)

    for i, (link, version_number) in enumerate(pre_netty_links):
        print("Scraping " + str(i + 1) + " of " + str(len(pre_netty_links)) + " pre netty pages")
        packets["preNetty"][version_number] = scrape_pre_netty(link)

    with open('packets.json', 'w') as outfile:
        json.dump(packets, outfile, indent=4, sort_keys=True)


STATES = ['Handshaking', 'Play', 'Status', 'Login']
TABLE_PACKET_ID_REGEX = re.compile(' *\| *rowspan=[^ ]* *\| (?P<id>\dx\d*)', re.IGNORECASE)
def scrape_post_netty(link):
    protocol_page = requests.get(link + "&action=edit")
    protocol_page = BeautifulSoup(protocol_page.text)

    wiki_source = protocol_page.textarea.get_text()
    wiki_source = wiki_source.split("\n")

    packets = {}

    for state in STATES:
        try:
            state_index = wiki_source.index("== " + state + " ==")
        except ValueError:
            print("State " + state + " not found @ " + link)
            continue
        packets[state] = {"Serverbound": {}, "Clientbound": {}}

        direction = None
        packet_name = None
        for line in wiki_source[state_index+1:]:
            line = line.strip()

            # break upon encountering the next level 2 heading
            if line.startswith("== ") and line.endswith("=="):
                break

            if "===" in line and "Serverbound" in line:
                direction = "Serverbound"
                continue
            elif "===" in line and "Clientbound" in line:
                direction = "Clientbound"
                continue

            # assume a level 4 heading is a packet
            if line.startswith("====") and line.endswith("===="):
                if not direction:
                    print("Encountered a packet before acquiring a direction")
                    continue

                packet_name = line.replace("====", "").strip()

            regex_match = TABLE_PACKET_ID_REGEX.match(line)
            if regex_match:
                packet_id = int(regex_match.group('id'), 16)

                if not packet_name:
                    print("Encountered a packet id before its name")
                    continue

                packets[state][direction][packet_id] = packet_name
                packet_name = None

    return packets


PACKET_REGEX = re.compile('(?P<name>.*) \((?P<id>.*)\)')
def scrape_pre_netty(link):
    protocol_page = requests.get(link)
    protocol_page = BeautifulSoup(protocol_page.text)

    packets = {}

    for heading in protocol_page.find_all("li", {"class": "toclevel-1"}):
        if heading.a and heading.a.get('href') == "#Packets":
            for packet_heading in heading.ul.find_all("li"):
                packet_name = packet_heading.a.find_all("span", {"class": "toctext"})[0]

                if not packet_name:
                    print("scraping screw up @ " + link + ": " + packet_heading)
                    sys.exit(1)

                packet_name = packet_name.get_text().strip()
                regex = PACKET_REGEX.match(packet_name)
                if not regex:
                    continue

                packets[int(regex.group('id'), 16)] = regex.group('name')

    return packets

if __name__ == '__main__':
  main()