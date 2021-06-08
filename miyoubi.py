import requests
import json
import logging
import re
import random
import configparser
import hashlib
import uuid
import time
import string

from wechat import senddata


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')


class ConfMeta(type):
  @property
  def index_url(self):
    return 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html'

  @property
  def app_version(self):
    return '2.3.0'

  @property
  def ua(self):
    return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) ' \
           'AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/%s' % (self.app_version)


class Conf(metaclass=ConfMeta):
  pass


class Miyoubi(object):
    def __init__(self, cookie: str = None):

        if not isinstance(cookie, str):
            raise TypeError("%s want a %s but got %s" % (
                self.__class__, type(__name__), type(cookie)))

        self._cookie = cookie

        '''
        login_ticket = re.findall(r'login_ticket=(.*?);', cookie)[0]

        url1 = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket=' + login_ticket
        res = requests.get(url1)
        res_text = res.text
        json1 = json.loads(res_text)
        print(json1)
        datalist_in = json1.get('data')
        if datalist_in['msg'] == "成功":
            # print('%s' % datalist_in['cookie_info']['cookie_token'])
            url2 = 'https://api-takumi.mihoyo.com/apihub/api/querySignInStatus?gids=1'
            datalist_out = {'cookie_token': 0, 'account_id': 0}
            datalist_out['cookie_token'] = datalist_in['cookie_info']['cookie_token']
            datalist_out['account_id'] = str(
                datalist_in['cookie_info']['account_id'])
            # print(datalist_out)
            res2 = requests.get(url2, cookies=datalist_out)
            # print(res2.cookies)
            url3 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket=' + \
                login_ticket + '&token_types=3&uid=' + str(datalist_in['cookie_info']['account_id'])
            res3 = requests.get(url3)
            res3_text = res3.text
            json2 = json.loads(res3_text)
            # print(json2)
            # print('-' * 70)
            # 构造cookie
            self.cookies_users = {}
            self.cookies_users['stuid'] = res2.cookies['ltuid']
            self.cookies_users['stoken'] = json2['data']['list'][0]['token']
            self.cookies_users['login_ticket'] = login_ticket

            url4 = 'https://api-takumi.mihoyo.com/apihub/api/querySignInStatus?gids=1'
            res = requests.get(url4, cookies=self.cookies_users)
            res_text = json.loads(res.text)
            # print(res_text)
            if res_text['message'] != 'OK':
                raise RuntimeError("检测用户信息失败，登录信息已失效.")
        else:
            # print('%s' % datalist_in['msg'])
            raise RuntimeError("登录信息已失效.")
        '''

    # Provided by Steesha
    def md5(self, text):
        md5 = hashlib.md5()
        md5.update(text.encode())
        return (md5.hexdigest())

    def get_DS(self):
        # n = self.md5(Conf.app_version)
        n = "h8w582wxwgqvahcdkpvdhbh2w9casgfl"
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = self.md5("salt=" + n + "&t=" + i + "&r=" + r)
        return i + "," + r + "," + c

    def get_header(self, ref):
        actid = 'e202009291139501'
        if not ref:
            ref = "%s?bbs_auth_required=%s&act_id=%s&utm_source=%s" \
                  "&utm_medium=%s&utm_campaign=%s" % (
                      Conf.index_url, 'true', actid, 'bbs', 'mys', 'icon')

        return {
            'x-rpc-device_id': str(uuid.uuid3(
                uuid.NAMESPACE_URL, self._cookie)).replace('-', '').upper(),
            'x-rpc-client_type': '5',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': Conf.ua,
            'Referer': ref,
            'x-rpc-app_version': Conf.app_version,
            'DS': self.get_DS(),
            'Cookie': self._cookie
        }

    def send_data(self):
        '''
        # 签到
        URL_signin = 'https://api-takumi.mihoyo.com/apihub/api/signIn'
        data = {
            'gids': '2'
        }
        try:
            jstr = requests.Session().post(
                URL_signin,
                headers=self.get_header('https://bbs.mihoyo.com/ys/'),
                data=json.dumps(data, ensure_ascii=False)).text
            jdict = json.loads(jstr)
            code = jdict['retcode']
        except Exception as e:
            raise e

        result = makeResult('Failed', jstr)
        if code in [0, 1008]:
            result = makeResult('Success', jstr)
            logging.info(result)
            if code == 1008:
                senddata(touser, "米游社重复签到或签到失败", result)
        else:
            logging.info(result)
            senddata(touser, "米游社签到失败", result)

        seconds = random.randint(1, 5)
        logging.info('Sleep for %s seconds ...' % (seconds))
        # time.sleep(seconds)
        '''

        # 原神板块
        # 获取贴子列表
        URL = 'https://api-takumi.mihoyo.com/post/api/getForumPostList?forum_id=26&is_good=false&is_hot=false&page_size=20&sort_type=1'
        # forum_id 1为崩3 26为原神 30为崩2
        try:
            res = requests.Session().get(URL, headers=self.get_header('https://bbs.mihoyo.com/ys/'))
            res_text = json.loads(res.text)
            post_list = res_text['data']['list']
            post_id_list = []
            for post in post_list:
                post_id_list.append(post['post']['post_id'])
        except Exception as e:
            raise e

        seconds = random.randint(1, 3)
        time.sleep(seconds)

        # 贴子操作
        detail_url = "https://api-takumi.mihoyo.com/post/api/getPostFull?post_id={}"
        vote_url = "https://api-takumi.mihoyo.com/apihub/sapi/upvotePost"
        for i in range(1):
            post_id = post_id_list.pop()
            ref = 'https://bbs.mihoyo.com/ys/article/' + post_id
            # 查看
            try:
                res = requests.Session().get(detail_url.format(post_id), headers=self.get_header('https://bbs.mihoyo.com/ys/'))
                print(res.text)
            except Exception as e:
                raise e
            # 点赞
            data = {
                'gids': '1',
                "post_id": str(post_id),
                "is_cancel": False
            }
            try:
                res = requests.Session().post(
                    vote_url,
                    headers=self.get_header(ref),
                    data=json.dumps(data, ensure_ascii=False))
                print(res.text)
            except Exception as e:
                raise e

            seconds = random.randint(1, 3)
            time.sleep(seconds)


def makeResult(result: str, data=None):
    return json.dumps(
        {
            'result': result,
            'message': data
        },
        sort_keys=False, indent=2, ensure_ascii=False
    )


if __name__ == "__main__":

    config = configparser.RawConfigParser()
    config.read('etc/config.ini')
    for section in config.sections():
        seconds = random.randint(10, 300)
        logging.info('Sleep for %s seconds ...' % (seconds))
        # time.sleep(seconds)

        touser = config[section]['Touser']
        cookie = config[section]['Cookie']

        myb_obj = Miyoubi(cookie)
        myb_obj.send_data()
