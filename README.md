# Postfix Slack
A Postfix mail queue monitor integrated with slack commands.
## Usage
Generate a report for the current MX mail queue:
```
# slack command
/mxq
```
Generate a report for the current SMTP mail queue:
```
# slack command
/smtpq
```
Gernerate a report form MX or smtp server and send it to slack
(Routine check and report are set in crontab)
```
# execute on smtp
python report-test.py --channel-name slackbot-test --whitelist /root/smtp-bot/whitelist --report
```
Dump the content of a certain mail. It returns a list of `(header, content)`.
```python
from dumpmail import *
dumpmail(qid) # dump a mail by the given qid
dump_rand_mail() # dump a mail randomly
dump_mail_by_sender(sender,rand) # dump the first mail from a given sender, if rand == True then choose a mail randomly
```

## Deployment (directly on mail servers)
#### Slack App Configuration
Alias command `/mxq` to `http://<mx-public-ip:port>/mailq`; `/smtpq` to `http://<smtp-public-ip:port>/mailq`.
#### MX and SMTP
Install dependencies:
```bash
pip3 install -r requirements.txt
``` 
Change permissions for shell scripts:
```bash
chmod 700 run.sh stop.sh
```
Start the server:
```bash
./run.sh
```
Stop the server:
```bash
./stop.sh
```
## Deployment (with reverse Proxy)
#### Slack App Configuration
Alias command `/mxq` to `http://<proxy-ip:port>/mx/mailq`; `/smtpq` to `http://<proxy-ip:port>/smtp/mailq`.
#### MX and SMTP
Install dependencies:
```bash
pip3 install -r requirements.txt
``` 
Change permissions for shell scripts:
```bash
chmod 700 run.sh stop.sh
```
Start the server:
```bash
./run.sh
```
Stop the server:
```bash
./stop.sh
```
#### Reverse Proxy
First, have Nginx installed and configure the server (refer to `nginx/bot.conf`). Remember to replace all placeholders with your own configurations.

Next, start the Nginx server by executing the `nginx` binary:
```
nginx
```
Stop the server:
```
nginx -s quit
```
## Notes
If there is `502 Bad Gateway` error while fowarding the request, it is possible that port 80 on the mail server is blocked by the firewall. Thus, you can run the following command to accept connections on port 80:
```bash
iptables -I INPUT -p tcp --dport 80 -j ACCEPT
```
Or if you use `firewalld`:
```bash
firewall-cmd --permanent --zone=public --add-port=80/tcp 
firewall-cmd --reload
```
