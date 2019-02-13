from flask import Flask, render_template, request, redirect, url_for
import requests
import service
from datetime import datetime, timedelta

application = Flask(__name__)

# TODO
# 似ている日をいくつか例示するとさらによい？
# URLを環境変数に隠蔽したい
# しきい値可変にしたい
# デプロイなど

@application.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        input_date = request.form['date_field']
        target_date = validate_target_date(input_date)
        base_date = target_date - timedelta(days=1)

    elif request.method == 'GET':
        # 00:00:00に揃える
        target_date = datetime.strptime(datetime.today().strftime("%Y/%m/%d"), "%Y/%m/%d")
        base_date = target_date - timedelta(days=1)

    confidence_scores, predictions, local_paths = service.do_evaluate(base_date)

    evaluations = [
        {
            'time':       "9時",
            'timeframe':  "午前",
            'image_path': local_paths[0],
            'confidence': "{:.2f}".format( confidence_scores[0] ),
            'prediction':  predictions[0],
        },
        {
            'time':       "21時",
            'timeframe':  "午後",
            'image_path': local_paths[1],
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

if __name__ == '__main__':
    application.run()

