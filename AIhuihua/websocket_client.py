import json
import pika
import uuid
import websocket
from config import config


class WebSocketProcessor:
    def __init__(self):
        self.ws = None
        self.prompt_id = None

    def connect_websocket(self, ws_url):
        print(ws_url)
        try:
            self.ws = websocket.create_connection(ws_url)
            print("WebSocket 连接成功")
        except Exception as e:
            print(f"尝试连接WebSocket失败: {e}")
            self.ws = None

    def listen_for_completion(self):
        while True:
            try:
                result = self.ws.recv()
                if isinstance(result, str):
                    data = json.loads(result)
                    print(data )
                    if data['type'] == 'status' and 'sid' not in data['data']:
                        if data['data']['status']['exec_info']['queue_remaining'] == 0:
                            self.notify_main_process()
            except websocket.WebSocketConnectionClosedException as e:
                print(f"WebSocket连接断开: {e}")
                break
            except TypeError as e:
                print(f"数据类型错误: {e}")
                self.ws = None
                break
            except Exception as e:
                print(f"监听WebSocket时发生错误: {e}")
                self.ws = None
                break

    def notify_main_process(self):
        # 通知主进程图片处理完成
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='image_processed')
        channel.basic_publish(exchange='', routing_key='image_processed', body='done')
        connection.close()

    def close_websocket(self):
        if self.ws:
            try:
                self.ws.close()
                print("WebSocket 连接已关闭")
            except Exception as e:
                print(f"关闭WebSocket时出错: {e}")
            finally:
                self.ws = None


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='uuid_queue')

    def callback(ch, method, properties, body):
        uuid = body.decode()
        ws_processor = WebSocketProcessor()
        ws_processor.connect_websocket(config["ws_url"] + uuid)
        ws_processor.listen_for_completion()
        ws_processor.close_websocket()

    channel.basic_consume(queue='uuid_queue', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for UUIDs. To exit press CTRL+C')
    channel.start_consuming()
