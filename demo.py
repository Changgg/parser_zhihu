"""功能演示模块"""
from Users import Users


def demo_login_by_password():
    """通过账号密码尝试登陆"""
    u = Users(from_browser=False)  # 传参不尝试依靠浏览器cookies值登陆
    u.login(username=15390381933, password=123456789)


def demo_login_by_browser_cookies():
    """通过浏览器cookies值尝试登陆"""
    u = Users()  # 传参不尝试依靠浏览器cookies值登陆
    u = u.users[0]
    u.refresh_user_answers()

def demo_login_by_cookies_file():
    """通过上次成功登陆自动保存的cookies来登陆账户"""
    u = Users(from_browser=False).users[0]
    print(u)
    print()

if __name__ == '__main__':
    demo_login_by_cookies_file()
