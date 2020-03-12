from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)
api = Api(app)
# job_stores = {'jobs': SQLAlchemyJobStore(url='sqlite:///db/jobs.sqlite')}
scheduler = BackgroundScheduler(daemon=True, timezone='America/Bogota')
scheduler.add_jobstore('sqlalchemy', url='sqlite:///db/jobs.sqlite')
#
scheduler.start()


class ScheduleSetter(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        hour = None
        minute = None
        second = None
        if json_data['hour']:
            hour = json_data['hour']
        if json_data['minute']:
            minute = json_data['minute']
        if json_data['second']:
            if isinstance(json_data['second'], list):
                second = ','.join(str(x) for x in json_data['second'])
            else:
                second = json_data['second']
        scheduler.add_job(start_recorder, 'cron', name='test', hour=hour, minute=minute, second=second)
        result = jsonify(hour=hour, minute=minute, second=second)
        return result


class Test(Resource):
    def get(self):
        os.system('python test.py')
        # output = subprocess.run('python test.py', shell=True)
        # print(output.stdout.__str__())
        # print(output.stdout)
        return "ok"


class Stream(Resource):
    def get(self, ch=None):
        os.system('python stream.py &')
        return 'Streaming...'


class Schedule(Resource):
    def get(self):
        scheduler.print_jobs()
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append(f'{job.id} : {job.__str__()}')
        return jobs

    def post(self):
        request.get_data()
        json_data = request.get_json()
        cron_params = {}
        if json_data is not None:
            for param in json_data:
                if param == "camera":
                    continue
                cron_params[param] = json_data[param]
        if "camera" in json_data:
            json_data['camera'] = 1
        scheduler.add_job(start_recorder, 'cron', [json_data['camera']], name='test', kwargs=cron_params)
        return 'Scheduler have been set'

    def delete(self):
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append(f'Job {job.id} {job.name} was removed')
            scheduler.remove_job(job.id)
        return jobs


# Job functions
def start_recorder(channel=None):
    print('executing script...')
    os.system(f'python stream.py {channel} &')
    print('script executed')


# Main
api.add_resource(Schedule, '/schedule')
api.add_resource(Stream, '/stream')

if __name__ == '__main__':
    app.run(debug=True)
