#!/usr/bin/env python3
"""
Generate test users and create them via the app's /signup endpoint.

Usage examples:
  python scripts/create_users.py --count 10
  BASE_URL=http://localhost:5000 python scripts/create_users.py --count 50 --domain example.com

This script uses `requests`. If you don't have it installed, run:
  pip install requests
"""

import argparse
import os
import random
import string
import sys
from typing import Dict


def random_password(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def create_user(base_url: str, email: str, username: str, password: str, session) -> Dict:
    """POST to /signup with form-encoded data. Returns dict with result info."""
    url = base_url.rstrip('/') + '/signup'
    payload = {
        'email': email,
        'username': username,
        'password': password,
    }
    try:
        resp = session.post(url, data=payload, timeout=10)
    except Exception as e:
        return {'ok': False, 'error': f'network error: {e}'}

    # If the server responds with a redirect to login (302 -> followed to GET /login),
    # requests will by default follow. We'll treat any 200 as "request completed" and
    # inspect the body for common signs of failure.
    text = resp.text or ''
    if 'Email address already exists' in text or 'already exists' in text:
        return {'ok': False, 'error': 'email exists', 'status_code': resp.status_code}
    if resp.status_code >= 400:
        return {'ok': False, 'error': f'status {resp.status_code}', 'status_code': resp.status_code}

    return {'ok': True, 'status_code': resp.status_code}


def main():
    parser = argparse.ArgumentParser(description='Generate users and create them via HTTP POST to /signup')
    parser.add_argument('--count', '-n', type=int, default=10, help='Number of users to create')
    parser.add_argument('--base-url', '-b', default=os.environ.get('BASE_URL', 'http://localhost:5000'), help='Base URL of the running app')
    parser.add_argument('--domain', '-d', default='example.com', help='Email domain to use for generated users')
    parser.add_argument('--start', type=int, default=1, help='Start index for generated usernames/emails')
    parser.add_argument('--password-length', type=int, default=12, help='Length of generated passwords')
    parser.add_argument('--dry-run', action='store_true', help="Don't actually POST, just print what would be sent")
    args = parser.parse_args()

    # Check for requests
    try:
        import requests
    except Exception:
        print('This script requires the `requests` library. Install it with: pip install requests', file=sys.stderr)
        sys.exit(2)

    session = requests.Session()

    created = 0
    skipped = 0
    errors = 0

    for i in range(args.start, args.start + args.count):
        username = f'user{i}'
        email = f'user{i}@{args.domain}'
        password = random_password(args.password_length)

        if args.dry_run:
            print(f'[dry-run] POST {args.base_url.rstrip("/")}/signup -> email={email} username={username} password={password}')
            continue

        res = create_user(args.base_url, email, username, password, session)
        if res.get('ok'):
            created += 1
            print(f'[ok] created {email}')
        else:
            err = res.get('error')
            if err == 'email exists':
                skipped += 1
                print(f'[skip] {email} already exists')
            else:
                errors += 1
                print(f'[err] {email} -> {err}')

    print('\nSummary:')
    if not args.dry_run:
        print(f'  created: {created}')
        print(f'  skipped (already exists): {skipped}')
        print(f'  errors: {errors}')
    else:
        print('  dry-run only; no requests sent')


if __name__ == '__main__':
    main()
