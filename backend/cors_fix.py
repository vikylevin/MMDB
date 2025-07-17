from flask_cors import CORS

# 在app.py中导入这个文件
# 在创建app后添加：
# from cors_fix import add_cors
# add_cors(app)

def add_cors(app):
    CORS(app, resources={
        r"/*": {
            "origins": "*"
        }
    })

    # 添加CORS头的另一种方法
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
