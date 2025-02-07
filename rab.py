import pika

# Параметры подключения
parameters = pika.URLParameters('amqp://admin:password@192.168.1.138:5672/myapp_vhost')

# Устанавливаем соединение
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Объявляем очередь
channel.queue_declare(queue='test_queue')

# Отправляем тестовое сообщение
channel.basic_publish(exchange='',
                      routing_key='test_queue',
                      body='Тестовое сообщение для RabbitMQ на Amvera')

print("Сообщение отправлено")

# Закрываем соединение
connection.close()
