from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session
import click

# 创建flask对象
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/movieDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

admin='孙大伟'
# 初始化数据库连接:
db = SQLAlchemy(app)

# 创建数据库不同表单模型
class MovieInfo(db.Model):
    __tablename__ = 'movie_info'

    movie_id=db.Column(db.String(10),primary_key=True)
    movie_name=db.Column(db.String(20),nullable=False)
    release_date=db.Column(db.DateTime)
    country=db.Column(db.String(20))
    type=db.Column(db.String(10))
    year=db.Column(db.Integer)

class MoveBox(db.Model):
    __tablename__ = 'move_box'

    movie_id=db.Column(db.String(10),db.ForeignKey('movie_info.movie_id'),primary_key=True)
    box=db.Column(db.Float)

class ActorInfo(db.Model):
    __tablename__ = 'actor_info'

    actor_id = db.Column(db.String(10), primary_key=True)
    actor_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(20))

class MovieActorRelation(db.Model):
    __tablename__ = 'movie_actor_relation'

    id = db.Column(db.String(10), primary_key=True)
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'), nullable=False)
    actor_id = db.Column(db.String(10), db.ForeignKey('actor_info.actor_id'), nullable=False)
    relation_type = db.Column(db.String(20))

##############################前端网页相关函数#############################
@app.route('/')
@app.route('/index/<int:page>')
def index(page=1):
    per_page=10#每页显示的数量
    pagination=MovieInfo.query.paginate(page=page,per_page=per_page,error_out=False)
    movies=pagination.items
    return render_template('index.html',name=admin,movies=movies,pagination=pagination)

@app.route('/add_movie')
def add_movie():

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('404.html', user=admin), 404

@app.route('/test_connection')
def test_connection():
    try:
        result=MovieInfo.query.first()
        if result is not None:
            return f'Successfully connected to database! first info is {result.movie_name}'
        else:
            return 'Successfully connected to database! But no data in database!'
    except Exception as e:
        return f"连接失败{e}"



