import time, requests, re, pickle, os, queue, urllib, threading, ThreadUtil
import io
from PIL import Image
from bs4 import BeautifulSoup
import Utils
import json

import pycookiecheat
import faker
import glob


class User(object):
    _xsrf = None
    answers = []

    def __init__(self, cookies: dict):
        session = self.session = requests.session()
        session.headers = Utils.BROWSER_HEADERS_DEFAULT
        session.headers[
            'User-Agent'] = Utils.BROWSER_HEADERS_USER_AGENTS_DEFAULT
        session.cookies = requests.utils.add_dict_to_cookiejar(
            session.cookies,
            cookies
        )

        # 从首页获得用户登陆状态和信息
        resp = session.get(Utils.URL_BASE)
        soup = BeautifulSoup(resp.text, 'lxml')

        _xsrf = soup.select_one('input[name=_xsrf]')
        self._xsrf = _xsrf['value'] if _xsrf else None
        if _xsrf:
            self._cookies_save()

            self.name, self.id, self.img_avatar, self.hash, self.desc, *spam = json.loads(
                soup.select_one('script[data-name=current_user]').text)
            self.time_created = json.loads(soup.select_one('script[data-name=ga_vars]').text)['user_created']

            """从用户界面获得更多信息"""
            resp = self.session.get(f"{Utils.URL_PREFIX_PEOPLE}{self.id}/activities")
            soup = BeautifulSoup(resp.text, 'lxml')

            company = soup.find('svg', class_='Icon Icon--company')
            if company:
                company = company.parent.parent.text
            else:
                company = ''
            self.company = company

            education = soup.find('svg', class_='Icon Icon--education')
            if education:
                education = education.parent.parent.text
            else:
                education = ''
            self.education = education

            # 侧边栏
            side = soup.select_one('div.Profile-sideColumn')
            card = side.select_one('div.Card')
            info = {}
            for match in re.finditer(r"([ 0-9]+)次([^获得,，参与]+)", card.text):
                info[match.group(2)] = int(match.group(1))

            self.count_approve = info['赞同']
            self.count_help = info['感谢']
            self.count_collect = info['收藏']
            self.count_public_edit = info['公共编辑']

            card = side.select_one('div.Card.FollowshipCard')
            self.count_following = int(card.select_one('a[href$=following] > div.NumberBoard-value').text)
            self.count_followers = int(card.select_one('a[href$=followers] > div.NumberBoard-value').text)

            info = {}
            for a in side.select('div.Profile-lightList > .Profile-lightItem'):
                info[a.select_one('.Profile-lightItemName').text.strip()] = \
                    int(a.select_one('.Profile-lightItemValue').text.strip())
            self.count_sponsor_live = info['赞助的 Live ⚡️']
            self.count_following_collections = info['关注的收藏夹']
            self.count_following_topics = info['关注的话题']
            self.count_following_questions = info['关注的问题']
            self.count_following_columns = info['关注的专栏']

            card = side.select_one('.Profile-footerOperations')
            self.view = int(re.match(r"个人主页被浏览([ 0-9]+)次", card.text).group(1))

    def __repr__(self):
        return f"""-----------------------------
欢迎 {self.name} 使用
-----------------------------
{self.desc}
-----------------------------
用户公司 {self.company}
-----------------------------
获得 {self.count_approve} 次赞同
获得 {self.count_help} 次感谢，{self.count_collect} 次收藏
参与 {self.count_public_edit} 次公共编辑
-----------------------------
专注了 {self.count_following} 个大神
拥有 {self.count_followers} 个小弟
-----------------------------
赞助了 {self.count_sponsor_live} 个live

关注的话题\t\t{self.count_following_topics}
关注的专栏\t\t{self.count_following_columns}
关注的问题\t\t{self.count_following_questions}
关注的收藏夹\t\t{self.count_following_collections}
-----------------------------
个人主页被浏览 {self.view} 次
-----------------------------"""

    def _cookies_save(self):
        path = f"{Utils.PATH_FILES}/{self._xsrf}.cookies"
        content = json.dumps(requests.utils.dict_from_cookiejar(self.session.cookies))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def answers(self):
        # TODO 获取用户答案
        pass

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
    users = []

    def __init__(self, from_browser=True):
        if from_browser:
            try:
                u = User(cookies=pycookiecheat.chrome_cookies(Utils.URL_BASE))
                if u._xsrf:
                    self.users.append(u)
                else:
                    print('没有从浏览器里读到有用数据')
            except:
                print('解析数据出错')

        # 从files目录下读取cookies
        for c in glob.iglob(f'{Utils.PATH_FILES}/[0-9a-z]*.cookies'):
            with open(c, encoding='utf-8') as f:
                c = json.load(f)
            u = User(cookies=c)
            if u._xsrf:
                self.users.append(u)

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
            self.users.append(u)
            return True
        else:
            pass
