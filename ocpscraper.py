""" Extract user information from a profile on http://www.oc.tc.


    Most information in and OCN profile is in the general form

    <h2>Value
        <small>Name</small>
    </h2>

    Extracting text from such a BeautifulSoup Tag object produces something like

    '\nValue\nName\n'

    which is then used to build the profile dictionary.


    This script is written in a more verbose (and less pythonic) manner, simply
    to provide an easier update process when the profile html (inevtiably) changes.

"""

import urllib2
import contextlib

from bs4 import BeautifulSoup


BASE_URL = 'http://www.oc.tc/'

def get_player_info(username):
    profile = {'username': username}

    def extract_stats(stat_list, prefix=""):
        """ This function takes a list of '\nValue\nName\n' strings and returns a dictionary of name, value pairs.

            `prefix` allows distinguishing between specific stats, e.g. project_ares_kd and blitz_kd.
        """
        for stat in stat_list:
            data = stat.strip().split('\n')
            value = data[0]
            name = prefix + data[1].replace(' ', '_')
            profile[name] = value


    url = BASE_URL + username

    try:
        with contextlib.closing(urllib2.urlopen(url)) as response:
            html = response.read()
    except urllib2.HTTPError:
        print "HTTPError: User %s not found." % username
        return {}

    soup = BeautifulSoup(html)

    # make sure account is not suspended
    if soup.find('div', {'class': 'alert-error'}):
        print "Account suspended for %s." % username
        return {}

    sections = soup.find_all('section')
    top_section = sections[0]

    # badges
    badges = top_section.find_all("span",{"class":"label"})
    profile['badges'] = map(lambda x: x.text.strip(), badges)

    # kills
    for div in top_section.find_all('div',{'class':'span5'}):
        extract_stats([div.find('h2').text])

    # deaths
    for div in top_section.find_all('div',{'class':'span4'}):
        extract_stats([div.find('h2').text])

    # friends
    friends_section = top_section.find('div', {'class': 'span2'}).find_next('h2')
    extract_stats([friends_section.text])

    # right pane stats
    right_column = top_section.find('div', {'class':'span3'})
    extract_stats(map(lambda x: x.text, right_column.select('h2')))

    # stats pane section
    stats_pane = soup.find('div', {'id':'stats'})
    for section_title in stats_pane.find_all('h4'):
        stats = section_title.find_next('div').select('h3')

        title_text = section_title.text.strip().lower()
        prefix = ''
        if 'forum' not in title_text:
            prefix = title_text.replace(' ','_').replace('stats', '')

        extract_stats(map(lambda x: x.text, stats), prefix=prefix)

    # objectives
    objectives_pane = soup.find('div', {'id':'objectives'})
    for objective in objectives_pane.find_all('div', {'class':'span4'}):
        extract_stats([objective.find('h2').text])

    return profile


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Get user information from oc.tc.')
    parser.add_argument('username', type=str, help="a player's username")

    args = parser.parse_args()

    print get_player_info(args.username)
