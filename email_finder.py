#!/usr/bin/env python3
"""
email_finder.py - generate likely business email addresses for a person at a company
domain, and check that the domain can actually receive mail (MX lookup).

It does NOT scrape the web, probe mail servers (no SMTP RCPT tricks), or send anything.
Treat the output as candidates, not confirmed addresses. Use it for legit outreach
(sales, recruiting, press) and respect opt-outs and local anti-spam laws.

Usage:
    python email_finder.py --first Jane --last Doe --domain example.com
    python email_finder.py --file people.csv          # columns: first,last,domain
    python email_finder.py --first Jane --last Doe --domain example.com --json

Install:
    pip install dnspython
"""

import argparse
import csv
import json
import re
import sys
import unicodedata

EMAIL_RE = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$")

# Roughly ordered by how common each format is at companies.
PATTERNS = [
    "{first}.{last}",
    "{first}",
    "{f}{last}",
    "{first}{last}",
    "{first}_{last}",
    "{first}{l}",
    "{f}.{last}",
    "{last}.{first}",
    "{last}{f}",
    "{last}",
    "{f}{l}",
]


def clean(name):
    """Lowercase, strip accents and anything that isn't a-z."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", name.lower())


def candidates(first, last, domain):
    first, last = clean(first), clean(last)
    if not first or not last:
        raise ValueError("first and last name must contain letters")
    seen, out = set(), []
    for pat in PATTERNS:
        local = pat.format(first=first, last=last, f=first[0], l=last[0])
        addr = f"{local}@{domain}"
        if addr not in seen and EMAIL_RE.match(addr):
            seen.add(addr)
            out.append(addr)
    return out


def mx_hosts(domain):
    import dns.resolver  # imported here so --skip-mx works without dnspython
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        return sorted(str(r.exchange).rstrip(".") for r in answers)
    except Exception:
        return []


def process(first, last, domain, skip_mx=False):
    domain = domain.lower().strip()
    result = {"first": first, "last": last, "domain": domain, "candidates": candidates(first, last, domain)}
    if skip_mx:
        result["mx"] = None
        result["domain_accepts_mail"] = None
    else:
        hosts = mx_hosts(domain)
        result["mx"] = hosts
        result["domain_accepts_mail"] = bool(hosts)
    return result


def main():
    p = argparse.ArgumentParser(description="Generate likely email addresses and check the domain's MX.")
    p.add_argument("--first")
    p.add_argument("--last")
    p.add_argument("--domain")
    p.add_argument("--file", help="CSV with columns first,last,domain")
    p.add_argument("--json", action="store_true")
    p.add_argument("--skip-mx", action="store_true", help="don't do the DNS lookup")
    args = p.parse_args()

    people = []
    if args.file:
        with open(args.file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                people.append((row["first"], row["last"], row["domain"]))
    elif args.first and args.last and args.domain:
        people.append((args.first, args.last, args.domain))
    else:
        p.error("give --first, --last and --domain, or --file")

    results = []
    for first, last, domain in people:
        try:
            results.append(process(first, last, domain, args.skip_mx))
        except ValueError as e:
            print(f"skipping {first} {last}: {e}", file=sys.stderr)

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
        return

    for r in results:
        print(f"\n{r['first']} {r['last']} @ {r['domain']}")
        if r["domain_accepts_mail"] is False:
            print("  ! no MX records, this domain probably can't receive email")
        elif r["mx"]:
            print("  MX:", ", ".join(r["mx"]))
        for addr in r["candidates"]:
            print("  ", addr)


if __name__ == "__main__":
    main()
