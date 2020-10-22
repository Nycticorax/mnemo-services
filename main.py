import requests
from flask import Flask, request, jsonify
from jobs import Jobs

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

def job_done(**payload):
    """ calling back webhook with payload"""
    payload["services"] = "job queued"
    print('sending request to webhook...', str(payload))
    response = requests.post('https://us-central1-telegram-bots-000.cloudfunctions.net/webhook', json=payload)
    if response:
        print('response from webhook', str(response))
        return

@app.route('/schedule', methods=['GET','POST'])
def schedule():
    if request.method == 'GET':
        return 'Sorry I only do POST requests.'
    elif request.method =='POST':
        data = request.get_json()
        if "services" in data:
            print('Spit out by webhook without change!')
            return 
        job_blueprint = data['job_blueprint']
        if job_blueprint['type'] != 'abs':
            Jobs.add(int(job_blueprint['time']), job_done, data, _abs=False)
            return jsonify('Thanks, calling back in a couple of seconds (' + job_blueprint['time'] + ')')
        else:
            sched_time = Jobs.makeSchedTime(job_blueprint['time'])
            if sched_time:
                Jobs.add(sched_time, job_done, data)
                return jsonify('Thanks, calling back @', job_blueprint['time'])

@app.route('/unschedule/<unscheduleToken>', methods=['POST'])
def unschedule(unscheduleToken):
    return


@app.route('/healthcheck', methods=['POST'])
def healthcheck():
    if request.method == 'POST':
        res = len(list(Jobs.jobs_queue.queue))
        return jsonify(str(res))

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]