'''
pixiv downloader by Foair
主页：https://foair.com/
TODO：填补登录认证和输入验证等逻辑、下载画集和动图、更多爬取的内容、加入异常处理提升稳定性……
TODO：指定文件夹下载、使用多线程处理、导出链接以便使用迅雷下载、简化代码提升效率……
'''
import re
import requests
from bs4 import BeautifulSoup

print('1. 下载「综合今日排行榜」')
print('2. 下载「综合本周排行榜」')
print('3. 下载「综合本月排行榜」')
print('4. 下载「原创作品排行榜」')
print('5. 下载「受男性欢迎排行榜」')
print('6. 下载「插画今日排行榜」')
print('7. 下载「插画本周排行榜」')
print('8. 下载「插画本月排行榜」')
print('9. 下载指定画师所有作品')
CHOICE = input('请输入要执行的内容：')

DAILY = 'http://www.pixiv.net/ranking.php?mode=daily'
WEEKLY = 'http://www.pixiv.net/ranking.php?mode=weekly'
MONTHLY = 'http://www.pixiv.net/ranking.php?mode=monthly'
ORIGINAL = 'http://www.pixiv.net/ranking.php?mode=original'
MALE = 'http://www.pixiv.net/ranking.php?mode=male'
ILLUST_DAILY = 'http://www.pixiv.net/ranking.php?mode=daily&content=illust'
ILLUST_WEEKLY = 'http://www.pixiv.net/ranking.php?mode=weekly&content=illust'
ILLUST_MONTHLY = 'http://www.pixiv.net/ranking.php?mode=monthly&content=illust'

if CHOICE == '1':
    WANT = DAILY
elif CHOICE == '2':
    WANT = WEEKLY
elif CHOICE == '3':
    WANT = MONTHLY
elif CHOICE == '4':
    WANT = ORIGINAL
elif CHOICE == '5':
    WANT = MALE
elif CHOICE == '6':
    WANT = ILLUST_DAILY
elif CHOICE == '7':
    WANT = ILLUST_WEEKLY
elif CHOICE == '8':
    WANT = ILLUST_MONTHLY
elif CHOICE == '9':
    WANT = 'http://www.pixiv.net/member_illust.php?id=' + \
        input('请输入要查询的画师 ID：')


def login(account, pwd):
    '''登录 pixiv'''
    loginaddr = 'https://accounts.pixiv.net/login?\
lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    loginapi = 'https://accounts.pixiv.net/api/login?lang=zh'
    head = {'Origin': 'https://accounts.pixiv.net',
            'Host': 'accounts.pixiv.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.103 Safari/537.36',
            'Referer': 'http://www.pixiv.net/', 'Accept-Language': 'zh-CN,zh;q=0.8'}
    session = requests.session()
    obj = session.get(loginaddr, headers=head)
    postkey = re.search(
        r'<input type="hidden" name="post_key" value="(.+?)">', obj.text).group(1)
    data = {'pixiv_id': account,
            'password': pwd,
            'post_key': postkey,
            'return_to': 'http://www.pixiv.net/'}
    session.get(loginaddr, headers=head)
    session.post(loginapi, data=data, headers=head)
    return session

ACCOUNT = input('请输入 ID 或邮箱：')
ACCOUNT = 'daody@qq.com'
PWD = input('请输入密码：')
PWD = '4yVyUUAJhhudrE'
print('正在登录中……')
S = login(ACCOUNT, PWD)
print('登录成功！')

LOG = open('pixiv.log', 'w', encoding='utf-8')


def getinfo(art):
    '''获取作品详细信息和原图网页地址'''
    date = art['data-date']
    artid = art['data-id']
    rank = art['data-rank']
    title = art['data-title']
    score = art['data-total-score']
    user = art['data-user-name']
    view = art['data-view-count']
    link = 'http://www.pixiv.net/' + \
        art.find(class_='ranking-image-item').a['href']
    ulink = 'http://www.pixiv.net/' + \
        art.find(class_='user-container ui-profile-popup')['href']
    tag = art.find(
        class_="_thumbnail ui-scroll-view")['data-tags'].replace(' ', ',')
    arttype = art.find(class_="_thumbnail ui-scroll-view")['data-type']
    print(date, artid, rank, title, score,
          user, view, link, tag, arttype, ulink)
    LOG.writelines([date, '\t', artid, '\t', rank, '\t', title, '\t', score, '\t',
                    user, '\t', view, '\t', link, '\t', tag, '\t', arttype, '\t', ulink, '\t'])
    return link


def download(link):
    '''下载图片'''
    head_img = {'Referer': link, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.103 Safari/537.36'}
    img = S.get(link, headers=HEADON)
    hiimg = BeautifulSoup(img.text, 'lxml')
    temp = hiimg.body.find(id='wrapper').find(class_='wrapper')
    if temp is None:
        print('这是一个画集，暂时无法下载！')
        LOG.writelines('这是一个画集，暂时无法下载！\n')
        return
    # print('>>>', temp)
    try:
        src = temp.find('img')['data-src']
    except KeyError:
        print('这是一个动图，暂时无法下载！')
        LOG.writelines('这是一个动图，暂时无法下载！\n')
        return
    print(src)
    new = S.get(src, headers=head_img)
    pic = open(src.split('/')[-1], 'wb')
    pic.write(new.content)
    print('下载完成！')
    LOG.writelines('下载完成！\n')
    pic.close()


def getother(num):
    '''获得画师其他页面的下载'''
    for i in range(2, num):
        other = WANT + '&p=' + str(i)
        haha = S.get(other, headers=HEADON)
        soup = BeautifulSoup(haha.text, 'lxml')
        for art in soup.find_all(class_='_work'):
            download('http://www.pixiv.net/' + art['href'])

HEADON = {'Host': 'www.pixiv.net',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.103 Safari/537.36',
          'Referer': 'http://www.pixiv.net/', 'Accept-Language': 'zh-CN,zh;q=0.8'}
HAHA = S.get(WANT, headers=HEADON)
# print(HAHA.text)
SOUP = BeautifulSoup(HAHA.text, 'lxml')
if CHOICE != '9':
    for ART in SOUP.find_all(id=re.compile(r'\d')):
        download(getinfo(ART))
else:
    for ART in SOUP.find_all(class_='_work'):
        download('http://www.pixiv.net/' + ART['href'])
    getother(int(SOUP.find(class_='count-badge').text.rstrip('件')) // 20 + 2)

LOG.close()
