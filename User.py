# encoding=utf8
import time, requests, re, pickle, os, queue, urllib, threading, ThreadUtil
import io
from PIL import Image
from bs4 import BeautifulSoup
import Utils
import json

import pycookiecheat
import faker


class User(object):
    _xsrf = None
    answers = []

    def __init__(self, cookies: dict):
        session = self.session = requests.session()
        session.headers = Utils.BROWSER_HEADERS_DEFAULT
        session.headers[
            'User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        session.cookies = requests.utils.add_dict_to_cookiejar(
            session.cookies,
            cookies
        )

        # 从首页获得用户信息
        resp = session.get(Utils.URL_BASE)
        soup = BeautifulSoup(resp.text, 'lxml')

        _xsrf = soup.select_one('input[name=_xsrf]')
        self._xsrf = _xsrf['value'] if _xsrf else None
        if _xsrf:
            self.name, self.id, self.img_avatar, self.hash, self.desc, *spam = json.loads(
                soup.select_one('script[data-name=current_user]').text)
            self.time_created = json.loads(soup.select_one('script[data-name=ga_vars]').text)['user_created']

    def refresh_user_answers(self):
        resp = self.session.get(f"https://www.zhihu.com/people/{self.id}/answers")
        soup = BeautifulSoup(resp.text, 'lxml')
        self.answers = []

        for i in soup.select("#Profile-answers > div > div.List-item"):
            item = {}
            a = i.select_one('.ContentItem-title a')
            item['link'], item['title'] = a['href'], a.text
            # <meta itemprop="upvoteCount" content="1">
            item['upvote'] = i.select_one('meta[itemprop=upvoteCount]')['content']
            self.answers.append(item)

            r = self.session.get(url=f'{Utils.URL_PERSOINFO_API}{self.id}/answers')
            if r.status_code == 200:

                b = BeautifulSoup(r.content, 'lxml')

                user_name = b.find('span', {'class': 'ProfileHeader-name'})
                user_name = user_name.text if user_name else None

                user_headline = b.find('span', class_='RichText ProfileHeader-headline')
                user_headline = user_headline.text if user_headline else None

                user_company = b.find('svg', class_='Icon Icon--company')
                if user_company:
                    user_company = user_company.parent.parent.text
                else:
                    user_company = None

                user_education = b.find('svg', class_='Icon Icon--education')
                if user_education:
                    user_education = user_education.parent.parent.text
                else:
                    user_education = None

                user_follow = b.find_all('div', {'class': 'NumberBoard-value'})
                user_follower, user_followee = -1, -1
                if len(user_follow) == 2:
                    user_follower, user_followee = user_follow[0].text, user_follow[1].text

                user_otherinfo = b.find_all('span', {'class': 'Profile-lightItemValue'})
                takein_live, followe_topic, followe_zhuanlan, followe_question, followe_collection = 0, 0, 0, 0, 0
                if len(user_otherinfo) == 5:
                    takein_live = user_otherinfo[0].text
                    followe_topic = user_otherinfo[1].text
                    followe_zhuanlan = user_otherinfo[2].text
                    followe_question = user_otherinfo[3].text
                    followe_collection = user_otherinfo[4].text

                user_activity = b.find_all('span', {'class': 'Tabs-meta'})
                answer_num, share_num, question_num, collection_num = 0, 0, 0, 0
                if len(user_activity) == 4:
                    answer_num = user_activity[0].text
                    share_num = user_activity[1].text
                    question_num = user_activity[2].text
                    collection_num = user_activity[3].text

                re_votenumber = r'(?<=获得 )[0-9]{1,}(?= 次赞同)'
                re_thanknumber = r'(?<=获得 )[0-9]{1,}(?= 次感谢)'
                re_collectnumber = r'(?<=，)[0-9]{1,}(?= 次收藏)'
                re_includenumber = r'(?<=收录 )[0-9]{1,}(?= 个回答)'

                c = r.text
                f = lambda x: x.group() if x else 0
                votenumber = f(re.search(re_votenumber, c))
                thanknumber = f(re.search(re_thanknumber, c))
                collectnumber = f(re.search(re_collectnumber, c))
                includenumber = f(re.search(re_includenumber, c))

                print(user_name, user_headline, user_company, user_education, user_follower, user_followee,
                      takein_live, followe_topic, followe_zhuanlan, followe_question, followe_collection,
                      answer_num, share_num, question_num, collection_num, votenumber, thanknumber, collectnumber,
                      includenumber)

    def archieve_list(self, userid, ftype='followers', thread_number=10):
        self.url_queue = queue.Queue()
        self.html_queue = queue.Queue()
        self.init_followee_url(userid, ftype)
        self.url_queue.put(Utils.ENG_FLAG)

        for x in range(thread_number):
            thread = threading.Thread(target=ThreadUtil.thread_queue,
                                      args=(self.url_queue, self.html_queue, self.session,))
            thread.start()

        for x in range(thread_number):
            thread = threading.Thread(target=self.parser_followelist_page_thread, args=(ftype,))
            thread.start()

    def init_followee_url(self, userid, ftype):

        url = Utils.URL_MEMBER_API + '/' + userid + '/' + ftype
        ThreadUtil.init_thread(url, 20, self.url_queue, self.session)

    def parser_followelist_page_thread(self, ftype):
        while True:
            if not self.html_queue.empty():
                html_page = self.html_queue.get()
                if html_page == Utils.ENG_FLAG:
                    break

                if ftype == 'folowees' or ftype == 'followers':
                    html_page = html_page.json()
                    for x in html_page['data']:
                        answer_count = x['answer_count']
                        articles_count = x['articles_count']
                        gender = x['gender']
                        name = x['name']
                        url_token = x['url_token']
                        print(answer_count, articles_count, gender, name, url_token)
                    self.html_queue.task_done()

                elif ftype == 'following-columns':
                    html_page = html_page.json()
                    for x in html_page['data']:
                        title = x['title']
                        articles_count = x['articles_count']
                        followers = x['followers']
                        updated = x['updated']
                        column = x['id']
                        intro = x['intro']
                        print(title, articles_count, followers, updated, column, intro)

                elif ftype == 'following-questions' or ftype == 'questions':
                    html_page = html_page.json()
                    for x in html_page['data']:
                        title = x['title']
                        url = x['url']
                        updated_time = x['updated_time']
                        answer_count = x['answer_count']
                        follower_count = x['follower_count']
                        created = x['created']
                        print(title, url, updated_time, answer_count, follower_count, created)


class Users(object):
    Users = []

    def __init__(self, from_browser=True):
        if from_browser:
            try:
                u = User(cookies=pycookiecheat.chrome_cookies(Utils.URL_BASE))
                if u._xsrf:
                    self.Users.append(u)
                else:
                    print('没有从浏览器里读到有用数据')
            except:
                print('解析数据出错')

    def login(self, username, password):
        """通过账号密码的方式加入新的 user实例 以管理
        返回 True 则登陆成功
        """
        session = requests.session()
        session.headers = Utils.BROWSER_HEADERS_DEFAULT

        resp = session.get(Utils.URL_CAPTCHA)
        Image.open(io.BytesIO(resp.content)).show()  # 显示二维码
        catpcha = input('input captcha...')

        resp = session.post(Utils.URL_PHONE_LOGIN,
                            data={"phone_num": username, "password": password, "captcha": catpcha})
        j = resp.json()

        print(j['msg'])
        if not j['r']:
            u = User(cookies=requests.utils.dict_from_cookiejar(session.cookies))
            self.Users.append(u)
            return True
        else:
            pass
