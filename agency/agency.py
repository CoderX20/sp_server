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

