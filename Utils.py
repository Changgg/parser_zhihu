import time
import os
import faker

Default_Headers = {
    'User-Agent': faker.Faker().chrome(),
    'Host': 'www.zhihu.com'
}
COOKIE = ''
PATH_FILES = os.path.join(os.path.dirname(__file__),'files')

BASE_URL = 'https://www.zhihu.com'
ZHUANLAN_URL = 'https://zhuanlan.zhihu.com'

PHONE_LOGIN = BASE_URL + '/login/phone_num'
CAPTCHA_URL = BASE_URL + '/captcha.gif?r=' + str(int(time.time()) * 1000) + '&type=login'

QUESTION_API = BASE_URL + '/api/v4/questions'
ANSWER_API = BASE_URL + '/api/v4/answers'

PERSOINFO_API = BASE_URL + '/people/'
MEMBER_API = BASE_URL + '/api/v4/members'

TOPIC_API = BASE_URL + '/topic/'

ZHUANLAN_ARTICLE = ZHUANLAN_URL + '/api/columns'

ENG_FLAG = 'End'
