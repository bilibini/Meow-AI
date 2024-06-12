from flask import Blueprint,render_template

ext1 = Blueprint('wechat', __name__,static_folder='static',template_folder='templates',url_prefix='/wechat')

@ext1.route('/')
def index():
    return render_template('mai_wechat/index.html')