from flask import Flask, render_template, request, redirect, url_for
import pickle
import requests
import subprocess
import os
from datetime import datetime, timedelta
from skimage import io

THRESHOLD = -0.96

app = Flask(__name__)
with open('./data/weather_nmf_nmf.pickle', 'rb') as fp:
    best_nmf = pickle.load(fp)

with open('./data/weather_nmf_svc.pickle', 'rb') as fp:
    best_svc = pickle.load(fp)


# TODO

# 似ている日をいくつか例示するとさらによい？
# モジュール化したい
# URLを環境変数に隠蔽したい
# デプロイなど

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_date = request.form['date_field']
        print(input_date)
        target_date = validate_target_date(input_date)
        base_date = target_date - timedelta(days=1)
    elif request.method == 'GET':
        # 00:00:00に揃える
        target_date = datetime.strptime(datetime.today().strftime("%Y/%m/%d"), "%Y/%m/%d")
        base_date = target_date - timedelta(days=1)
    else:
        return redirect(url_for('index'))

    date_str_am = image_path_for(base_date, '09')
    date_str_pm = image_path_for(base_date, '21')
    fetch_images_unless_exist(date_str_am, date_str_pm)


    images = [
      io.imread(build_target_path(date_str_am)),
      io.imread(build_target_path(date_str_pm))
    ]
    normalized_images = [image.ravel()/255. for image in images]

    target_nmf = best_nmf.transform(normalized_images)
    confidence_scores = best_svc.decision_function(target_nmf) - THRESHOLD
    predictions = [1 if score >= 0 else 0 for score in confidence_scores]

    evaluations = [
        {
            'time':       "9時",
            'timeframe':  "午前",
            'image_path': build_target_path(date_str_am),
            'confidence': "{:.2f}".format( confidence_scores[0] ),
            'prediction':  predictions[0],
        },
        {
            'time':       "21時",
            'timeframe':  "午後",
            'image_path': build_target_path(date_str_pm),
            'confidence': "{:.2f}".format( confidence_scores[1] ),
            'prediction':  predictions[1],
        }
    ]

    return render_template('index.html', target_date=target_date.strftime("%Y/%m/%d"), base_date=base_date.strftime("%Y/%m/%d"), evaluations=evaluations)

def validate_target_date(date=''): # TODO: 10時以降で翌日午前の予測が出るようにする
    today = datetime.today().strftime("%Y/%m/%d") # 00:00:00に揃える
    if date == '':
      date = today

    date  = datetime.strptime(date, "%Y/%m/%d")
    today = datetime.strptime(today, "%Y/%m/%d")
    if date > today:
      date = today
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

