from flask import Flask, request
from flask_restful import Resource, Api
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)
api = Api(app)
scheduler = BackgroundScheduler(daemon=True, timezone='America/Bogota')
scheduler.add_jobstore('sqlalchemy', url='sqlite:///db/jobs.sqlite')
scheduler.start()


class Stream(Resource):
    def get(self, ch=None):
        os.system('python stream.py &')
        return 'Streaming...'


class Index(Resource):
    def get(self):
        return 'Running...'


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
                if param == "camera" or json_data[param] is None:
                    continue
                cron_params[param] = json_data[param]
        if "camera" not in json_data:
            json_data['camera'] = 1
        print(type(cron_params))
        # scheduler.add
        scheduler.add_job(start_recorder, 'cron', [json_data['camera']], **cron_params)
        return 'Scheduler have been set'

    def delete(self):
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append(f'Job {job.id} {job.name} was removed')
            scheduler.remove_job(job.id)
        return jobs


# Job functions
def start_recorder(channel=None):
    for channel in range(4):
        print('executing script...')
        os.system(f'python stream.py {channel} &')
        print('script executed')


# Main
api.add_resource(Schedule, '/schedule')
api.add_resource(Stream, '/stream')
api.add_resource(Index, '/')

if __name__ == '__main__':
    app.run(debug=True)
