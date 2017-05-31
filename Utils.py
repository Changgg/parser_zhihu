import time
import os
import faker
import requests

BROWSER_HEADERS_DEFAULT = requests.structures.CaseInsensitiveDict(
    {
        'User-Agent': faker.Faker().chrome(),
        'Accept-Encoding': ', '.join(('gzip', 'deflate')),
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com'
    }
)

PATH_FILES = os.path.join(os.path.dirname(__file__), 'files')

URL_BASE = 'https://www.zhihu.com'
URL_ZHUANLAN = 'https://zhuanlan.zhihu.com'

URL_PHONE_LOGIN = f'{URL_BASE}/login/phone_num'
URL_CAPTCHA = f'{URL_BASE}/captcha.gif?r={str(int(time.time()) * 1000)}&type=login'

URL_QUESTION_API = f'{URL_BASE}/api/v4/questions'
URL_ANSWER_API = f'{URL_BASE}/api/v4/answers'

URL_PERSOINFO_API = f'{URL_BASE}/people/'
URL_MEMBER_API = f'{URL_BASE}/api/v4/members'

URL_TOPIC_API = f'{URL_BASE}/topic/'

URL_ZHUANLAN_ARTICLE = f'{URL_ZHUANLAN}/api/columns'

ENG_FLAG = 'End'
