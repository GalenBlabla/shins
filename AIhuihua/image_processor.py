import os.path

import requests
import json
import random
import pika
from pathlib import Path
from requests_toolbelt.multipart.encoder import MultipartEncoder
from config import config


class ImageProcessor:
    def __init__(self, base_url, proxy_url=None):
        self.base_url = base_url
        self.proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        self.image_name_server = None
        self.prompt_id = None

    def upload_image(self, image_path):
        url = f"{self.base_url}/upload/image"
        filename = image_path.name
        try:
            with open(image_path, 'rb') as file:
                m = MultipartEncoder(
                    fields={'image': (filename, file, 'image/png')}
                )
                response = requests.post(url, data=m, headers={'Content-Type': m.content_type}, proxies=self.proxies)
                if response.status_code == 200:
                    self.image_name_server = response.json()['name']
                    print('Image uploaded successfully', response.json())
                else:
                    print('Failed to upload image', response.status_code, response.text)
                    return None
        except Exception as e:
            print(f'Error: {e}')
            return None
        return self.image_name_server

    def queue_prompt(self, prompt_workflow):
        if self.image_name_server is None:
            print("请先上传一张照片和选择风格")
            return None

        try:
            request_data = json.dumps({"prompt": prompt_workflow})
            response = requests.post(
                f"{self.base_url}/prompt",
                data=request_data,
                headers={'Content-Type': 'application/json'},
                proxies=self.proxies
            )
            if response.status_code == 200:
                self.prompt_id = response.json()['prompt_id']
                print(self.prompt_id)
                return self.prompt_id
            else:
                print('Failed to make the API request')
                return None
        except Exception as e:
            print(f'Exception: {e}')
            return None

    def get_images(self):
        if self.prompt_id is None:
            print("No prompt ID available to fetch images.")
            return []

        response = requests.get(f"{self.base_url}/history/{self.prompt_id}")
        data = response.json()
        if not data:
            return []
        images_data = []
        outputs = data[self.prompt_id]['outputs']

        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = self.get_server_image(image['filename'], image['subfolder'], image['type'])
                    if image_data:
                        images_data.append(image_data)
        return images_data

    def get_server_image(self, filename, subfolder, image_type):
        url = f"{self.base_url}/view?filename={filename}&subfolder={subfolder}&type={image_type}"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            image_data = response.content
            if not os.path.exists('output'):
                os.makedirs('output')
            with open(f"output/{filename}", "wb") as f:
                f.write(image_data)
            print("Image retrieved successfully")
            return image_data
        else:
            print("Failed to load image")
            return None

    def wait_for_image_processed_signal(self):
        # 等待 WebSocket 通信程序发送的处理完成信号
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='image_processed')

        def callback(ch, method, properties, body):
            if body.decode() == 'done':
                ch.stop_consuming()

        channel.basic_consume(queue='image_processed', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
        connection.close()

