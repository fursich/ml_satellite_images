from flask import Flask, render_template, request, redirect, url_for
import pickle
import requests
import subprocess
import os
from datetime import datetime, timedelta
from skimage import io

app = Flask(__name__)
with open('./data/weather_nmf_nmf.pickle', 'rb') as fp:
    best_nmf = pickle.load(fp)

with open('./data/weather_nmf_svc.pickle', 'rb') as fp:
    best_svc = pickle.load(fp)

@app.route('/')
def hello_world():
    title = "ようこそ"
    message = '名前を入れてください'
    # index.html をレンダリングする
    return render_template('index.html',
                           message=message, title=title)

@app.route('/post', methods=['GET', 'POST'])
def post():
    title = "こんにちは"
    if request.method == 'POST':
        current     = datetime.today()
        target_date = calculate_target_date(current)

        date_str_am = image_path_for(target_date, '09')
        date_str_pm = image_path_for(target_date, '21')
        fetch_images_unless_exist(date_str_am, date_str_pm)

        image_paths = [
            {
                'time': date_str_am,
                'path': build_target_path(date_str_am),
            },
            {
                'time': date_str_pm,
                'path': build_target_path(date_str_pm),
            }
        ]

        image = io.imread(build_target_path(date_str_am))
        print(build_target_path(date_str_am))
        normalized_image = image/255.
        X_nmf = best_nmf.transform(normalized_image)
        X_pred = best_svc.predict(X_nmf)
        print(X_pred)

        name = request.form['name']
        # index.html をレンダリングする
        return render_template('index.html',
                               name=name, title=title, image_paths=image_paths)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return redirect(url_for('index'))

def calculate_target_date(current): # TODO: 10時以降で翌日午前の予測が出るようにする
    if current.hour <= 22: # 21時の衛星画像が入る時刻（決め打ち）
      current -= timedelta(days=1)
    return current

def image_path_for(target_date, hour):
    return target_date.strftime(f'%Y/%m/%d/{hour}/00/00')

def fetch_images_unless_exist(*date_str):
    for date in date_str:
      target_path = build_target_path(date)
      if not os.path.exists(target_path):
        url = build_image_url(date)
        run(convert_command(url, target_path))

def build_image_url(date_str):
    return f"https://storage.tenki.jp/archive/satellite/{date_str}/japan-near-small.jpg"

def convert_args():
    return " -shave 20x20 -colorspace linear-gray"
    # colorspaces "linear-gray" are only available after ImageMagick 7.0.7-17

def convert_command(url, target_path):
    return f"convert {convert_args()} '{url}' '{target_path}'"

def build_target_path(date_str):
    filename = date_str.replace('/','_')
    return f"static/{filename}.jpg"

def run(cmd):
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    app.run()

