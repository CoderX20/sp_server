# coding:utf-8

from flask import Blueprint,make_response,request,jsonify
from attraction.attraction_database import AttractionDB


attraction_bp=Blueprint("attraction",__name__,url_prefix='')
db_set=AttractionDB(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')


@attraction_bp.route('/getAttractionsCity',methods=['POST'])
def get_attractions_city():
    """
    获取景区城市数据
    :return:
    """
    post_res=db_set.get_attractions_city()
    return make_response(jsonify(post_res))


@attraction_bp.route('/getAttractionsLevel',methods=['POST'])
def get_attractions_level():
    """
    获取景区A级信息
    :return:
    """
    post_res=db_set.get_attraction_level()
    return make_response(jsonify(post_res))


@attraction_bp.route('/getAttractionsRange',methods=['POST'])
def get_attractions_range():
    """
    获取一定数值范围内的景点
    :return:
    """
    data=request.get_json()
    start=data.get('start')
    end=data.get('end')
    city=data.get('city')
    level=data.get('level')
    keyword=data.get('keyword')
    post_res=db_set.get_attractions_range(start,end,city,level,keyword)
    return make_response(jsonify(post_res))


@attraction_bp.route('/getAttractionsByID',methods=['POST'])
def get_attractions_by_id():
    """
    通过id获取景点细节信息
    :return:
    """
    data=request.get_json()
    attraction_id=data.get('id')
    post_res=db_set.get_attraction_by_id(attraction_id)
    return make_response(jsonify(post_res))


@attraction_bp.route('/addAttractionScore',methods=['POST'])
def add_attraction_score():
    """
    添加景点评分
    :return:
    """
    data=request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    attraction_id=data.get('attraction_id')
    score=data.get('score')
    post_res=db_set.add_attraction_score(account_id,identify,attraction_id,score)
    return make_response(jsonify(post_res))


@attraction_bp.route('/alterAttractionScore',methods=['POST'])
def alter_attraction_score():
    """
    修改景区评分
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    attraction_id = data.get('attraction_id')
    score = data.get('score')
    post_res=db_set.alter_attraction_score(account_id,identify,attraction_id,score)
    return make_response(jsonify(post_res))


@attraction_bp.route('/getMyAttractionScore',methods=['POST'])
def get_my_attraction_score():
    """
    获取某个用户在某个景区下的评分
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    attraction_id = data.get('attraction_id')
    post_res=db_set.get_user_attraction_score(account_id,identify,attraction_id)
    return make_response(jsonify(post_res))


@attraction_bp.route('/addAttractionComment',methods=['POST'])
def add_attraction_comment():
    """
    添加景点评论
    :return:
    """
    data=request.get_json()
    comment=data.get('comment')
    time=data.get('time')
    trump_count=data.get('trump_count')
    account_id=data.get('account_id')
    identify=data.get('identify')
    name=data.get('name')
    attraction_id=data.get('attraction_id')
    # print(comment,time,trump_count,account_id,identify,name,attraction_id)
    post_res=db_set.add_new_attraction_comment(comment,time,attraction_id,account_id,name,identify)
    return make_response(jsonify(post_res))


@attraction_bp.route('/alterAttractionComment',methods=['POST'])
def alter_attraction_comment():
    """
    修改景点评论
    :return:
    """
    data=request.get_json()
    comment_id=data.get('comment_id')
    comment_new=data.get('comment_new')
    post_res=db_set.alter_attraction_comment(comment_id,comment_new)
    return make_response(jsonify(post_res))


@attraction_bp.route('/removeAttractionCommentID',methods=['POST'])
def remove_attraction_comment_id():
    """
    通过景区评论id移除景点评论
    :return:
    """
    data=request.get_json()
    comment_id=data.get('comment_id')
    post_res=db_set.remove_attraction_comment_id(comment_id)
    return make_response(jsonify(post_res))


@attraction_bp.route('/removeAttractionCommentAccount',methods=['POST'])
def remove_attraction_comment_account():
    """
    通过用户账号移除景点评论
    :return:
    """
    data=request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    post_res=db_set.remove_attraction_comment_account(account_id,identify)
    return make_response(jsonify(post_res))


@attraction_bp.route('/getAttractionComments',methods=['POST'])
def get_attraction_comments():
    """
    获取某个景点下的所有评论信息
    :return:
    """
    data=request.get_json()
    attraction_id=data.get('attraction_id')
    post_res=db_set.get_attraction_comments(attraction_id)
    return make_response(jsonify(post_res))


@attraction_bp.route('/trumpAttractionComment',methods=['POST'])
def trump_attraction_comment():
    """
    点赞景点评论
    :return:
    """
    data=request.get_json()
    account_id=data.get('id')
    identify=data.get('identify')
    comment_id=data.get('comment_id')
    post_res=db_set.trump_attraction_comment(account_id,identify,comment_id)
    return make_response(jsonify(post_res))


@attraction_bp.route('/cancelTrumpAttractionComment',methods=['POST'])
def cancel_trump_attraction_comment():
    """
    取消景点点赞
    :return:
    """
    data = request.get_json()
    account_id = data.get('id')
    identify = data.get('identify')
    comment_id = data.get('comment_id')
    post_res=db_set.cancel_trump_attraction_comment(account_id,identify,comment_id)
    return make_response(jsonify(post_res))


@attraction_bp.route('/getMyAttractionTrumpComments',methods=['POST'])
def get_my_attraction_trump_comments():
    data=request.get_json()
    account_id=data.get('id')
    identify=data.get('identify')
    post_res=db_set.get_my_attraction_trump_comment(account_id,identify)
    return make_response(jsonify(post_res))


@attraction_bp.route('/uploadAttractionData',methods=['POST','GET'])
def upload_attraction_image():
    """
    上传景点描述、图片
    :return:
    """
    data=request.get_json()
    img=data.get('img')
    des=data.get('des')
    attraction_id=data.get('attraction_id')
    post_res=db_set.upload_attraction_des(attraction_id,des,img)
    return make_response(jsonify(post_res))


@attraction_bp.route('/getWordsCutAttractionComments',methods=["POST"])
def get_words_cut_attraction_comments():
    """
    获取景点评论的分词统计
    :return:
    """
    data = request.get_json()
    attraction_id=data.get("attraction_id")
    post_res=db_set.get_word_cut_attraction_by_id(attraction_id)
    return post_res

