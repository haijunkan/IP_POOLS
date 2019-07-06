import requests
from scrapy.selector import Selector
import time
import pymysql

dbparams= {
            'host':'127.0.0.1',
            'port':3306,
            'user':'root',
            'password':'123456',
            'database':'jianshu2',
            'charset':'utf8',
        }
conn = pymysql.connect(**dbparams)
cursor = conn.cursor()


def crawl_ip():
    headers = {
        'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",

    }
    for i in range(1,30):
        url = 'https://www.kuaidaili.com/free/inha/{0}/'.format(i)
        re = requests.get(url=url, headers=headers)
        print(url)
        selector = Selector(text=re.text)
        trs = selector.xpath('//tbody//tr')
        ip_list=[]
        for tr in trs[1:]:
            list = tr.xpath('.//text()').getall()
            ip = list[1]
            port = list[3]
            proxy_type = 'http'
            ip_list.append((ip,port,proxy_type))
            # break
        for ip_info in ip_list:
            cursor.execute("insert into proxy_ip(ip, port, proxy_type) VALUES('{0}','{1}','http')".format(ip_info[0],ip_info[1]))
            # cursor.execute(
            #     "insert into proxy_ip(ip, port, proxy_type) VALUES(%s,%s,%s,)")
            conn.commit()
        time.sleep(2)
        # break


class GetIp(object):
    def JudgeIp(self, ip, port):
        http_url = 'http://www.baidu.com'
        proxy_url = 'http://{0}:{1}'.format(ip, port)
        try:
            proxy_dict = {
                "http":proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict, timeout=5)
        except Exception as e:
            print('invalid ip and port')
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code>=200 and code <300:
                print('effective ip')
                print(ip, port)
            else:
                print('invalid ip and port')
                self.delete_ip(ip)
                return False

    def delete_ip(self, ip):
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def get_random_ip(self):
        random_sql = """
            SELECT ip,port FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.JudgeIp(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()

if __name__ == '__main__':

    crawl_ip()
    # get_ip = GetIp()
    # get_ip.get_random_ip()