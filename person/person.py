# coding:utf-8

from flask import make_response,jsonify,request,Blueprint
from person.person_database import PersonDb


db_set=PersonDb(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')
person_bp=Blueprint("person",__name__,url_prefix='')


@person_bp.route('/alterName',methods=['POST'])
def alter_name():
    """
    修改用户名
    :return:
    """
    data=request.get_json()
    userid=data.get('userid')
    new_name=data.get('newName')
    identify=data.get('identify')
    post_res=db_set.alter_user_name(userid,identify,new_name)
    return make_response(jsonify(post_res))


@person_bp.route("/delMyAccount",methods=['POST'])
def del_account():
    """
    删除账户
    """
    data=request.get_json()
    userid=data.get('id')
    identify=data.get('identify')
    post_res=db_set.del_account(userid=userid,identify=identify,username="")
    return make_response(jsonify(post_res))


@person_bp.route('/alterPassword',methods=["POST"])
def alter_password():
    """
    修改密码
    :return:
    """
    data=request.get_json()
    userid=data.get('id')
    new_pwd=data.get('newPwd')
    identify=data.get('identify')
    post_res=db_set.alter_password(userid,new_pwd,identify)
    return make_response(jsonify(post_res))


@person_bp.route('/getMyHallMessages',methods=['POST'])
def get_my_hall_messages():
    """
    获取账户大厅留言数据
    :return:
    """
    data = request.get_json()
    userid = data.get('id')
    identify=data.get('identify')
    post_res=db_set.get_my_hall_messages(userid,identify)
    return make_response(jsonify(post_res))


@person_bp.route('/editHallMessage',methods=["POST"])
def edit_hall_message():
    """
    编辑账户大厅留言
    :return:
    """
    data=request.get_json()
    userid = data.get('userid')
    identify = data.get('identify')
    message_id=data.get('message_id')
    new_message=data.get('new_message')
    post_res=db_set.edit_hall_messages(userid,identify,new_message,message_id)
    return make_response(jsonify(post_res))


@person_bp.route('/alterAccountAvatar',methods=['POST'])
def alter_user_avatar():
    """
    修改用户头像
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    avatar_data=data.get('avatar_data')
    post_res=db_set.alter_user_avatar(account_id,identify,avatar_data)
    return make_response(jsonify(post_res))


@person_bp.route('/getAllMyAttractionComments',methods=['POST'])
def get_all_my_attractions_comments():
    """
    获取当前用户的所有景区评论信息
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    post_res=db_set.get_all_my_attraction_comments(account_id,identify)
    return make_response(jsonify(post_res))


@person_bp.route('/registerAdmin',methods=["POST"])
def register_admin():
    """
    注册新的管理员账户
    :return:
    """
    data=request.get_json()
    name=data.get('name')
    password=data.get('password')
    post_res=db_set.register_admin(name,password)
    return make_response(jsonify(post_res))


@person_bp.route('/editMySignature',methods=['POST'])
def edit_my_signature():
    """
    编辑个性签名
    :return:
    """
    data=request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    signature=data.get('signature')
    post_res=db_set.edit_my_signature(account_id,identify,signature)
    return make_response(jsonify(post_res))


@person_bp.route('/getUserInfo',methods=['POST'])
def get_user_info():
    """
    获取用户基础信息
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    post_res=db_set.get_user_info(account_id,identify)
    return make_response(jsonify(post_res))


