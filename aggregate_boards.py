#!/usr/bin/env python3
import csv
import sys
import os
from pathlib import Path
home = str(Path.home())
#print(home)
#myPath = home + os.sep + '.druthers'
#print(myPath)
sys.path.append(home + os.sep + '.druthers')
import config
#import urllib.request as urlrequest
from urllib.request import Request, urlopen
import json
from urllib.parse import urlparse

def main():
    token = config.api_token
    tsv_file = 'boards.tsv'
    cache_dir = 'cache'
    #print(tsv_file)
    #print(token)
    #exit()
    titles_by_issue = {}
    alldata = []
    with open(tsv_file) as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")
        rows = [row for row in reader]
        for row in rows:
            #print(row)
            board = row['Board URL HTML']
            board_json = row['Board URL JSON']
            print(board_json)
            project_id = board_json.split('/')[4]
            print(project_id)
            print(board)
            hostname = row['Installation hostname']
            #if hostname == 'dataverse.harvard.edu':
            #    continue
            print(hostname)
            #if board:
            #    print(board)
            #    hostname = row['Installation hostname']
            #hostname_path = os.path.join(cache_dir, 'installations', hostname)
            #if not os.path.exists(hostname_path):
            #    os.makedirs(hostname_path)
            #org = board.split('/')[4]
            #foo_path = os.path.join(cache_dir, 'boards', org)
            #if not os.path.exists(foo_path):
            #    os.makedirs(foo_path)
            #org_url = 'https://api.github.com/orgs/' + org + '/projects'
            #print('fetching ' + org_url)
            boards_for_org_out  = '{}'
            #req = Request(org_url)
            #req.add_header('Accept', 'application/vnd.github.inertia-preview+json')
            #response = urlopen(req)
            #boards_for_org_out = get_remote_json(response)
            boards_for_org_filename  = 'boards.json'
            #with open(foo_path + os.sep + boards_for_org_filename, 'w') as outfile:
            #    json.dump(boards_for_org_out, outfile, indent=4)

            # curl -H 'Accept: application/vnd.github.inertia-preview+json' https://api.github.com/projects/2783568/columns
            # {
            #  "message": "Requires authentication",
            #  "message": "Must have admin rights to Repository.",
            #  "documentation_url": "https://developer.github.com/v3/projects/columns/#list-project-columns"
            #}
            columns_url = 'https://api.github.com/projects/' + project_id + '/columns'
            print('fetching ' + columns_url)
            columns_out = '{}'
            req = Request(columns_url)
            req.add_header('Accept', 'application/vnd.github.inertia-preview+json')
            req.add_header('Authorization', 'token ' + token)
            response = urlopen(req)
            columns_out = get_remote_json(response)
            columns = 'columns.json'
            #with open(hostname_path + os.sep + columns, 'w') as outfile:
            #    json.dump(columns_out, outfile, indent=4)
            for col in columns_out:
                cards_url = col['cards_url']
                column_name = col['name']
                print(cards_url)
                print('fetching ' + cards_url)
                req = Request(cards_url)
                req.add_header('Accept', 'application/vnd.github.inertia-preview+json')
                req.add_header('Authorization', 'token ' + token)
                response = urlopen(req)
                cards_out = get_remote_json(response)
                print( ' cards found in column ' + column_name)
                for card in cards_out:
                    mycard = {}
                    #print(json.dumps(card, indent=4))
                    #content_url = card['content_url']
                    card_url = card.get('url', None)
                    #print(card_url)
                    #datarow.append(card_url)
                    content_url = card.get('content_url', None)
                    #print(content_url)
                    issue_url = None
                    #datarow.append('issue42')
                    #break
                    archived = card['archived']
                    if content_url and not archived:
                        #print(content_url)
                        #print(content_url)
                        #print(content_url)
                        issue_org = content_url.split('/')[4]
                        issue_repo = content_url.split('/')[5]
                        issue_number = content_url.split('/')[7]
                        issue_url = 'https://github.com/' + issue_org + '/' + issue_repo + '/issues/' + issue_number
                    if issue_url:
                        datarow = []
                        datarow.append(issue_url)
                        datarow.append(hostname)
                        datarow.append(board)
                        datarow.append(column_name)
                        #title = None
                        title = titles_by_issue.get(issue_url, None)
                        issue_state = ''
                        #if titles_by_issue[issue_url]:
                        #    title = titles_by_issue[issue_url]
                        if not title:
                            #api_issue_url = GET /repos/:owner/:repo/issues/:issue_number
                            api_issue_url = 'https://api.github.com/repos/' + issue_org + '/' + issue_repo + '/issues/' + issue_number
                            print('fetching ' + api_issue_url)
                            req = Request(api_issue_url)
                            #req.add_header('Accept', 'application/vnd.github.inertia-preview+json')
                            req.add_header('Authorization', 'token ' + token)
                            response = urlopen(req)
                            issue_out = get_remote_json(response)
                            print(json.dumps(issue_out, indent=4))
                            titles_by_issue[issue_url] = issue_out['title']
                            title = titles_by_issue[issue_url]
                            #     "state": "closed",
                            issue_state = issue_out['state']
                        datarow.append(title)
                        if not issue_state == 'closed':
                            alldata.append(datarow)
            #break
            #cards_out = '[]'
            #cards = 'cards.json'
            #with open(path + os.sep + cards, 'w') as outfile:
            #    json.dump(cards_out, outfile, indent=4)
            ## FIXME: remove this break

    #print(json.dumps(alldata, indent=4))
    #outfile = open('votes.tsv','w')
    outfile = open('issues.tsv','w')
    writer=csv.writer(outfile, delimiter='\t')
    #writer.writerow(['SNo', 'States', 'Dist', 'Population'])
    #writer.writerow(['filename', 'dataset_name', 'dataverse_level_1_alias', 'dataverse_level_1_friendly', 'dataverse_level_2_alias', 'dataverse_level_2_friendly', 'dataverse_level_3_alias', 'dataverse_level_3_friendly', 'subjects', 'publication_date'])
    writer.writerow(['Issue URL', 'Installation hostname', 'Board URL', 'Board Column', 'Issue title'])
    #writer.writerows(list_of_rows)
    alldata.sort(key=lambda x: x[0])
    writer.writerows(alldata)

def get_remote_json(response):
    return json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))

if __name__ == '__main__':
    main()
