from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session
import click
from datetime import datetime

# 创建flask对象
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/movieDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key='123456'
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

@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    # 查询电影信息
    movie = MovieInfo.query.get_or_404(movie_id)

    # 查询电影的票房信息
    box = MoveBox.query.filter_by(movie_id=movie_id).first()

    # 查询与电影相关的演员信息
    actor_relations = db.session.query(MovieActorRelation, ActorInfo).join(ActorInfo, MovieActorRelation.actor_id == ActorInfo.actor_id).filter(MovieActorRelation.movie_id == movie_id).all()

    # 将查询结果传递给模板
    return render_template('movie_detail.html', movie=movie, box=box, actor_relations=actor_relations)

@app.route('/search_movie', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        actor_name = request.form.get('actor_name')
        release_date = request.form.get('release_date')

        # 根据输入信息构建查询
        query = db.session.query(MovieInfo)
        if movie_name:
            query = query.filter(MovieInfo.movie_name.like(f'%{movie_name}%'))
        if actor_name:
            query = query.join(MovieActorRelation, MovieInfo.movie_id == MovieActorRelation.movie_id)\
                         .join(ActorInfo, ActorInfo.actor_id == MovieActorRelation.actor_id)\
                         .filter(ActorInfo.actor_name.like(f'%{actor_name}%'))
        if release_date:
            query = query.filter(MovieInfo.release_date == release_date)

        results = query.all()
        return render_template('search_results.html', movies=results)

    return render_template('search_movie.html')

@app.route('/search_actor', methods=['GET', 'POST'])
def search_actor():
    if request.method == 'POST':
        movie_names = request.form.get('movie_names').split(' ')
        movie_names = [name.strip() for name in movie_names]

        # 查询出演了所有这些电影的演员
        actors = db.session.query(ActorInfo)\
            .join(MovieActorRelation, ActorInfo.actor_id == MovieActorRelation.actor_id)\
            .join(MovieInfo, MovieInfo.movie_id == MovieActorRelation.movie_id)\
            .filter(MovieInfo.movie_name.in_(movie_names))\
            .group_by(ActorInfo.actor_id)\
            .having(db.func.count(MovieInfo.movie_id) == len(movie_names))\
            .all()

        return render_template('actor_results.html', actors=actors)

    return render_template('search_actor.html')

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('404.html', user=admin), 404





