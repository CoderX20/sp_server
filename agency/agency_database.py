# coding:utf-8

import pymysql
from dbIO import MySQLClient
import time
import random


class AgencyDB(MySQLClient):
    def get_hot_agency(self) -> dict:
        """
        获取热门旅行社
        :return:
        """
        data_ret={'state':1,'hot_agency':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,agency_name,phone,score,license from travel_agency where phone is not null order by rand() limit 10"""
        cur.execute(get_str)
        hot_agency_list=cur.fetchall()
        for row in hot_agency_list:
            data_ret['hot_agency'].append({
                "id":row[0],
                "agency_name":row[1],
                "phone":row[2],
                "score":row[3],
                "license":row[4],
            })
        return data_ret

    def get_agency_by_city(self,city:str,keyword:str,start:int,end:int) -> dict:
        """
        查询符合要求的旅行社名称
        :param city:
        :param keyword:
        :param start:
        :param end:
        :return:
        """
        data_ret={'state':1,"agency":[],"total":0}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,agency_name,phone,score,license from travel_agency where 1=1 """
        if len(city)>0:
            get_str+=f""" and address like '%{city}%' """
        if len(keyword)>0:
            get_str+=f""" and (agency_name like '%{keyword}%' or address like '%{keyword}%' or license like '%{keyword}%' 
            or phone like '%{keyword}%' or fax like '%{keyword}%') """
        # print(get_str)
        cur.execute(get_str)
        agency_list=cur.fetchall()
        data_ret["total"]= len(agency_list)
        for row in agency_list[start:end+1]:
            data_ret["agency"].append({
                'id':row[0],
                'agency_name':row[1],
                'phone':row[2],
                'score':row[3],
                'license':row[4],
            })
        return data_ret

    def get_agency_by_id(self,agency_id:int) -> dict:
        """
        根据id获取旅行社数据
        :param agency_id:
        :return:
        """
        data_ret={'state':-1,'agency_info':{}}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,agency_name,address,license,phone,fax,score from travel_agency where id=%s"""%agency_id
        cur.execute(get_str)
        agency_data=cur.fetchall()
        if len(agency_data)>0:
            data_ret['state']=1
            data_ret['agency_info']['id']=agency_data[0][0]
            data_ret['agency_info']['agency_name']=agency_data[0][1]
            data_ret['agency_info']['address']=agency_data[0][2]
            data_ret['agency_info']['license']=agency_data[0][3]
            data_ret['agency_info']['phone']=agency_data[0][4]
            data_ret['agency_info']['fax']=agency_data[0][5]
            data_ret['agency_info']['score']=agency_data[0][6]
        return data_ret

    def get_my_agency_score(self,account_id:int,identify:str,agency_id:int) -> dict:
        """
        获取当前用户在旅行社下的评分
        :param account_id:
        :param identify:
        :param agency_id:
        :return:
        """
        data_ret={'state':1,'score':-1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select score from agency_score where account_id=%s and identify='%s' and agency_id=%s"""%\
                (account_id,identify,agency_id)
        cur.execute(get_str)
        score_data=cur.fetchall()
        if len(score_data)>0:
            data_ret['score']=score_data[0][0]
            return data_ret
        return data_ret

    def add_agency_score(self,account_id:int,identify:str,agency_id:int,score:int) -> dict:
        """
        添加旅行社评分
        :param account_id:
        :param identify:
        :param agency_id:
        :param score:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into agency_score (account_id, identify, agency_id, score) values (%s,'%s',%s,%s);"""%\
                (account_id,identify,agency_id,score)
        cur.execute(add_str)
        self.update_agency_score(agency_id)
        return data_ret

    def alter_agency_score(self,account_id:int,identify:str,agency_id:int,score:int) -> dict:
        """
        修改个人旅行社评分
        :param account_id:
        :param identify:
        :param agency_id:
        :param score:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        alter_str="""update agency_score set score =%s where account_id=%s and identify='%s' and agency_id=%s;"""%\
                  (score,account_id,identify,agency_id)
        cur.execute(alter_str)
        self.update_agency_score(agency_id)
        return data_ret

    def update_agency_score(self,agency_id:int):
        """
        更新旅行社评分
        :param agency_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        update_str="""update travel_agency set score=(select avg(score) from agency_score where agency_id=%s) where id=%s"""%\
                   (agency_id,agency_id)
        cur.execute(update_str)

    def get_agency_attractions(self) -> dict:
        """
        根据旅行社查找当地的景点
        :param address:
        :return:
        """
        data_ret={'state':1,'attraction_list':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        attraction_count=random.randint(10,30)
        get_str="""select id,name,address,level,img,lat,lng from attractions order by rand() limit %s"""%attraction_count
        cur.execute(get_str)
        attraction_data=cur.fetchall()
        for row in attraction_data:
            data_ret['attraction_list'].append({
                'id':row[0],
                'name':row[1],
                'address':row[2],
                'level':row[3],
                'img':row[4],
                'lat':row[5],
                'lng':row[6],
                'price':random.randint(50,2000)
            })
        return data_ret


