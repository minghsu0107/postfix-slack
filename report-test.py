#! /usr/bin/python3

from argparse import ArgumentParser
from collections import Counter
import subprocess as sp
from datetime import datetime
from slack import WebClient
import os
from mail.qmonitor import store
from mail.send import getStatus,serialize
import dotenv
TOTAL = '''
*Total mails in queue*: `{total_mails}`
*Total queue size*: `{total_mails_size:.3}` MB
'''
MAILS = '''
*Mails by accepted date*
last 24h: `{mails_by_age[last_24h]}`
1 to 4 days ago: `{mails_by_age[1_to_4_days_ago]}`
older than 4 days: `{mails_by_age[older_than_4_days]}`

*Mails by status*
Active: `{active_mails}`
Hold: `{hold_mails}`
Deferred: `{deferred_mails}`

*Mails by size*
Average size: `{average_mail_size:.3f}` KB
Maximum size: `{max_mail_size:.3f}` KB
Minimum size: `{min_mail_size:.3f}` KB
'''
UNIQUE = '''
*Unique senders*
Senders: `{unique_senders}`
Domains: `{u_s_domains}`

*Unique recipients*
Recipients: `{unique_recipients}`
Domains: `{u_r_domains}`
'''

TOP_s = '''
*Top senders*
{top_senders}
'''
TOP_sd = '''
*Top sender domains*
{top_sender_domains}
'''
TOP_r = '''
*Top recipients*
{top_recipients}
'''
TOP_rd = '''
*Top recipient domains*
{top_recipient_domains}

'''
def parseArguments():
    parser = ArgumentParser(description = 'Report mailq status to slack')
    parser.add_argument('--channel-name',
                        dest = 'channelName',
                        type = str,
                        required = True,
                        help = 'token file for slack bot')
    parser.add_argument('-w', '--whitelist',
                        dest = 'whitelist',
                        default = None,
                        help = 'a file containing whitelist senders')
    parser.add_argument('--report',
                        dest = 'report',
                        action = 'store_const',
                        const = True,
                        default = False,
                        help = 'determine whether to report if no spam')
    return parser.parse_args()

def getSenderStatus(status, whitelist = []):
    senders = status['top_senders']
    senders = [s for s in senders if s[0] not in whitelist]
    return senders

def show(token, channel, report = False, whitelist = []):
    client = WebClient(token = token)
    currentTime = datetime.now().isoformat(' ', timespec = 'seconds')
    status = getStatus()
    senders = getSenderStatus(status, whitelist = whitelist)
    print(senders)
    suspects = [s for s in senders if s[1] >= 80]
    suspects.sort()
    numMails = status['total_mails']
    status = serialize(status)
    if report is True or numMails >= 320 or len(suspects) > 0:
        header = 'Warning' if numMails >= 320 or len(suspects) > 0 else 'Report'
        ret = client.chat_postMessage(
            channel = channel,
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":envelope: *SMTP report-test* :star2::star2:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": TOTAL.format(**status)
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": MAILS.format(**status)
                        },
                        {
                            "type": "mrkdwn",
                            "text": UNIQUE.format(**status)
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": TOP_s.format(**status)
                        },
                        {
                            "type": "mrkdwn",
                            "text": TOP_sd.format(**status)
                        },
                        {
                            "type": "mrkdwn",
                            "text": TOP_r.format(**status)
                        },
                        {
                            "type": "mrkdwn",
                            "text": TOP_rd.format(**status)
                        }
                    ]
                }
            ]
        )

def main():
    args = parseArguments()
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    dotenv.load_dotenv(dotenv_path)
    slack_api_token = os.environ['SLACK_API_TOKEN']
    
    whitelist = []
    if args.whitelist is not None:
        with open(args.whitelist, 'r') as f:
            whitelist = [l.strip() for l in f.readlines()]

    show(slack_api_token, args.channelName, report = args.report, whitelist = whitelist)

if __name__ == '__main__':
    main()

