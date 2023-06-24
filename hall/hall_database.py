# coding:utf-8

from dbIO import MySQLClient,MessageNew
import pymysql


class HallDb(MySQLClient):
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
                  self.NN_mode.predict_pro(messageInfo.message))
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
        获取用户大厅发言点赞数据
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

    def get_hot_attractions(self):
        """
        获取热门推荐景点
        :return:
        """
        data_ret = {'state': 1,"attractions":[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,name,img from attractions where level='5A' or level='4A' and img is not null order by rand() limit 5"""
        cur.execute(get_str)
        attractions=cur.fetchall()
        for row in attractions:
            data_ret["attractions"].append({
                "id":row[0],
                "name":row[1],
                "img":row[2],
            })
        return data_ret
