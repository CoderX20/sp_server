# coding:utf-8

import pymysql
from NeuralNetwork import NNEmotionClassifyMode


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
        with open(stop_words,encoding="UTF-8") as file_txt:
            self.stop_words=file_txt.read().split('\n')

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
        tar_user['user']['signature']=""
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.DBName, autocommit=True)
        cur = con.cursor()
        check_SQL_str = "select id,name,password,avatar,signature from %s where name='%s'" % (identify, username)
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
                    tar_user['user']['signature']=row[4]
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
        register_sql_str="insert into sp_app_datasets.users (name, password,avatar,signature) values ('%s','%s','','')"%(username,password)
        affect_rows=cur.execute(register_sql_str)
        # 获取用户的全部信息
        reg_res = self.login_check(username, password, "users")
        if affect_rows==1:
            reg_res['state']=1
            return reg_res
        else:
            reg_res["state"]=-1
            return reg_res

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



