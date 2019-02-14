from flask import Flask, render_template, request, redirect, url_for
import requests
import service
from datetime import datetime, timedelta

application = Flask(__name__)

# TODO
# 似ている日をいくつか例示するとさらによい？
# しきい値可変にしたい

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

def validate_target_date(date_str=''): # TODO: 10時以降で翌日午前の予測が出るようにする
    today         = datetime.today()
    latest_date   = datetime(today.year, today.month, today.day)
    earliest_date = datetime(2013,1,1)

    if date_str == '':
        date = latest_date
    else:
        date  = datetime.strptime(date_str, "%Y/%m/%d")

    if date < earliest_date:
        date = earliest_date
    if date > latest_date:
        date = earliest_date

    return date

if __name__ == '__main__':
    application.run()

