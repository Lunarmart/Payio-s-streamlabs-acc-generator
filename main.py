from validate import validate
validate()
import re
import tls_client
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
from console import Console
from colorama import Fore
log = Console()
b = Fore.LIGHTBLACK_EX
r = Fore.RESET

class StreamlabsBot:
    def __init__(self, thread_count=100, tokens_file='tokens.txt', output_file='accs.txt', failed_file='failed_tokens.txt', max_retries=2):
        self.tkns = self.read_accounts(tokens_file)
        self.thread_count = min(thread_count, len(self.tkns))
        self.tokens_file = tokens_file
        self.output_file = output_file
        self.failed_file = failed_file
        self.max_retries = max_retries

    def read_accounts(self, filename):
        with open(filename, 'r') as f, [line.strip() for line in f.readlines()]:
            pass  # postinserted
    def save_result(self, twitter_token, slsid):
        with open(self.output_file, 'a') as f:
            f.write(f'{twitter_token}:{slsid}\n')
        log.Subscribed(f'Created Streamlabs Account : {b}token={r}{Fore.LIGHTBLUE_EX}{twitter_token}{r}, {b}slsid={r}', slsid[:20])

    def save_failed_token(self, twitter_token):
        with open(self.failed_file, 'a') as f:
            f.write(f'{twitter_token}\n')

    def login(self, twitter_token):
        retries = 0
        while retries < self.max_retries:
            try:
                session = tls_client.Session(client_identifier='chrome_131', random_tls_extension_order=True)
                response = session.get('https://streamlabs.com/slid/login')
                if response.status_code!= 200:
                    raise Exception('Failed to load Streamlabs login page.')
                xsrf_token = session.cookies.get('XSRF-TOKEN')
                if not xsrf_token:
                    raise Exception('XSRF token not found.')
                headers = {'accept': 'application/json, text/plain, */*', 'cache-control': 'no-cache', 'client-id': '419049641753968640', 'content-type': 'application/json', 'origin': 'https://streamlabs.com', 'referer': 'https://streamlabs.com/', 'x-xsrf-token': xsrf_token, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
                auth_response = session.get('https://streamlabs.com/api/v5/login/get-platform-url?platform=twitter&redirect=https%3A%2F%2Fstreamlabs.com%2Fdashboard')
                if auth_response.status_code!= 200:
                    raise Exception('Failed to retrieve Twitter login URL.')
                twitter_login_url = auth_response.text
                twitter_response = session.get(twitter_login_url, headers={'cookie': f'auth_token={twitter_token};'})
                if twitter_response.status_code!= 200:
                    raise Exception('Failed to access Twitter login page.')
                soup = BeautifulSoup(twitter_response.text, 'html.parser')
                authenticity_token = soup.find('input', {'name': 'authenticity_token'})
                if not authenticity_token:
                    raise Exception('Authenticity token not found.')
                auth_token_value = authenticity_token['value']
                oauth_token = re.search('oauth_token=([^&]+)', twitter_login_url)
                if not oauth_token:
                    raise Exception('OAuth token not found.')
                data = {'authenticity_token': auth_token_value, 'oauth_token': oauth_token.group(1)}
                auth_response = session.post('https://x.com/oauth/authorize', data=data, headers={'cookie': f'auth_token={twitter_token};'})
                if auth_response.status_code!= 200:
                    raise Exception('Failed to authorize Twitter login.')
                soup = BeautifulSoup(auth_response.text, 'html.parser')
                meta_tag = soup.find('meta', attrs={'http-equiv': 'refresh'})
                if not meta_tag:
                    raise Exception('No redirect meta tag found.')
                redirect_url = re.search('url=(.+)', meta_tag.get('content', ''))
                if not redirect_url:
                    raise Exception('No redirect URL found.')
                final_url = redirect_url.group(1).replace('amp;', '')
                Req1 = session.get(final_url)
                Req2 = session.get('https://streamlabs.com/dashboard')
                headers = Req2.headers
                for cookie in headers.get('Set-Cookie', []):
                    if (match := re.search('slsid=([^;]+)', cookie)):
                        slsid = match.group(1)
                        self.save_result(twitter_token, slsid)
                        return
            except Exception as e:
                else:  # inserted
                    raise Exception('SLSID not found in cookies.')
        else:  # inserted
            self.save_failed_token(twitter_token)
            retries += 1
            time.sleep(2)

    def run(self):
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            executor.map(self.login, self.tkns)
if __name__ == '__main__':
    bot = StreamlabsBot(thread_count=50)
    bot.run()
