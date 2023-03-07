import cv2
from cv2 import dnn_superres
import uuid
import os

from flask import Flask
from flask import request
from flask.views import MethodView
from flask import jsonify
from celery import Celery
from celery.result import AsyncResult

app_name = 'upscale'
app = Flask(app_name)
app.config['UPLOAD_FOLDER'] = 'files'
celery = Celery(
    app_name,
    backend='redis://localhost:6379/1',
    broker='redis://localhost:6379/2'
)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

@celery.task()
def upscale_task(input_path='lama_300px.png', output_path='lama_600px.png', model_path: str = 'EDSR_x2.pb') -> None:
    """
    :param input_path: путь к изображению для апскейла
    :param output_path:  путь к выходному файлу
    :param model_path: путь к ИИ модели
    :return:
    """
    print('---in upscale---')
    print(f'{input_path}')
    print(f'{output_path}')

    scaler = dnn_superres.DnnSuperResImpl_create()
    scaler.readModel(model_path)
    scaler.setModel("edsr", 2)
    image = cv2.imread(input_path)
    result = scaler.upsample(image)
    cv2.imwrite(output_path, result)



class Upscale(MethodView):

    def post(self):
        image_pathes = [self.save_image(field) for field in ('image_in', 'image_out')]
        task = upscale_task.delay(input_path=image_pathes[0], output_path=image_pathes[1])
        return jsonify(
            {'task_id': task.id,
             'output_path': image_pathes[1]}
        )

    def save_image(self, field):
        image = request.files.get(field)
        print(f'image={image}')
        extension = image.filename.split('.')[-1]
        path = os.path.join('files', f'{uuid.uuid4()}.{extension}')
        # if not os.path.exists(path):
        #     os.makedirs('files')
        image.save(path)
        return path

class Tasks(MethodView):
    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status,
                        'result': task.result})

class Processed(MethodView):
    def get(self, file):
        status = 'ERROR'
        if file:
            status = 'SUCCESS'
        return jsonify({'status': status, 'result_path': os.path.join('files', f'{file}')})


upscale_view = Upscale.as_view('upscale')
tasks_view = Tasks.as_view('tasks')
processed_view = Processed.as_view('processed')

app.add_url_rule('/upscale/', view_func=upscale_view, methods=['POST'])
app.add_url_rule('/tasks/<string:task_id>', view_func=tasks_view, methods=['GET'])
app.add_url_rule('/processed/<string:file>', view_func=processed_view, methods=['GET'])


if __name__ == '__main__':
    app.run()
