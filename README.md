# email-finder

Generates likely business email addresses for a person at a company domain and checks that the domain can receive mail (MX lookup).

It does **not** scrape the web, probe mail servers, or send anything. Output is a list of candidates, not confirmed addresses.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python email_finder.py --first Jane --last Doe --domain example.com
python email_finder.py --file people.csv      # columns: first,last,domain
python email_finder.py --first Jane --last Doe --domain example.com --json
python email_finder.py --first Jane --last Doe --domain example.com --skip-mx
```

## Use responsibly

Use for legitimate outreach (sales, recruiting, press). Respect opt-outs and local anti-spam laws.

Built by [NANTHEDU](https://nanthedu.dpdns.org).
