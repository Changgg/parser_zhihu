# Passer-zhihu
用Python看知乎

入口模块 demo.py

## 注释
知乎会通过User-Agent判断用户的浏览器版本能否正常解析页面，不能完全使用随机User-Agent

## 修改内容
- [x] 全部代码遵守基本规范

- [ ] `Users.py`
    - [x] mac和linux下从chrome获取cookies并验证
    - [x] 账号密码登录逻辑中的验证码图片不写入磁盘
    - [x] User登陆成功后自动写cookies到文件
    - [x] Users类在init的时候加入路径判断，对路径下用户cookies进行载入操作
    - [ ] 罗列出用户所有订阅和被订阅人的数据
    - [ ] 罗列出用户所有回答
    - [ ] 通过获取到的账户创建时间值算账户年龄
- [ ] 多用户模式


