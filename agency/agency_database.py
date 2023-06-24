# coding:utf-8

import pymysql
from dbIO import MySQLClient
import time


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
