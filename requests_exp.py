import requests
import base64
import time
import urllib.request


# resp = requests.post('http://127.0.0.1:5000/upscale', files={
#     'image_in': open('lama_300px.png', 'rb'),
#     'image_out': open('lama_600px.png', 'rb')
# })
#
# resp_data = resp.json()
# print(resp_data)
# task_id = resp_data.get('task_id')
# output_path = resp_data.get('output_path')
# print(task_id)

task_id = '1d6c1a15-82e9-4ef0-ba3f-6566ed9a77d3'
output_path = 'files/95ec52dc-b5ee-472c-b902-0644132a2798.png'
output_file = '95ec52dc-b5ee-472c-b902-0644132a2798.png'
resp = requests.get(f'http://127.0.0.1:5000/tasks/{task_id}')
print(resp.json())

status_pic = resp.json()['status']

if status_pic == 'SUCCESS':
    resp_file = requests.get(f'http://127.0.0.1:5000/processed/{output_file}')
    print(resp_file.json())
