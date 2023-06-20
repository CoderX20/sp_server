# coding:utf-8

import pymysql
from dbIO import MySQLClient


class RouteDb(MySQLClient):
    def get_routes_by_userid(self,account_id:int,identify:str) -> dict:
        """
        利用用户id获取路线
        :param account_id:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,account_id,identify,route,name,start,line from routes where account_id=%s and identify='%s'"""%(account_id,identify)
        data_ret = {'state': 1,'routes':[]}
        cur.execute(get_str)
        routes_data=cur.fetchall()
        for row in routes_data:
            data_ret['routes'].append({
                'id':row[0],
                'account_id':row[1],
                'identify':row[2],
                'route':row[3],
                'name':row[4],
                'start':row[5],
                'line':row[6]
            })
        return data_ret

    def add_new_route(self,account_id:int,identify:str,name:str,route:str,start:str,line:str) -> dict:
        """
        添加新的路线
        :param account_id:
        :param identify:
        :param name:
        :param route:
        :param start:
        :param line:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into routes (name, account_id, identify, route,start,line) values ('%s',%s,'%s','%s','%s','%s')"""%\
                (name,account_id,identify,route,start,line)
        data_ret = {'state': 1}
        cur.execute(add_str)
        return data_ret

    def update_route_attractions(self,route_id:int,attractions:str) -> dict:
        """
        更新路线上的旅游景点
        :param route_id:
        :param attractions:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        update_str="""update routes set route='%s' where id=%s"""%(attractions,route_id)
        cur.execute(update_str)
        return data_ret

    def add_route_start(self,route_id:int,route_start:str) -> dict:
        """
        修改路线上的起始点
        :param route_id:
        :param route_start:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        update_str="""update routes set start='%s' where id=%s"""%(route_start,route_id)
        cur.execute(update_str)
        return data_ret

