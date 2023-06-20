# coding: utf-8

from flask import Blueprint,make_response,request,jsonify
from hall.database import HallDb
from dbIO import MessageNew


hall_bp=Blueprint("hall",__name__,url_prefix='')
db_set=HallDb(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')


@hall_bp.route('/getMessages',methods=['POST'])
def get_message():
    """
    获取大厅留言信息
    :return:
    """
    data_get=make_response(jsonify(db_set.get_messages()))
    return data_get


@hall_bp.route('/addMessage',methods=['POST'])
def add_messages():
    """
    添加大厅新的留言
    :return:
    """
    data=request.get_json()
    message=data.get('message')
    deliver_time=data.get('time')
    trump_count=data.get('trumpCount')
    user_id=data.get('userID')
    admin_id=data.get('adminID')
    name=data.get('name')
    identify=data.get('identify')
    if identify=="users":
        admin_id='null'
        user_id=int(user_id)
    elif identify=="admin":
        user_id='null'
        admin_id=int(admin_id)
    else:
        return make_response(jsonify({'state':-1}))
    message_new=MessageNew(message,deliver_time,int(trump_count),user_id,admin_id,name)
    add_res=make_response(jsonify(db_set.add_message(message_new)))
    return add_res


@hall_bp.route('/popMessage',methods=['POST'])
def pop_message():
    """
    删除某一个大厅发言
    :return:
    """
    data=request.get_json()
    message_id=data.get('id')
    pop_res=db_set.pop_message(message_id)
    return make_response(jsonify(pop_res))


@hall_bp.route('/getTrumpData',methods=['POST'])
def get_trump_datasets():
    """
    获取点赞数据
    :return:
    """
    data=request.get_json()
    userid=data.get('id')
    identify=data.get('identify')
    post_res=db_set.get_trump_data(userid,identify)
    return make_response(jsonify(post_res))


@hall_bp.route('/trumpHallMessage',methods=['POST'])
def trump_hall_message():
    """
    点赞某一大厅留言
    :return:
    """
    data=request.get_json()
    userid=data.get('id')
    identify=data.get('identify')
    message_id=data.get('message_id')
    post_res=db_set.add_trump_data(userid,identify,message_id)
    return make_response(jsonify(post_res))


@hall_bp.route('/cancelTrumpHallMessage',methods=['POST'])
def cancel_trump_hall_message():
    """
    某一用户取消某一大厅留言的点赞
    :return:
    """
    data = request.get_json()
    userid = data.get('id')
    identify = data.get('identify')
    message_id = data.get('message_id')
    post_res=db_set.pop_trump_data(userid,identify,message_id)
    return post_res

