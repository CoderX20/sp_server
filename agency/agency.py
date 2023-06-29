# coding:utf-8

from flask import Blueprint,request,make_response,jsonify
from agency.agency_database import AgencyDB


agency_bp=Blueprint("agency",__name__,url_prefix="")
db_set=AgencyDB(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')


@agency_bp.route('/getHotAgency',methods=["POST"])
def get_hot_agency():
    """
    获取热门推荐的旅行社
    :return:
    """
    post_res=db_set.get_hot_agency()
    return make_response(jsonify(post_res))


@agency_bp.route('/getAgencySearch',methods=["POST"])
def get_agency_search():
    """
    根据前端搜索要求返回搜索结果
    :return:
    """
    data=request.get_json()
    city=data.get('city')
    keyword=data.get('keyword')
    start=data.get('start')
    end=data.get('end')
    post_res=db_set.get_agency_by_city(city,keyword,start,end)
    return make_response(jsonify(post_res))


@agency_bp.route('/getAgencyID',methods=['POST'])
def get_agency_id():
    """
    根据id获取旅行社数据
    :return:
    """
    data=request.get_json()
    agency_id=data.get('agency_id')
    post_res=db_set.get_agency_by_id(agency_id)
    return make_response(jsonify(post_res))


@agency_bp.route('/getMyAgencyScore',methods=['POST'])
def get_my_agency_score():
    """
    获取当前用户的旅行社评分
    :return:
    """
    data=request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    agency_id=data.get('agency_id')
    post_res=db_set.get_my_agency_score(account_id,identify,agency_id)
    return make_response(jsonify(post_res))


@agency_bp.route('/addAgencyScore',methods=['POST'])
def add_agency_score():
    """
    添加旅行社评分
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    agency_id = data.get('agency_id')
    score=data.get('score')
    post_res=db_set.add_agency_score(account_id,identify,agency_id,score)
    return make_response(jsonify(post_res))


@agency_bp.route('/alterAgencyScore',methods=['POST'])
def alter_agency_score():
    """
    修改旅行社评分数据
    :return:
    """
    data = request.get_json()
    account_id = data.get('account_id')
    identify = data.get('identify')
    agency_id = data.get('agency_id')
    score = data.get('score')
    post_res=db_set.alter_agency_score(account_id,identify,agency_id,score)
    return make_response(jsonify(post_res))


@agency_bp.route('/getAgencyAttractions',methods=['POST'])
def get_agency_attractions():
    """
    获取旅行社所代理的景点
    :return:
    """
    data=request.get_json()
    agency_id=data.get("agency_id")
    post_res=db_set.get_agency_attractions(agency_id)
    return make_response(jsonify(post_res))


@agency_bp.route('/setAgencyRoutes',methods=['GET'])
def set_agency_routes():
    """
    设置旅行社路线
    :return:
    """
    return db_set.set_agency_attractions()


@agency_bp.route('/addNewOrder',methods=['POST'])
def add_new_order():
    """
    添加新的订单
    :return:
    """
    data=request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    route=data.get('route')
    agency_id=data.get('agency_id')
    price=data.get('price')
    add_time=data.get('add_time')
    post_res=db_set.add_new_order(account_id,identify,route,agency_id,price,add_time)
    return make_response(jsonify(post_res))

