from flask import Flask,jsonify,make_response,request
from attraction.attraction import attraction_bp
from hall.hall import hall_bp
from person.person import person_bp
from route.route import route_bp
from agency.agency import agency_bp
from flask_cors import CORS
from dbIO import MySQLClient

app = Flask(__name__)
CORS(app,resources=r'/*') # 解决跨域
app.register_blueprint(attraction_bp)
app.register_blueprint(hall_bp)
app.register_blueprint(person_bp)
app.register_blueprint(route_bp)
app.register_blueprint(agency_bp)
db_set=MySQLClient(host="localhost",port=3306,username='root',password='gx628572',database='sp_app_datasets')
# cookie保存的时间
cookie_time = 60*60*24


@app.route('/')
def hello_world():  # put application's code here
    with open("./static/dist/index.html") as file_html:
        page=file_html.read()
    return page


@app.route('/login',methods=['post'])
def login():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    identify = request.cookies.get('identify')
    # print(type(username),username)
    post_res=make_response()
    post_res.set_cookie("userid","",max_age=cookie_time)
    post_res.set_cookie("username",str(username),max_age=cookie_time)
    post_res.set_cookie("password",str(password),max_age=cookie_time)
    post_res.set_cookie("identify",str(identify),max_age=cookie_time)
    # 首先用cookie验证是否有登陆信息
    # cookie无登陆信息
    if username is None or password is None or identify is None or username=="None" or password =="None" or identify =="None":
        #        使用API接口参数
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')
        identify=data.get('identify')
        if username is not None or password is not None or identify is not None and username !="None" or password !="None" or identify !="None":
            check_res=db_set.login_check(username,password,identify)
            post_res=make_response(jsonify(check_res))
            if check_res['state']==1:
                # print(check_res['user']['id'])
                post_res.set_cookie('userid',str(check_res['user']['id']),max_age=cookie_time)
    else:
        # cookie有登录信息
        # print(username is None)
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


if __name__=="__main__":
    app.run(port=5260)
