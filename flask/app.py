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


# TODO
# routing 整理する
# しきい値をいい感じにする(-0.9x程度？、またはrecall/precisionを表示？）
# 現状だと、決定関数の値に+0.96足すといい感じ

# 基準日に対して、翌日の午前午後の推定であることを明示する
# 似ている日をいくつか例示するとさらによい？
# モジュール化したい
# 教育研究用であることを明記
# URLを環境変数に隠蔽したい
# デプロイなど

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
        target_date = request.form['date_field']
        target_date = validate_target_date(target_date)

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

        images = [
          io.imread(build_target_path(date_str_am)),
          io.imread(build_target_path(date_str_pm))
        ]
        normalized_images = [image.ravel()/255. for image in images]

        target_nmf = best_nmf.transform(normalized_images)
        target_pred = best_svc.predict(target_nmf)
        decision_data = best_svc.decision_function(target_nmf)

        return render_template('index.html', title=title, predictions=target_pred, decision_data=decision_data, image_paths=image_paths)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return redirect(url_for('index'))

def validate_target_date(date=''): # TODO: 10時以降で翌日午前の予測が出るようにする
    today = datetime.today().strftime("%Y/%m/%d") # 00:00:00に揃える
    if date == '':
      date = today

    date  = datetime.strptime(date, "%Y/%m/%d")
    today = datetime.strptime(today, "%Y/%m/%d")
    if date >= today:
      date = today - timedelta(days=1)
    return date

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

