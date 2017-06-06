# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask, request, render_template,\
     redirect, url_for, send_file,flash

from models import File, Text
from ext import db
from config import logger

import os
from gevent import monkey; monkey.patch_all()
from gevent import pywsgi

import win32api
import win32print


app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
ONE_DAY = 24 * 60 * 60

def prt_file(filename):
    win32api.ShellExecute (
      0,
      "print",
      filename,
      #
      # If this is None, the default printer will
      # be used anyway.
      #
      '/d:"%s"' % win32print.GetDefaultPrinter (),
      ".",
      0
    )

@app.route('/print/<filename>')
def prt(filename):
    dirname = os.path.dirname(__file__) + '/files/'
    file = dirname + filename
    try:
        prt_file(file)
        flash('正在打印文件：{}'.format(filename))
    except Exception as e:
        logger.error(e)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if not request.files['file'].filename:
        flash(u'请上传文件')
        return redirect(url_for('index'))

    f = request.files['file']
    files = [file.name for file in File.query.all()]
    if f.filename in files:
        flash(u'文件已存在, 直接下载')
        return redirect(url_for('index'))

    # 将文件存至服务器
    dirname = os.path.join(os.path.dirname(__file__), 'files')
    try:
        f.save(os.path.join(dirname, f.filename))
    except Exception as e:
        logger.error(e)
        return redirect(url_for('index'))
    # 将信息存入数据库
    file = File(name=f.filename, size=request.content_length)
    try:
        db.session.add(file)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/text', methods=['POST'])
def text():
    text = request.form.get('text', None)
    if not text:
        flash('没有文本，请重试')

    # 将信息存入数据库
    text = Text(content=text)
    try:
        db.session.add(text)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/')
def index():
    files = File.query.all()
    for file in files:
        file.url = ''.join(['download/', file.name])
        file.delete_url = ''.join(['delete/', file.name])
        file.prt_url = ''.join(['print/', file.name])

    texts = Text.query.all()
    return render_template('index.html', files=files, texts=texts)

@app.route('/download/<filename>')
def download(filename):
    dirname = os.path.join(os.path.dirname(__file__), 'files')
    file = os.path.join(dirname, filename)
    try:
        return send_file(open(file, 'rb'),
                     mimetype='application/octet-stream',
                     cache_timeout=ONE_DAY,
                     as_attachment=True,
                     attachment_filename=filename)
    except Exception as e:
        logger.error(e)
        return redirect(url_for('index'))


@app.route('/delete/<filename>')
def delete(filename):
    dirname = os.path.join(os.path.dirname(__file__), 'files')
    file = os.path.join(dirname, filename)
    try:
        os.unlink(file)
        file = File.query.filter_by(name=filename).first()
        db.session.delete(file)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        return redirect(url_for('index'))

    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    pywsgi.WSGIServer(('0.0.0.0', 5000), app).serve_forever()

