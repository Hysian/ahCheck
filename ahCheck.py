#!/usr/bin/env python
#coding: utf-8
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import requests
import time
import json

class login():
    def __init__(self,num,pwd,token):
        self.head = {
                "Host":"api.ahmobile.cn:8081","Accept-Encoding":"gzip","User-Agent":"安徽移动 3.3.2 (iPhone; iPhone OS 9.2.1; en_CN)",
                "Content-Type":"application/x-www-form-urlencoded","Connection":"close","ssoId":'',
                "headmsg": json.dumps({"clientType":"IOS","version_sdk":"9.2.1","yuliuone":"02:00:00:00:00:00","token":"","phoneModle":"iPhone6s","netWorkType":"wifi","version":"3.3.2"})
                 }
        self.form = {
                'userIn.userPasswd': pwd ,'clientVersion': '3.3.2',
                'flag': '1','userIn.phone_no': num,'ytnb': 'true',
                'imei': '','token': token
                }
        #查询签到信息
        self.parms1 = {'token': 'ffc6179a49cf4ddc411c7f93c28b56c6','eip_serv_id' : 'app.getCheckInDate'}
        #签到请求
        self.checkParams = {'token': '3ca39ee0ba60cf01b07a14fe1c4078c5', 'eip_serv_id': 'app.checkInIm'}
        #POST http://api.ahmobile.cn:8081/eip?eip_serv_id=app.rollAndRoll
        self.rollInfo = {'token':'b7ecc9259bfe0882191ffee7255f4f51','ytnb':'true'}
        self.rollPam = {'token':'14a8e241a8b557bf6463bc598042ec51','ytnb':'true'}
        #获取流量情况
        self.fee = {'token':'30d5dc52ea7959f2e53c6fa6eeca88b8','eip_serv_id':'app.queryGprsNew'}
        #获取话费情况
        self.charge = {'eip_serv_id': 'app.service', 'token': '25aa3a79213793ece32892474da34ac2', 'month': '201609', 'page': 'Charge', 'ytnb': 'true'}
        # data = {"eip_serv_id" : "app.ioscheckPwd HTTP"}
        #登陆Url
        self.postUrl = "http://api.ahmobile.cn:8081/eip?eip_serv_id=app.ioscheckPwd"
        self.baseUrl = "http://api.ahmobile.cn:8081/eip"

        self.s = requests.Session()
        self.s.headers.update(self.head)
        self.s.post(self.postUrl, data=self.form)

    def CheckIn(self):
        getCheckPage = self.s.get(self.baseUrl, params=self.parms1) #进入签到页面
        getJson = getCheckPage.json()
        if(getJson['button2'] == u"我要签到"):
            checkin = self.s.get(self.baseUrl, params = self.checkParams) #签到操作
            checkJson = checkin.json()
            str1 = u'---签到信息---\n'\
                   u'时间:%s\n'\
                   u'%s\n '\
                   u'%s \n'\
                   % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), checkJson['msg'], checkJson['checkIn'])
            print str1
        else:
            str1 = u'------签到信息------ \n'\
                   u'时间: %s \n'\
                   u'本月已签到 %s 天\n'\
                   u'今日已签到 √\n'\
                   % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), getJson['day'])
            print str1

        con = self.s.post("http://api.ahmobile.cn:8081/eip?eip_serv_id=app.getShakeInfo",params=self.rollInfo).json()
        if(con['chance'] == 0):
            str2 = u'今日已摇一摇\n'
            print str2
        else:
            roll = self.s.post('http://api.ahmobile.cn:8081/eip?eip_serv_id=app.rollAndRoll',params=self.rollPam).json()
            str2 = roll['awardMsg']
            print str2
        return str2+'\n'
        return str1+str2

    # def getRoll(self):
    #     """
    #     每日摇一摇
    #     """
    #     con = self.s.post("http://api.ahmobile.cn:8081/eip?eip_serv_id=app.getShakeInfo",params=self.rollInfo).json()
    #     if(con['chance'] == 0):
    #         str2 = u'今日已摇一摇\n'
    #         print str2
    #     else:
    #         roll = self.s.post('http://api.ahmobile.cn:8081/eip?eip_serv_id=app.rollAndRoll',params=self.rollPam).json()
    #         str2 = roll['awardMsg']
    #         print str2
    #     return str2+'\n'

    def getInfo(self):
        info = self.s.get(self.baseUrl, params = self.fee).json()
        info2 = self.s.get(self.baseUrl, params = self.charge).json()
        str1 =  u"------账户信息------\n" \
                u"电话: %s\n" \
                u"已用流量 %s MB\n" \
                u"剩余流量 %s\n" \
                u"本月话费 %s 元\n" \
                u"当前余额 %s 元\n" \
                % (info2[0]['phoneNo'],
                    eval(info['appendUflow']),
                    info['appendRflowXww'],
                    info2[1]['baseInstantFee'],
                    info2[1]['balance'])
        print str1
        return str1

    def _format_addr(self,s):
        name, addr = parseaddr(s)
        return formataddr(( \
            Header(name, 'utf-8').encode(), \
            addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    def sendmail(self,txt,mail,i):
        #邮件发送查询信息
        from_addr = '0@hysian.cn' #发件邮箱账号
        from_addr2 = 'hysian0@126.com' #备用发件账号
        password = 'wy@7120'
        if mail is "":
            to_addr = 'hysian0@163.com'#默认发件账号
        else:
            to_addr = mail
        smtp_server = 'smtp.ym.163.com'
        msg = MIMEText(txt, 'plain', 'utf-8')
        n = i
        msg['From'] = self._format_addr(u'服务器 <%s>' %from_addr)
        msg['To'] = self._format_addr(u'君 <%s>' % to_addr)
        msg['Subject'] = Header(u'mobileCheck%s'%n).encode()
        try:

            server = smtplib.SMTP(smtp_server, 25)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
        except:
            server = smtplib.SMTP('smtp.126.com', 25)
            server.login(from_addr2,'hysian0')
            server.sendmail(from_addr2, [to_addr], msg.as_string())
            server.quit()

if __name__ == '__main__':
    #签到账号信息
    FORM = [
        {'userIn.userPasswd': 'azPGGyDaMoM=','userIn.phone_no': '15212997101','token': '7215751b1ed2de841fd705456da36fc7','mail':""}
       ]
    n = 0 #初始化签到次数
    while True:
        time1 = time.time()
        for i in range(len(FORM)):
            p = login(
                      FORM[i]['userIn.phone_no'],
                      FORM[i]['userIn.userPasswd'],
                      FORM[i]['token']
                      )
            try:
                txt = p.CheckIn() + p.getInfo()
                if( n % 2 == 0): #每查询两次发一条邮件
                    print "1"
                    p.sendmail(txt, FORM[i]['mail'], n)
            except:
                p.sendmail("本次查询失败",0,0)
        time2 = time.time()
        sltime = 3600*12 - time2 + time1 #等待时间3小时
        flag = u"查询时间%s \n" \
               u"正在执行第%s 次" %(time2-time1,n)
        print flag
        n += 1
        time.sleep(sltime)

