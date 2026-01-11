#!/usr/bin/env python3
import argparse

import requests
import jwt
import time

# ================= CONFIG =================
API_VERSION = "v5.0"
# =========================================


def generate_token(key_id: str, secrect: str):
    return jwt.encode(
        {
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
            "aud": "/admin/"
        },
        bytes.fromhex(secret),
        algorithm="HS256",
        headers={"kid": key_id}
    )

def get_posts(url: str, key_id: str, secret: str, tag: str, page: int=1):
    token = generate_token(key_id, secret)
    url = f"{url}/ghost/api/admin/posts/"
    params = {
        "limit": 100,
        "page": page,
        "filter": f"tag:{tag}",
        "fields": "id,title"
    }

    r = requests.get(url, params=params, headers={
        "Authorization": f"Ghost {token}"
    })
    r.raise_for_status()
    return r.json()["posts"]

def delete_post(url: str, key_id: str, secret: str, post_id: str):
    token = generate_token(key_id, secret)
    url = f"{url}/ghost/api/admin/posts/{post_id}/"
    r = requests.delete(url, headers={
        "Authorization": f"Ghost {token}"
    })
    r.raise_for_status()

# ================= RUN =================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert TYPO3 export JSON to Ghost import JSON"
    )
    parser.add_argument('-u','--url',
                        default=0,
                        type=str,
                        required=True,
                        help="API URL"
                        )

    parser.add_argument('-k', '--key',
                        type=str,
                        required=True,
                        help="API Key"
                        )

    parser.add_argument('-t', '--tag',
                        type=str,
                        required=True,
                        help="Tag"
                        )

    args = parser.parse_args()

    key_id, secret = args.key.split(":")
    page = 1
    deleted = 0

    while True:
        posts = get_posts(args.url, key_id, secret,args.tag, page)

        if not posts:
            break

        for post in posts:
            print(f"Deleting: {post['title']}")
            delete_post(args.url, key_id, secret, post["id"])
            deleted += 1

        page += 1

    print(f"\nDONE — Deleted {deleted} posts with tag '{args.tag}'")

