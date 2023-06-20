# coding: utf-8

from flask import Blueprint,make_response,request,jsonify
from route.database import RouteDb


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


