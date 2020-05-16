# Mail Server Monitor with Slack APIs
A Postfix mail queue monitor integrated with slack commands.
## Usage
Generate a report for the current MX mail queue:
```
# slack command
/mxq
```
Generate a report for the current SMTP mail queue:
```
/smtpq
```
## Deployment
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
#### MRTG
First, have Nginx installed and configure the server (refer to `nginx/bot.conf`).

Next, start the Nginx server by executing the `nginx` binary:
```
nginx
```