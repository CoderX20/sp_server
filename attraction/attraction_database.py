# coding:utf-8

from dbIO import MySQLClient
import pymysql
import jieba as jb
import base64
import time
import json


class AttractionDB(MySQLClient):
    def get_attractions_city(self) -> dict:
        """
        获取景区城市信息
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select distinct city from attractions"""
        cur.execute(get_str)
        data_ret = {'state': 1, "city": []}
        for row in cur.fetchall():
            data_ret['city'].append(row[0])
        return data_ret

    def get_attraction_level(self) -> dict:
        """
        获取景区A级信息
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str = """select distinct level from attractions"""
        cur.execute(get_str)
        data_ret = {'state': 1, "level": []}
        for row in cur.fetchall():
            data_ret['level'].append(row[0])
        return data_ret

    def get_attractions_range(self,start:int,end:int,city:str,level:str,keyword:str) -> dict:
        """
        通过一定条件获取一定范围内的景区
        :param start:
        :param end:
        :param city:
        :param level:
        :param keyword:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,name,city,county,address,level,lng,lat,score,img,period from attractions where 1=1 """
        if len(city)>0:
            get_str+=""" and city='%s' """%city
        if len(level)>0:
            get_str+=""" and level='%s' """%level
        if len(keyword)>0:
            get_str+=""" and name like '%{}%' """.format(keyword)
        # print(get_str)
        cur.execute(get_str)
        data_ret = {'state': 1, "attractions": []}
        selected_data=cur.fetchall()
        if len(selected_data)>0:
            for row in selected_data[start:end+1]:
                data_ret['attractions'].append({
                    "id":row[0],
                    "name":row[1],
                    "city":row[2],
                    "county":row[3],
                    "address":row[4],
                    "level":row[5],
                    "lng":row[6],
                    "lat":row[7],
                    "score":row[8],
                    "img":row[9],
                    "period":row[10],
                })
        return data_ret

    def get_attraction_by_id(self,attraction_id:int) -> dict:
        """
        通过id号获取景点信息
        :param attraction_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,name,city,county,address,level,lng,lat,score,img,des,period from attractions where id=%s"""%attraction_id
        data_ret = {'state': 1, "attractions": {}}
        # print(get_str)
        cur.execute(get_str)
        attraction_detail=cur.fetchall()[0]
        data_ret['attractions']['id']=attraction_detail[0]
        data_ret['attractions']['name']=attraction_detail[1]
        data_ret['attractions']['city']=attraction_detail[2]
        data_ret['attractions']['county']=attraction_detail[3]
        data_ret['attractions']['address']=attraction_detail[4]
        data_ret['attractions']['level']=attraction_detail[5]
        data_ret['attractions']['lng']=attraction_detail[6]
        data_ret['attractions']['lat']=attraction_detail[7]
        data_ret['attractions']['score']=attraction_detail[8]
        data_ret['attractions']['img']=attraction_detail[9]
        data_ret['attractions']['des']=attraction_detail[10]
        data_ret['attractions']['period']=attraction_detail[11]
        return data_ret

    def add_attraction_score(self,account_id:int,identify:str,attraction_id:int,score:float) -> dict:
        """
        添加景点评分
        :param account_id:
        :param identify:
        :param attraction_id:
        :param score:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into attractions_score (account_id, identify, attraction_id, score) values (%s,'%s',%s,%s)"""%\
                (account_id,identify,attraction_id,score)
        data_ret={'state':1}
        cur.execute(add_str)
        self.update_attractions_score(attraction_id)
        return data_ret

    def alter_attraction_score(self,account_id:int,identify:str,attraction_id:int,score:float)->dict:
        """
        修改景点评分
        :param account_id:
        :param identify:
        :param attraction_id:
        :param score:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        alter_str="""update attractions_score set score=%s where account_id=%s and identify='%s' and attraction_id=%s"""%\
                  (score,account_id,identify,attraction_id)
        data_ret = {'state': 1}
        # print(alter_str)
        cur.execute(alter_str)
        self.update_attractions_score(attraction_id)
        return data_ret

    def update_attractions_score(self,attraction_id:int) -> dict:
        """
        更新景区评分的平均值
        :param attraction_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        update_str="""update attractions set score=(select avg(score) from attractions_score where attraction_id=%s) where id=%s"""%\
                   (attraction_id,attraction_id)
        cur.execute(update_str)
        return {'state':1}

    def get_user_attraction_score(self,account_id:int,identify:str,attraction_id:int)->dict:
        """
        获取某个用户在某个景点上的评分
        :param account_id:
        :param identify:
        :param attraction_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select score from attractions_score where account_id=%s and identify='%s' and attraction_id=%s"""%\
                (account_id,identify,attraction_id)
        # print(get_str)
        cur.execute(get_str)
        data_ret = {'state': 1,'score':-1}
        select_data=cur.fetchall()
        if len(select_data)>0:
            data_ret['score']=select_data[0][0]
        return data_ret

    def get_attraction_comments(self,attraction_id:int) -> dict:
        """
        获取旅游景点的评论
        :param attraction_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,comment,account_id,identify,name,trump_count,time,emotion 
        from attraction_comments 
        where attraction_id=%s 
        order by time asc,trump_count desc ;"""%attraction_id
        data_ret={'state':1,'comments':[]}
        cur.execute(get_str)
        comments=cur.fetchall()
        for row in comments:
            data_ret['comments'].append({
                "id":row[0],
                'comment':row[1],
                'account_id':row[2],
                'identify':row[3],
                'name':row[4],
                'trump_count':row[5],
                'time':row[6],
                "emotion":row[7]
            })
        return data_ret

    def add_new_attraction_comment(self,comment:str,time:str,attraction_id:int,account_id,name:str,identify:str) -> dict:
        """
        添加新的经典评论
        :param comment:
        :param time:
        :param attraction_id:
        :param account_id:
        :param name:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into attraction_comments ( comment, attraction_id, account_id, identify, name, trump_count, time, emotion) 
        values ('%s',%s,%s,'%s','%s',0,'%s',%s)"""%\
                (comment,
                 attraction_id,
                 account_id,
                 identify,
                 name,
                 time,
                 self.NN_mode.predict_pro(comment))
        # print(add_str)
        data_ret={'state':1}
        cur.execute(add_str)
        return data_ret

    def alter_attraction_comment(self,comment_id:int,comment_new:str) -> dict:
        """
        修改景区评论
        :param comment_id:
        :param comment_new:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        alter_str="""update attraction_comments set comment='%s' where id=%s"""%(comment_new,comment_id)
        data_ret = {'state': 1}
        if cur.execute(alter_str)==1:
            data_ret['state']=1
        else:
            data_ret['state']=-1
        return data_ret

    def remove_attraction_comment_id(self,comment_id:int) -> dict:
        """
        通过id移除景点评论
        :param comment_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        pop_str="""delete from attraction_comments where id=%s"""%comment_id
        data_ret={'state': 1}
        cur.execute(pop_str)
        return data_ret

    def trump_attraction_comment(self,account_id:int,identify:str,comment_id:int) -> dict:
        """
        对某个景点评论进行点赞操作
        :param account_id:
        :param identify:
        :param comment_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into trump_attraction_comments (account_id, identify, comment_id) values (%s,'%s',%s)"""%\
                (account_id,identify,comment_id)
        data_ret = {'state': 1}
        cur.execute(add_str)
        # 更新景点评论点赞数
        self.alter_attraction_comment_trump_count(comment_id,1)
        return data_ret

    def cancel_trump_attraction_comment(self,account_id:int,identify:str,comment_id:int) -> dict:
        """
        取消经典评论点赞操作
        :param account_id:
        :param identify:
        :param comment_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        del_str="""delete from trump_attraction_comments where account_id=%s and identify='%s' and comment_id=%s"""%\
                (account_id,identify,comment_id)
        data_ret = {'state': 1}
        cur.execute(del_str)
        # 更新景点评论点赞数
        self.alter_attraction_comment_trump_count(comment_id,-1)
        return data_ret

    def alter_attraction_comment_trump_count(self,comment_id:int,alter_num:int) -> dict:
        """
        更新景点评论点赞数据
        :param comment_id:
        :param alter_num:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        update_str="""update attraction_comments set trump_count =trump_count+%s where id=%s"""%(alter_num,comment_id)
        data_ret = {'state': 1}
        cur.execute(update_str)
        return data_ret

    def get_my_attraction_trump_comment(self,account_id:int,identify:str) -> dict:
        """
        获取我的景点评论点赞数据
        :param account_id:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select comment_id from trump_attraction_comments where account_id=%s and identify='%s'"""%(account_id,identify)
        data_ret={'state': 1,"comments":[]}
        cur.execute(get_str)
        my_trump_comments=cur.fetchall()
        for row in my_trump_comments:
            data_ret["comments"].append(row[0])
        return data_ret

    def upload_attraction_des(self,attraction_id:int,des:str,img:str) -> dict:
        """
        上传景点描述和图片
        :param attraction_id:
        :param des:
        :param img:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        data_ret = {'state': 1}
        base_url="http://127.0.0.1:5260/"
        if img is not None:
            save_path="static/img/%s_%s.webp"%(attraction_id,time.time())
            image_data=base64.b64decode(img.split(',')[-1])
            with open(save_path, "wb") as f:
                f.write(image_data)
            upload_str="""update attractions set img='%s' where id=%s """%(base_url+save_path,attraction_id)
            cur.execute(upload_str)
            data_ret['img']=base_url+save_path
        if des is not None:
            upload_str="""update attractions set des='%s' where id=%s """%(des,attraction_id)
            cur.execute(upload_str)
            data_ret['des']=des
        return data_ret

    def get_word_cut_attraction_by_id(self,attraction_id:int) -> dict:
        """
        通过id获取某一个景点的评论的分词以及统计
        :param attraction_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select comment from attraction_comments where attraction_id=%s"""%attraction_id
        cur.execute(get_str)
        comments=cur.fetchall()
        # print(comments)
        words_arr=[]
        for el in comments:
            words_arr+=jb.lcut(el[0])
        words_count={}
        words_new=[x for x in words_arr if x not in self.stop_words]
        for el in words_new:
            words_count[el]=0
        for el in words_new:
            words_count[el]+=1
        return {"state":1,"words":words_count}

    def get_attraction_heat_data(self) -> dict:
        """
        获取景点数据的热力图数据
        :return:
        """
        data_ret={'state':1,'heat_data':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_route_str="""select route from routes"""
        cur.execute(get_route_str)
        route_data=cur.fetchall()
        node_list=[]
        for row in route_data:
            node_list+=json.loads(str(row[0]))['nodes']
        get_attraction_str = """select id,lat,lng from attractions"""
        cur.execute(get_attraction_str)
        attraction_data=cur.fetchall()
        for item in attraction_data:
            data_ret['heat_data'].append([item[1], item[2], len([x for x in node_list if x['id'] == item[0]])])
        return data_ret


