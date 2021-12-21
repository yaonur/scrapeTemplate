import json
import os
import requests
import mimetypes
import requests.cookies
from requests_toolbelt import MultipartEncoder
from bs4 import BeautifulSoup
from bot.BookmarkManager import BookmarkManager
from bot.Registry import Registry
from bot.RequestBuilder import RequestBuilder
from requests.structures import CaseInsensitiveDict
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from time import sleep

AGENT_STRING = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
)

#  endpoints
HOME_PAGE = 'https://www.instagram.com/'
DELETE_USER_SESSION = ''
LOAD_DATA_URL=''
user_name='yaonur'
password='asgala32167321'
user_mail='ya_onur@hotmail.com'


class Bot:
    def __init__(
            self,
            password="",
            proxies=None,
            username="",
            email="",
            cred_root="cookies",
            user_agent=None,
    ):
        self.email = email
        self.username = username
        self.password = password
        self.req_builder = RequestBuilder()
        self.bookmark_manager = BookmarkManager()
        self.http = requests.session()
        self.proxies = proxies
        self.user_agent = user_agent


        self.registry = Registry(cred_root, email)

        cookies = self.registry.get_all()
        for key in cookies.keys():
            self.http.cookies.set(key, cookies[key])

        if self.user_agent is None:
            self.user_agent = AGENT_STRING

    def request(self, method, url, data=None, files=None, extra_headers=None):
        headers = CaseInsensitiveDict(
            [
                ("Referer", HOME_PAGE),
                ("X-Requested-With", "XMLHttpRequest"),
                ("Accept", "application/json"),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
            ]
        )
        csrftoken = self.http.cookies.get("csrftoken")
        if csrftoken:
            headers.update([("X-CSRFToken", csrftoken)])

        if extra_headers is not None:
            for h in extra_headers:
                headers.update([(h, extra_headers[h])])

        response = self.http.request(
            method, url, data=data, headers=headers, files=files, proxies=self.proxies
        )
        response.raise_for_status()

        return response

    def get(self, url):
        return self.request("GET", url=url)

    def post(self, url, data=None, files=None, headers=None):
        return self.request(
            "POST", url=url, data=data, files=files, extra_headers=headers
        )

    def login(self, headless=False, wait_time=15, proxy=None, lang="en"):
        """
        Logs user in with the provided credentials
        User session is stored in the 'cred_root' folder
        and reused so there is no need to login every time.
        Pinterest sessions lasts for about 15 days
        Ideally you need to call this method 3-4 times a month at most.
        :return python dict object describing the pinterest response
        """
        chrome_options = Options()
        chrome_options.add_argument("--lang=%s" % lang)
        if headless:
            chrome_options.add_argument("--headless")

        if proxy is not None:
            http_proxy = Proxy()
            http_proxy.proxy_type = ProxyType.MANUAL
            http_proxy.http_proxy = proxy
            http_proxy.socks_proxy = proxy
            http_proxy.ssl_proxy = proxy
            http_proxy.add_to_capabilities(chrome_options)

        driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(), options=chrome_options
        )
        driver.get(HOME_PAGE)
        sleep(1)

        try:
            cookies = driver.get_cookies()

            self.http.cookies.clear()
            for cookie in cookies:
                self.http.cookies.set(cookie["name"], cookie["value"])

            self.registry.update_all(self.http.cookies.get_dict())
        except Exception as e:
            print("Failed to login", e)

        print("Successfully logged in with account " + self.email)
        return driver
        # driver.close()

    def check_login_status(self):
        """
        checks login status
        :return: boolean describing the pinterest response
        """
        resp = self.get(url=HOME_PAGE)
        soup = BeautifulSoup(resp.text, 'html.parser')
        scripts = soup.findAll('script')
        for s in scripts:
            if 'id' in s.attrs and s.attrs['id'] == '__PWS_DATA__':
                pinJsonData = json.loads(s.contents[0])['isAuthenticated']
                return pinJsonData

        raise Exception(" data not found. ")

    def logout(self):
        """
        Logs current user out. Takes few seconds for the session to be invalidated on pinterest's side
        """
        options = {"disable_auth_failure_redirect": True}

        data = self.req_builder.buildPost(options=options)
        return self.post(url=DELETE_USER_SESSION, data=data)

    def load_data(self):
        """
        Loads full information about a pin
        :param pin_id: pin id to load
        :return: python dict describing the pinterest response
        """
        resp = self.get(url=LOAD_DATA_URL)
        soup = BeautifulSoup(resp.text, "html.parser")
        scripts = soup.findAll("script")
        raise Exception("data not found.")

bot =Bot(password=password,username=user_name,email=user_mail)
