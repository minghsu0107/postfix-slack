#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import base64
import quopri
import random
from mail.qmonitor.store import PostqueueStore


def dumpmail(qid):
    """
    Dump mail content of specific queue id
    return type: list of section where each section is a tuple (header,content)
    header is a dict() where the most important one is 'Content-Type'
    if header['Content-Type'] == 'text/plain':
        content is plaintext (type:str)
    if header['Content-Type'] == 'text/html':
        content is html (type:str)
    if header['Content-Type'] == 'image/*':
        content is image binary (type:bytes)
        the * is usually the extention of the image
        it can be saved by:
            with open('filename','wb') as f:
                f.write(content)
    """

    # print('queue id:',cid)

    proc = subprocess.Popen(['postcat', '-bq', qid],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (outs, errs) = proc.communicate()
    encs = ['utf-8', 'big5']
    s = None
    for enc in encs:
        try:
            s = outs.decode(encoding=enc).split('\n')
            break
        except:
            s = None
    if s is None:
        s = outs.decode(encoding='utf-8', errors='replace')
    (parts, cur, flag) = ([], [], False)
    for i in range(len(s)):
        if i + 1 < len(s) and (s[i])[:2] == '--' and (len(s[i
                + 1].strip()) == 0 or (s[i + 1])[:7] == 'Content'):
            if flag:
                parts.append(cur)
            cur = []
            flag = False
            continue
        cur.append(s[i])
        if len(s[i].strip()) > 0:
            flag = True
    if flag:
        parts.append(cur)
    section = []
    for part in parts:
        (header, content) = ({}, [])
        prev = ''
        for i in range(len(part)):
            if len(part[i].strip()) == 0:
                content = part[i + 1:]
                break
            elif len(part[i]) > 7 and (part[i])[:7] == 'Content':
                pos = part[i].find(': ')
                prev = (part[i])[:pos]
                header[prev] = (part[i])[pos + 2:].strip()
            else:
                header[prev] += ' ' + part[i].strip()
        if 'Content-Type' in header:
            s = header['Content-Type'].split(';')
            header['Content-Type'] = s[0].strip()
            for i in range(1, len(s)):
                pos = s[i].find('=')
                header[(s[i])[:pos].strip()] = (s[i])[pos + 1:].strip()
        if 'Content-Type' not in header:
            header['Content-Type'] = 'text/plain'

    #    if 'charset' not in header:
    #        header['charset']='utf-8'

        if 'Content-Transfer-Encoding' in header:
            if header['Content-Transfer-Encoding'] == 'base64':
                content = ''.join(content).strip()
                if (header['Content-Type'])[:5] != 'image':
                    enc = ('utf-8' if 'charset'
                           not in header else header['charset'])
                    content = \
                        base64.b64decode(content.encode()).decode(encoding=enc,
                            errors='replace')
                else:
                    content = base64.b64decode(content.encode())
            elif header['Content-Transfer-Encoding'] \
                == 'quoted-printable':
                content = '\n'.join(content)
                enc = ('utf-8' if 'charset'
                       not in header else header['charset'])
                content = \
                    quopri.decodestring(content.encode()).decode(encoding=enc,
                        errors='replace')
            else:
                content = '\n'.join(content)
        else:
            content = '\n'.join(content)
        section.append((header, content))
    return section

def dump_rand_mail():
    """
    Randomly pick a mail in mail queue to dump
    if mail queue is empty, return None
    """

    tmp = PostqueueStore()
    tmp._load_from_postqueue(parse=True)
    if len(tmp.mails) == 0:
        print 'mail queue empty'
        return None
    qid = random.choice(tmp.mails).qid
    return dumpmail(qid)


def dump_mail_by_sender(sender, rand=False):
    """
    Dump a mail of a specific sender
    if rand==False it will dump the first mail of the sender
    otherwise it will randomly dump a mail of the sender
    if there is no mail of the sender, return None
    """

    tmp = PostqueueStore()
    tmp._load_from_postqueue(parse=True)
    if '@' not in sender and sender != 'MAILER-DAEMON':
        sender += '@csie.ntu.edu.tw'
    qida = []
    for mail in tmp.mails:
        if mail.sender == sender:
            qida.append(mail.qid)
    if len(qida) == 0:
        print sender + ' has no mail in queue'
        return None
    if rand:
        qid = random.choice(qida)
    else:
        qid = qida[0]
    return dumpmail(qid)


def list_sender():
    tmp = PostqueueStore()
    tmp._load_from_postqueue(parse=True)
    senders = set()
    for mail in tmp.mails:
        senders.add(mail.sender)
    return senders
