# coding:utf-8

import pymysql
from NeuralNetwork import NNEmotionClassifyMode
import base64
import jieba as jb
import time


class MessageNew:
    def __init__(self,message:str,time:str,trumpCount:int,userID:any,adminID:any,name:str):
        self.message=message
        self.time=time
        self.trump_count=trumpCount
        self.user_id=userID
        self.admin_id=adminID
        self.name=name


class AttractionComment:
    def __init__(self, comment: str,time: str, trump_count: int, account_id: int, identify: str, name: str, attraction_id: int):
        self.comment=comment
        self.time=time,
        self.trump_count=trump_count
        self.account_id=account_id
        self.identify=identify
        self.name=name,
        self.attraction_id=attraction_id


class MySQLClient:
    def __init__(self,host:str,port:int,username:str,password:str,database:str):
        self.host = host
        self.port = port
        self.user = username
        self.pwd = password
        self.DBName = database
        # 初始化神经网络
        dict_path = "./datasets/word_dict.json"
        stop_words = "./datasets/百度停用词表.txt"
        vec_mode = "./models/vec.model"
        self.NN_mode=NNEmotionClassifyMode(vec_len=100, txt_path=dict_path, stop_words_path=stop_words,vec_mode_path=vec_mode)
        self.NN_mode.load_mode("./models/NN.pickle")

    def login_check(self,username:str,password:str,identify:str) -> dict:
        """登陆检查
        :param username:
        :param password:
        :param identify:身份验证
        """
        # 返回的数据
        tar_user = {'state': -1, 'user': {}}
        tar_user['user']['id'] = ""
        tar_user['user']['name'] = ""
        tar_user['user']['password'] = ""
        tar_user['user']['identify'] = ""
        tar_user['user']['avatar']=""
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        check_SQL_str = "select id,name,password,avatar from %s where name='%s'" % (identify, username)
        cur.execute(check_SQL_str)
        check_rows = cur.fetchall()
        if len(check_rows) < 1:
            # 无账户
            tar_user['state']=-1
            return tar_user
        else:
            for row in check_rows:
                if row[2] == password:
                    tar_user['state']=1
                    tar_user['user']['id']=row[0]
                    tar_user['user']['username']=row[1]
                    tar_user['user']['password']=row[2]
                    tar_user['user']['avatar']=row[3]
                    tar_user['user']['identify']=identify
                    return tar_user
            # 密码错误
            tar_user['state']=0
            return tar_user

    def register_user(self,username:str,password:str) -> dict:
        """
        注册普通用户
        :param username:
        :param password:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        register_sql_str="insert into sp_app_datasets.users (name, password,avatar) values ('%s','%s','')"%(username,password)
        affect_rows=cur.execute(register_sql_str)
        # 获取用户的全部信息
        reg_res = self.login_check(username, password, "users")
        if affect_rows==1:
            reg_res['state']=1
            return reg_res
        else:
            reg_res["state"]=-1
            return reg_res

    def get_messages(self) -> dict:
        """
        获取大厅留言版的信息
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="select id,message,time,trumpCount,userID,adminID,name from messages order by time desc,trumpCount desc,message asc"
        data_ret={'state':1,'dataset':[]}
        cur.execute(get_str)
        message_rows=cur.fetchall()
        for row in message_rows:
            data_ret['dataset'].append({'id':row[0],
                                        'message':row[1],
                                        'time':row[2],
                                        'trumpCount':row[3],
                                        'userID':row[4],
                                        'adminID':row[5],
                                        'name':row[6]})
        for index,item in enumerate(data_ret['dataset']) :
            if item['userID'] is None:
                data_ret['dataset'][index]['identify']='admin'
            else:
                data_ret['dataset'][index]['identify'] = 'users'
        return data_ret

    def add_message(self,messageInfo:MessageNew)->dict:
        """
        添加新的大厅留言信息
        :param messageInfo:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into messages (message, time, trumpCount, userID, adminID, name,emotion) values ('%s','%s',%s,%s,%s,'%s',%s)"""\
                %(messageInfo.message,
                  messageInfo.time,
                  messageInfo.trump_count,
                  messageInfo.user_id,
                  messageInfo.admin_id,
                  messageInfo.name,
                  self.NN_mode.predict_single(messageInfo.message)[0])
        # print(add_str)
        data_ret={'state':1}
        affect_rows=cur.execute(add_str)
        if affect_rows==1:
            return data_ret
        else:
            data_ret['state']=-1
            return data_ret

    def pop_message(self,message_id:int) -> dict:
        """
        清除某一个发言
        :param message_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        del_str="""delete from messages where id=%s"""%message_id
        data_ret={'state':1}
        affect_rows=cur.execute(del_str)
        # 移除该发言下的所有点赞信息
        self.remove_trump_data(message_id)
        if affect_rows>=1:
            return data_ret
        else:
            data_ret['state']=-1
            return data_ret

    def get_trump_data(self,userid:int,identify:str) -> dict:
        """
        获取用户点赞数据
        :param userid:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        select_str="""select id,identify,message_id from trump_messages where id=%s and identify='%s'"""%(userid,identify)
        data_ret={'state':1,'trump_data':[]}
        cur.execute(select_str)
        all_rows=cur.fetchall()
        for row in all_rows:
            data_ret['trump_data'].append({
                "id":row[0],
                "identify":row[1],
                "message_id":row[2]
            })
        return data_ret

    def add_trump_data(self,userid:int,identify:str,message_id:int) -> dict:
        """
        添加点在信息
        :param userid:
        :param identify:
        :param message_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into trump_messages (id, identify, message_id) values (%s,'%s',%s)"""%(userid,identify,message_id)
        data_ret={'state':1}
        affect_rows=cur.execute(add_str)
        if affect_rows==1:
            self.alter_message_trump_count(message_id,1)
            return data_ret
        else:
            data_ret['state']=-1
            return data_ret

    def pop_trump_data(self,userid:int,identify:str,message_id:int) -> dict:
        """
        取消某人在某留言下的点赞
        :param userid:
        :param identify:
        :param message_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        pop_str="""delete from trump_messages where id=%s and identify='%s' and message_id=%s"""%(userid,identify,message_id)
        data_ret = {'state': 1}
        affect_rows = cur.execute(pop_str)
        if affect_rows >= 1:
            self.alter_message_trump_count(message_id,-1)
            return data_ret
        else:
            data_ret['state'] = -1
            return data_ret

    def remove_trump_data(self,message_id:int) -> dict:
        """
        删除某一条留言的所有点赞信息
        :param message_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        remove_str="""delete from trump_messages where message_id=%s"""%message_id
        cur.execute(remove_str)
        return {'state': 1}

    def alter_message_trump_count(self,message_id:int,alter_num:int):
        """
        点赞增加或取消后将messages表的数据及逆行更新
        :param message_id:
        :param alter_num:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        update_str="""update messages set trumpCount = trumpCount+%s where id=%s"""%(alter_num,message_id)
        cur.execute(update_str)

    def alter_user_name(self,userid:int,identify:str,new_name:str) -> dict:
        """
        修改用户名
        :param userid:
        :param identify:
        :param new_name:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        data_ret={'state': 1}
        alter_name_str="""update %s set name='%s' where id=%s"""%(identify,new_name,userid)
        # 首先将用户表或管理员表内的数据进行修改
        if cur.execute(alter_name_str)>=1:
            data_ret['state']=1
            # 修改大厅留言表里面的数据
            if identify=="users":
                alter_name_str="""update messages set name='%s' where userID=%s"""%(new_name,userid)
            elif identify=="admin":
                alter_name_str="""update messages set name='%s' where adminID=%s"""%(new_name,userid)
            cur.execute(alter_name_str)
            return data_ret
        else:
            data_ret['state']=-1
            return data_ret

    def del_account(self,userid:int,username:str,identify:str) -> dict:
        """
        删除账户
        :param userid:
        :param username:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        data_ret = {'state': 1}
        del_str="""delete from %s where id=%s"""%(identify,userid)
        # 首先删除用户表或管理员表里面的数据
        if cur.execute(del_str)>=1:
            data_ret['state'] = 1
            if identify=="users":
                del_str="""delete from messages where userID=%s"""%userid
            elif identify=="admin":
                del_str="""delete from messages where adminID=%s"""%userid
            cur.execute(del_str)
            self.remove_attraction_comment_account(userid,identify)
            return data_ret
        else:
            data_ret['state']=-1
            return data_ret

    def alter_password(self,userid:int,new_pwd:str,identify:str)->dict:
        """
        修改账户密码
        :param userid:
        :param new_pwd:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        data_ret = {'state': 1}
        alter_str="""update %s set password='%s' where id=%s"""%(identify,new_pwd,userid)
        if cur.execute(alter_str)>=1:
            return data_ret
        else:
            data_ret['state']=-1
            return data_ret

    def get_my_hall_messages(self,userid:int,identify:str) -> dict:
        """
        获取用户大厅留言数据
        :param userid:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        if identify=="users":
            get_str="""select id,message,time,trumpCount from messages where userID=%s order by time desc,trumpCount desc,message asc"""%userid
        else:
            get_str="""select id,message,time,trumpCount from messages where adminID=%s order by time desc,trumpCount desc,message asc"""%userid
        data_ret={'state':1,"message_data":[]}
        cur.execute(get_str)
        message_data=cur.fetchall()
        for row in message_data:
            data_ret['message_data'].append({
                "id":row[0],
                "message":row[1],
                "time":row[2],
                "trump_count":row[3]
            })
        return data_ret

    def edit_hall_messages(self,userid:int,identify:str,new_message:str,message_id:int) -> dict:
        """
        修改用户大厅留言
        :param userid:
        :param identify:
        :param new_message:
        :param message_id:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        if identify=="users":
            set_str="""update messages set message='%s' emotion=%s where userID=%s and id=%s"""%\
                    (new_message,self.NN_mode.predict_single(new_message)[0],userid,message_id)
        else:
            set_str="""update messages set message='%s' emotion=%s where adminID=%s and id=%s"""%\
                    (new_message,self.NN_mode.predict_single(new_message)[0],userid,message_id)
        data_ret = {'state': 1}
        if cur.execute(set_str)>=1:
            data_ret['state']=1
        else:
            data_ret['state']=-1
        return data_ret

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
                 self.NN_mode.predict_single(comment)[0])
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

    def remove_attraction_comment_account(self,account_id:int,identify:str) -> dict:
        """
        移除某个用户的所有景点留言
        :param account_id:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        pop_str="""delete from attraction_comments where account_id=%s and identify='%s'"""%(account_id,identify)
        data_ret = {'state': 1}
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
        if len(des)>0:
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
        for el in words_arr:
            words_count[el]=0
        for el in words_arr:
            words_count[el]+=1
        return {"state":1,"words":words_count}

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

    def alter_user_avatar(self,account_id:int,identify:str,avatar_data:str) -> dict:
        """
        修改用户头像
        :param account_id:
        :param identify:
        :param avatar_data:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        base_url = "http://127.0.0.1:5260/"
        save_path = "static/avatar/%s_%s.webp" % (time.time(),account_id)
        image_data = base64.b64decode(avatar_data.split(',')[-1])
        with open(save_path, "wb") as f:
            f.write(image_data)
        alter_str="""update %s set avatar = '%s' where id=%s;"""%(identify,base_url+save_path,account_id)
        data_ret = {'state': 1,'avatar':base_url+save_path}
        cur.execute(alter_str)
        return data_ret

    def get_all_my_attraction_comments(self,account_id:int,identify:str) -> dict:
        """
        获取当前用户在景点下的所有发言
        :param account_id:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,comment,attraction_id,trump_count  from attraction_comments where account_id=%s and identify='%s'"""%\
                (account_id,identify)
        data_ret = {'state': 1,'comments':[]}
        cur.execute(get_str)
        my_comments=cur.fetchall()
        for el in my_comments:
            data_ret['comments'].append({
                "id":el[0],
                "comment":el[1],
                "attraction_id":el[2],
                "trump_count":el[3],
            })
        return data_ret

    def register_admin(self,name:str,password:str) -> dict:
        """
        注册新的管理员账号
        :param name:
        :param password:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into admin (name, password, avatar) values ('%s','%s','');"""%(name,password)
        data_ret={'state':1}
        cur.execute(add_str)
        return data_ret

