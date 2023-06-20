# coding: utf-8

from flask import Blueprint,make_response,request,jsonify
from route.route_database import RouteDb


route_bp=Blueprint("route",__name__,url_prefix="")
db_set=RouteDb(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')


@route_bp.route('/getRoutesByAccountID',methods=['POST'])
def get_routes_account_id():
    """
    根据用户id获取路线数据
    :return:
    """
    data = request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    post_res=db_set.get_routes_by_userid(account_id,identify)
    return make_response(jsonify(post_res))


@route_bp.route('/addNewRoute',methods=['POST'])
def add_new_route():
    """
    添加新的路线
    :return:
    """
    data=request.get_json()
    account_id=data.get('account_id')
    identify=data.get('identify')
    route_name=data.get('route_name')
    route=data.get('route')
    start=data.get('start')
    line=data.get('line')
    post_res=db_set.add_new_route(account_id,identify,name=route_name,route=route,start=start,line=line)
    return make_response(jsonify(post_res))


@route_bp.route("/updateRouteAttractions",methods=['POST'])
def update_route_attractions():
    """
    更新路线上的景点信息
    :return:
    """
    data = request.get_json()
    route_id=data.get("route_id")
    route_attractions=data.get('attractions')
    post_res=db_set.update_route_attractions(route_id,route_attractions)
    return make_response(jsonify(post_res))


@route_bp.route('/addRouteStart',methods=['POST'])
def add_route_start():
    """
    添加路线的起点
    :return:
    """
    data = request.get_json()
    route_id=data.get('route_id')
    route_start=data.get('route_start')
    post_res=db_set.add_route_start(route_id,route_start)
    return make_response(jsonify(post_res))


