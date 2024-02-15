
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import concurrent.futures
import requests
import time
import random
import uuid

API_INDEX = 0

def fetch_and_update_proxies():
    global API_INDEX
    proxy_api_urls = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://proxyspace.pro/http.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
        "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://api.openproxylist.xyz/http.txt",
        "https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous"
    ]

    if API_INDEX >= len(proxy_api_urls):
        print("[!] All proxy APIs used. Restarting from the beginning.")
        API_INDEX = 0

    proxies = set()

    for api_url in proxy_api_urls[API_INDEX:]:
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                proxies.update(response.text.strip().split('\n'))
                break
        except requests.exceptions.RequestException as e:
            print(f"[!] Error fetching proxies from {api_url}: {e}")

    with open('proxies.txt', 'w') as file:
        file.write('\n'.join(proxies))

    print("[+] Proxies updated successfully.")

    API_INDEX += 1

def fetch_user_agents():
    user_agents_url = "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"
    try:
        response = requests.get(user_agents_url, timeout=10)
        if response.status_code == 200:
            return response.text.strip().split('\n')
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching user-agents: {e}")
    return []

def generate_random_device_id():
    return str(uuid.uuid4())

def send_request(proxy, user_agent, device_id, nglusername, message, total_count):
    headers = {
        'Host': 'ngl.link',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': user_agent,
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://ngl.link',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://ngl.link/{nglusername}',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    data = {
        'username': f'{nglusername}',
        'question': f'{message}',
        'deviceId': device_id,
        'gameSlug': '',
        'referrer': '',
    }

    success_count = 0
    fail_count = 0

    while success_count + fail_count < total_count:
        try:
            with requests.Session() as session:
                response = session.post('https://ngl.link/api/submit', headers=headers, data=data, proxies=proxy, timeout=10)
                if response.status_code == 200:
                    success_count += 1
                else:
                    fail_count += 1
            time.sleep(1)
        except requests.exceptions.RequestException:
            fail_count += 1

    return success_count, fail_count

def attack(update: Update, context: CallbackContext):
    fetch_and_update_proxies()

    nglusername = update.message.text.split()[1]
    message = update.message.text.split()[2]
    count = int(update.message.text.split()[3])

    with open('proxies.txt', 'r') as file:
        proxies_list = [line.strip() for line in file]

    user_agents = fetch_user_agents()

    value = 0
    success_count = 0
    fail_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _ in range(count):
            proxy = {'http': 'http://' + random.choice(proxies_list)}
            user_agent = random.choice(user_agents)
            device_id = generate_random_device_id()

            future = executor.submit(
                send_request, proxy, user_agent, device_id, nglusername, message, count
            )
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            success, fail = future.result()
            success_count += success
            fail_count += fail

    update.message.reply_text(f"Attack completed successfully.\nUsername: {nglusername} | Message: {message} | Count: {count}")

def main():
    updater = Updater("6883960019:AAEy-U_oxX3pkXap0BWwsLr-iL4v_vCVzKM")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("attack", attack))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    