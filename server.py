from flask import Flask, request, make_response, render_template
from flask_restful import Resource, Api
from apscheduler.schedulers.background import BackgroundScheduler
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import os
import json
import subprocess

app = Flask(__name__)
api = Api(app)
scheduler = BackgroundScheduler(daemon=True, timezone='America/Bogota')
scheduler.add_jobstore('sqlalchemy', url='sqlite:///db/jobs.sqlite')
scheduler.start()


class Update(Resource):
    def get(self):
        subprocess.Popen(['python', 'updater.py'])
        return 'Updating...'


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
        scheduler.add_job(start_recorder, 'cron', [json_data['camera']], **cron_params)
        return 'Scheduler have been set'

    def delete(self):
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append(f'Job {job.id} {job.name} was removed')
            scheduler.remove_job(job.id)
        return jobs


class Files(Resource):
    def get(self, req_path=''):
        headers = {'Content-Type': 'text/html'}
        root_dir = os.getcwd()
        # Joining the base and the requested path
        abs_path = os.path.join(root_dir, req_path)

        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return 'This file doesn\'t exists'

        # Check if path is a file and serve
        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            name = os.path.basename(abs_path)
            print(name)
            with open(f'{abs_path}') as file:
                content = file.read()
                content = highlight(content, PythonLexer(), HtmlFormatter())
                css = HtmlFormatter().get_style_defs('.highlight')
            return make_response(render_template('file.html', name=name, content=content, css=css), 200, headers)

        # Show directory contents
        files = [os.path.join(req_path, x) for x in os.listdir(abs_path)]
        file_list = []
        for file in files:
            data = {
                "path": file,
                "name": os.path.basename(file)
            }
            file_list.append(data)
        parent = os.path.basename(abs_path)
        print('parent ', parent)
        return make_response(render_template('browse.html', files=file_list, parent=parent), 200, headers)


# Job functions
def start_recorder():
    for channel in range(4):
        print('executing script...')
        subprocess.Popen(['python', 'recorder.py', f'{channel}'])
        print('script executed')


# Main
api.add_resource(Schedule, '/schedule')
api.add_resource(Files, '/files', '/files/<path:req_path>')
api.add_resource(Index, '/')

if __name__ == '__main__':
    app.run(debug=True)
