# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 数据库配置：数据库地址，关闭自动跟踪修改
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#创建数据库对象
db = SQLAlchemy(app)
'''
1 配置数据库
2 添加书和作者模型
3 添加数据
4 使用模板显示数据库查询结果
5 使用WTF显示表单
6 实现相关的增删逻辑
'''

# 定义书和作者模型
# 作者模型
class Author(db.Model):
    # 表名
    __tablename__ = 'authors'
    # 字段
    id = db.Column(db.Interger, primary_key=True)






@app.route('/', methods=['GET', 'POST'])
def home():
    return '<h1>Home</h1>'

@app.route('/signin', methods=['GET'])
def signin_form():
    return '''<form action="/signin" method="post">
              <p><input name="username"></p>
              <p><input name="password" type="password"></p>
              <p><button type="submit">Sign In</button></p>
              </form>'''

@app.route('/signin', methods=['POST'])
def signin():
    # 需要从request对象读取表单内容：
    if request.form['username']=='admin' and request.form['password']=='password':
        return '<h3>Hello, admin!</h3>'
    return '<h3>Bad username or password.</h3>'

if __name__ == '__main__':
    app.run()