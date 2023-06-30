# coding:utf-8
import json

import pymysql
from dbIO import MySQLClient
import time
import base64


class PersonDb(MySQLClient):
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
        data_ret = {'state': 1, "message_data": []}
        if userid is None or identify is None:
            data_ret['state']=-1
            return data_ret
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        if identify=="users":
            get_str="""select id,message,time,trumpCount from messages where userID=%s order by time desc,trumpCount desc,message asc"""%userid
        else:
            get_str="""select id,message,time,trumpCount from messages where adminID=%s order by time desc,trumpCount desc,message asc"""%userid
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
                    (new_message,self.NN_mode.predict_pro(new_message),userid,message_id)
        else:
            set_str="""update messages set message='%s' emotion=%s where adminID=%s and id=%s"""%\
                    (new_message,self.NN_mode.predict_pro(new_message),userid,message_id)
        data_ret = {'state': 1}
        if cur.execute(set_str)>=1:
            data_ret['state']=1
        else:
            data_ret['state']=-1
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
        data_ret = {'state': 1, 'comments': []}
        if account_id is None or identify is None :
            data_ret['state']=-1
            return data_ret
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,comment,attraction_id,trump_count,time from attraction_comments where account_id=%s and identify='%s'"""%\
                (account_id,identify)
        # print(get_str)
        cur.execute(get_str)
        my_comments=cur.fetchall()
        for el in my_comments:
            data_ret['comments'].append({
                "id":el[0],
                "comment":el[1],
                "attraction_id":el[2],
                "trump_count":el[3],
                "time":el[4]
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
        add_str="""insert into admin (name, password, avatar,signature) values ('%s','%s','','');"""%(name,password)
        data_ret={'state':1}
        cur.execute(add_str)
        return data_ret

    def edit_my_signature(self,account_id:int,identify:str,signature:str) -> dict:
        """
        编辑我的个性签名
        :param account_id:
        :param identify:
        :param signature:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        edit_str="""update %s set signature='%s' where id=%s"""%(identify,signature,account_id)
        data_ret = {'state': 1}
        cur.execute(edit_str)
        return data_ret

    def get_user_info(self,account_id:int,identify:str) -> dict:
        """
        获取用户基本信息
        :param account_id:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select name,avatar,signature from %s where id=%s"""%(identify,account_id)
        data_ret={'state':-1,'user':{}}
        if account_id is None or (identify != "admin" and identify != "users"):
            return data_ret
        cur.execute(get_str)
        user_data=cur.fetchall()
        if len(user_data)>0:
            data_ret['state']=1
            data_ret['user']['name']=user_data[0][0]
            data_ret['user']['avatar']=user_data[0][1]
            data_ret['user']['signature']=user_data[0][2]
        return data_ret

    def add_space_messages(self,account_id:int,identify:str,message:str,img:str,deliver_time:str,trump_count=0,collect_count=0) -> dict:
        """
        发表新的空间发言
        :param account_id:
        :param identify:
        :param message:
        :param img:
        :param deliver_time:
        :param trump_count:
        :param collect_count:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        base_url = "http://127.0.0.1:5260/"
        space_img=[]
        for index,item in enumerate(img.split('\n')):
            save_path="static/space/%s_%s_%s.webp"%(time.time(),account_id,index)
            img_data=base64.b64decode(item.split(',')[-1])
            with open(save_path,'wb') as file_img:
                file_img.write(img_data)
            space_img.append(base_url+save_path)
        add_str="""insert into space_messages (account_id, identify, message, img, trump_count, collect_count, time) 
        values (%s,'%s','%s','%s',%s,%s,'%s');"""%\
                (account_id,identify,message,'\n'.join(space_img),trump_count,collect_count,deliver_time)
        cur.execute(add_str)
        return data_ret

    def get_space_messages(self,account_id:int,identify:str) -> dict:
        """
        获取个人空间内的发言信息
        :param account_id:
        :param identify:
        :return:
        """
        data_ret = {'state': -1,'message_list':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select id,account_id,identify,message,img,trump_count,collect_count ,time
        from space_messages where account_id=%s and identify='%s'"""%\
                (account_id,identify)
        if account_id is None or (identify != "admin" and identify != "users"):
            return data_ret
        cur.execute(get_str)
        space_data=cur.fetchall()
        for row in space_data:
            data_ret['message_list'].append({
                'id':row[0],
                'account_id':row[1],
                'identify':row[2],
                'message':row[3],
                'img':row[4],
                'trump_count':row[5],
                'collect_count':row[6],
                'time':row[7],
                'name': self.get_name_id(row[1], row[2]),
            })
        return data_ret

    def trump_space_message(self,account_id:int,identify:str,message_id:int) -> dict:
        """
        点赞个人空间里的留言动态
        :param account_id:
        :param identify:
        :param message_id:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into trump_space_messages (id, identify, message_id) values (%s,'%s',%s);"""%(account_id,identify,message_id)
        cur.execute(add_str)
        self.update_space_message_trump_count(message_id)
        return data_ret

    def cancel_trump_space_message(self,account_id:int,identify:str,message_id:int) -> dict:
        """
        取消点赞个人空间里面的留言动态
        :param account_id:
        :param identify:
        :param message_id:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        del_str="""delete from trump_space_messages where id=%s and identify='%s' and message_id=%s;"""%(account_id,identify,message_id)
        cur.execute(del_str)
        self.update_space_message_trump_count(message_id)
        return data_ret

    def get_my_trump_data(self,account_id:int,identify:str) -> dict:
        """
        获取当前用户的点赞数据
        :param account_id:
        :param identify:
        :return:
        """
        data_ret={'state':1,'messages':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select message_id from trump_space_messages where id=%s and identify='%s'"""%(account_id,identify)
        cur.execute(get_str)
        trump_data=cur.fetchall()
        for row in trump_data:
            data_ret['messages'].append(row[0])
        return data_ret

    def get_space_message_collect_data(self,account_id:int,identify:str) -> dict:
        """
        获取当前用户在个人空间留言动态的收藏数据
        :param account_id:
        :param identify:
        :return:
        """
        data_ret = {'state': 1, 'messages': []}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        get_str="""select message_id from collect_space_messages where id=%s and identify='%s'"""%(account_id,identify)
        cur.execute(get_str)
        collect_data=cur.fetchall()
        for row in collect_data:
            data_ret['messages'].append(row[0])
        return data_ret

    def del_space_message(self,message_id:int) -> dict:
        """
        删除空间留言动态
        :param message_id:
        :return:
        """
        data_ret={'state':1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        del_str="""delete from space_messages where id=%s;"""%message_id
        cur.execute(del_str)
        return data_ret

    def collect_space_message(self,account_id:int,identify:str,message_id:int) -> dict:
        """
        收藏空间留言动态
        :param account_id:
        :param identify:
        :param message_id:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        add_str="""insert into collect_space_messages (id, identify, message_id) values (%s,'%s',%s);"""%\
                (account_id,identify,message_id)
        cur.execute(add_str)
        self.update_space_message_collect_count(message_id)
        return data_ret

    def cancel_collect_space_message(self,account_id:int,identify:str,message_id:int) -> dict:
        """
        取消收藏留言动态
        :param account_id:
        :param identify:
        :param message_id:
        :return:
        """
        data_ret = {'state': 1}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        del_str="""delete from collect_space_messages where id=%s and identify='%s' and message_id=%s;"""%\
                (account_id,identify,message_id)
        cur.execute(del_str)
        self.update_space_message_collect_count(message_id)
        return data_ret

    def get_my_collect_messages(self,account_id:int,identify:str) -> dict:
        """
        获取我的个人空间留言收藏
        :param account_id:
        :param identify:
        :return:
        """
        data_ret={'state':1,'collect_list':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        cur.execute("""select id,account_id,identify,message,img,trump_count,collect_count,time from space_messages where id in 
        (select message_id from collect_space_messages where id=%s and identify=%s)"""
                    ,(account_id,identify,))
        message_list=cur.fetchall()
        for row in message_list:
            data_ret['collect_list'].append({
                'id': row[0],
                'account_id': row[1],
                'identify': row[2],
                'message': row[3],
                'img': row[4],
                'trump_count': row[5],
                'collect_count': row[6],
                'time': row[7],
                'name': self.get_name_id(row[1],row[2]),
            })
        return data_ret

    def get_name_id(self,account_id:int,identify:str) -> str:
        """
        获取用户姓名
        :param account_id:
        :param identify:
        :return:
        """
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        cur.execute("""select name from %s where id=%s"""%(identify,account_id))
        name_list=cur.fetchall()
        if len(name_list)>0:
            return name_list[0][0]

    def get_my_orders(self,account_id:int,identify:str)-> dict:
        """
        获取我的订单数据
        :param account_id:
        :param identify:
        :return:
        """
        data_ret={'state':1,'order_list':[]}
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        cur.execute("""select route_order.id,account_id,identify,route,price,agency_id,ta.agency_name,ta.phone,time 
        from route_order 
        join travel_agency ta on route_order.agency_id = ta.id 
        where account_id=%s and identify=%s""",(account_id,identify))
        order_data=cur.fetchall()
        for row in order_data:
            data_ret['order_list'].append({
                'id':row[0],
                'account_id':row[1],
                'identify':row[2],
                'route':json.loads(row[3]),
                'price':row[4],
                'agency_id':row[5],
                'agency_name':row[6],
                'agency_phone':row[7],
                'time':row[8]
            })
        return data_ret


