from flask import Flask,jsonify,make_response,request
from flask_cors import CORS
from dbIO import MySQLClient,MessageNew

app = Flask(__name__)
CORS(app,resources=r'/*') # 解决跨域
db_set=MySQLClient(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')
# cookie保存的时间
cookie_time = 60*60*24


@app.route('/')
def hello_world():  # put application's code here
    return


@app.route('/login',methods=['post'])
def login():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    identify = request.cookies.get('identify')
    post_res=make_response()
    post_res.set_cookie("userid","",max_age=cookie_time)
    post_res.set_cookie("username",str(username),max_age=cookie_time)
    post_res.set_cookie("password",str(password),max_age=cookie_time)
    post_res.set_cookie("identify",str(identify),max_age=cookie_time)
    # 首先用cookie验证是否有登陆信息
    # cookie无登陆信息
    if username is None or password is None or identify is None:
        #        使用API接口参数
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')
        identify=data.get('identify')
        if username is not None or password is not None or identify is not None:
            check_res=db_set.login_check(username,password,identify)
            post_res=make_response(jsonify(check_res))
            if check_res['state']==1:
                # print(check_res['user']['id'])
                post_res.set_cookie('userid',str(check_res['user']['id']),max_age=cookie_time)
    else:
        # cookie有登录信息
        check_res=db_set.login_check(username,password,identify)
        post_res=make_response(jsonify(check_res))
        if check_res['state']==1:
            post_res.set_cookie('userid',str(check_res['user']['id']),max_age=cookie_time)
    return post_res


@app.route('/register',methods=['POST'])
def register():
    """新用户注册"""
    data=request.get_json()
    username=data.get('username')
    password=data.get('password')
    post_res = make_response()
    post_res.set_cookie("userid", "", max_age=cookie_time)
    post_res.set_cookie("username", str(username), max_age=cookie_time)
    post_res.set_cookie("password", str(password), max_age=cookie_time)
    post_res.set_cookie("identify", "users", max_age=cookie_time)
    register_res=db_set.register_user(username,password)
    if register_res['state']==1:
        post_res.set_cookie("userid",str(register_res['user']['id']),max_age=cookie_time)
    return register_res


@app.route('/getMessages',methods=['POST'])
def get_message():
    """
    获取大厅留言信息
    :return:
    """
    data_get=make_response(jsonify(db_set.get_messages()))
    return data_get


@app.route('/addMessage',methods=['POST'])
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


@app.route('/popMessage',methods=['POST'])
def pop_message():
    """
    删除某一个大厅发言
    :return:
    """
    data=request.get_json()
    message_id=data.get('id')
    pop_res=db_set.pop_message(message_id)
    return make_response(jsonify(pop_res))


@app.route('/getTrumpData',methods=['POST'])
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


@app.route('/trumpHallMessage',methods=['POST'])
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


@app.route('/cancelTrumpHallMessage',methods=['POST'])
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


@app.route('/alterName',methods=['POST'])
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


@app.route("/delMyAccount",methods=['POST'])
def del_account():
    """
    删除账户
    """
    data=request.get_json()
    userid=data.get('id')
    identify=data.get('identify')
    post_res=db_set.del_account(userid=userid,identify=identify,username="")
    return make_response(jsonify(post_res))


@app.route('/alterPassword',methods=["POST"])
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


@app.route('/getMyHallMessages',methods=['POST'])
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


@app.route('/editHallMessage',methods=["POST"])
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


@app.route('/getAttractionsCity',methods=['POST'])
def get_attractions_city():
    """
    获取景区城市数据
    :return:
    """
    post_res=db_set.get_attractions_city()
    return make_response(jsonify(post_res))


@app.route('/getAttractionsLevel',methods=['POST'])
def get_attractions_level():
    """
    获取景区A级信息
    :return:
    """
    post_res=db_set.get_attraction_level()
    return make_response(jsonify(post_res))


@app.route('/getAttractionsRange',methods=['POST'])
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


@app.route('/getAttractionsByID',methods=['POST'])
def get_attractions_by_id():
    """
    通过id获取景点细节信息
    :return:
    """
    data=request.get_json()
    attraction_id=data.get('id')
    post_res=db_set.get_attraction_by_id(attraction_id)
    return make_response(jsonify(post_res))


@app.route('/addAttractionScore',methods=['POST'])
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


@app.route('/alterAttractionScore',methods=['POST'])
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


@app.route('/getMyAttractionScore',methods=['POST'])
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


@app.route('/addAttractionComment',methods=['POST'])
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


@app.route('/alterAttractionComment',methods=['POST'])
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


@app.route('/removeAttractionCommentID',methods=['POST'])
def remove_attraction_comment_id():
    """
    通过景区评论id移除景点评论
    :return:
    """
    data=request.get_json()
    comment_id=data.get('comment_id')
    post_res=db_set.remove_attraction_comment_id(comment_id)
    return make_response(jsonify(post_res))


@app.route('/removeAttractionCommentAccount',methods=['POST'])
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


@app.route('/getAttractionComments',methods=['POST'])
def get_attraction_comments():
    """
    获取某个景点下的所有评论信息
    :return:
    """
    data=request.get_json()
    attraction_id=data.get('attraction_id')
    post_res=db_set.get_attraction_comments(attraction_id)
    return make_response(jsonify(post_res))


@app.route('/trumpAttractionComment',methods=['POST'])
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


@app.route('/cancelTrumpAttractionComment',methods=['POST'])
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


@app.route('/getMyAttractionTrumpComments',methods=['POST'])
def get_my_attraction_trump_comments():
    data=request.get_json()
    account_id=data.get('id')
    identify=data.get('identify')
    post_res=db_set.get_my_attraction_trump_comment(account_id,identify)
    return make_response(jsonify(post_res))


@app.route('/uploadAttractionData',methods=['POST','GET'])
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


@app.route('/getWordsCutAttractionComments',methods=["POST"])
def get_words_cut_attraction_comments():
    """
    获取景点评论的分词统计
    :return:
    """
    data = request.get_json()
    attraction_id=data.get("attraction_id")
    post_res=db_set.get_word_cut_attraction_by_id(attraction_id)
    return post_res


@app.route('/getRoutesByAccountID',methods=['POST'])
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


@app.route('/addNewRoute',methods=['POST'])
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


@app.route('/alterAccountAvatar',methods=['POST'])
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


@app.route('/getAllMyAttractionComments',methods=['POST'])
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


@app.route('/registerAdmin',methods=["POST"])
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


if __name__=="__main__":
    app.run(port=5260)
