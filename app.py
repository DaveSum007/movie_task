from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session
import click
from datetime import datetime

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

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        # 获取表单数据
        movie_id = request.form['movie_id']
        movie_name = request.form['movie_name']
        release_date_str = request.form['release_date']
        country = request.form['country']
        movie_type = request.form['type']
        year = request.form['year']
        box_office = request.form['box']
        actor_id = request.form['actor_id']
        actor_name = request.form['actor_name']
        gender = request.form['gender']
        actor_country = request.form['actor_country']
        relation_type = request.form['relation_type']

        # 转换日期格式
        release_date = datetime.strptime(release_date_str, '%Y-%m-%d') if release_date_str else None

        # 创建电影信息
        new_movie = MovieInfo(
            movie_id=movie_id,
            movie_name=movie_name,
            release_date=release_date,
            country=country,
            type=movie_type,
            year=year
        )
        db.session.add(new_movie)

        # 创建票房信息
        if box_office:
            new_box = MoveBox(
                movie_id=movie_id,
                box=float(box_office)
            )
            db.session.add(new_box)

        # 创建演员信息，假设每次只添加一位演员
        new_actor = ActorInfo(
            actor_id=actor_id,
            actor_name=actor_name,
            gender=gender,
            country=actor_country
        )
        db.session.add(new_actor)

        # 创建电影与演员的关系
        new_relation = MovieActorRelation(
            movie_id=movie_id,
            actor_id=actor_id,
            relation_type=relation_type
        )
        db.session.add(new_relation)

        # 提交到数据库
        db.session.commit()

        # 重定向回主页或确认页面
        flash('成功添加电影条目！')
        return redirect(url_for('index'))

    # 如果是 GET 请求，则渲染添加电影条目的页面
    return render_template('add_movie.html')

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



