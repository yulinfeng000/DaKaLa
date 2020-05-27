import time

from flask import Flask, request, render_template, Response
import userdb
from daka import dakala
import threading
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

app = Flask(__name__, static_folder='./static')
http_server = HTTPServer(WSGIContainer(app), xheaders=True)


@app.route('/', methods=['GET'])
def hello_world():
    cok = request.cookies
    stuid = cok.get("stuid")

    if stuid is None:
        return render_template('index.html')
    else:
        return render_template('info.html', stuid=stuid)


@app.route("/register", methods=['POST'])
def register():
    required = ['stuid', 'password', 'cityStatus', 'workingPlace', 'healthStatus', 'livingStatus', 'homeStatus']
    values = request.form
    if not all(k in values for k in required):
        return 'Missing values', 403
    stuid = values.get('stuid')
    password = values.get('password')
    config = {
        'homeStatus': values.get('homeStatus'),
        'livingStatus': values.get('livingStatus'),
        'healthStatus': values.get('healthStatus'),
        'workingPlace': values.get('workingPlace'),
        'cityStatus': values.get('cityStatus')
    }
    userdb.db_put_user_info(stuid, password)
    userdb.db_put_user_config(stuid, config)

    resp = Response(render_template('success.html'))
    resp.set_cookie("stuid", stuid)
    return resp


@app.route('/delete', methods=['POST'])
def del_info():
    required = ['stuid']
    values = request.form
    if not all(k in values for k in required):
        return 'Missing values', 403
    stuid = values.get('stuid')
    userdb.delete(stuid)
    resp = Response("<h1>delete success</h1>")
    resp.delete_cookie("stuid")
    return resp, 200


@app.route('/photo/<stuid>', methods=['GET'])
def photo(stuid):
    vc_path = f'{stuid}_img.png'
    return render_template('photo.html', img_src=vc_path)


def daka_worker(stuid):
    print("打卡中", stuid)
    student = userdb.db_get_user_by_stuid(stuid)
    config = userdb.db_get_user_config(stuid)
    dakala(student, config)


@app.route('/daka/nophoto/<stuid>', methods=['GET'])
def dakanophoto(stuid):
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    return "打卡成功", 200


@app.route('/daka/<stuid>', methods=['GET'])
def daka(stuid):
    t1 = threading.Thread(target=daka_worker, args=(stuid,), daemon=True)
    t1.start()
    while t1.is_alive():
        time.sleep(2)

    return photo(stuid), 200


if __name__ == '__main__':
    http_server.listen(5000, "0.0.0.0")
    IOLoop.instance().start()
