#CONFIG DLYA SOFTA

timeout = 1 #таймауты между сообщениями или пачками сообщений. Рекомендуется - 1
proxy = {
    'proxy_type': 'SOCKS5', # только SOCKS5 proxy!!!
    'addr': '',
    'port': 12345,
    'username': '',  # если требуется аутентификация на прокси
    'password': ''  # если требуется аутентификация на прокси
}

message_text = "Hi there!" # текст для рассылки
channel_link = "t.me/" #сюда вставить t.me если рассылка будет с постов канала, message_text можно не удалять

sema = 1 #кол-во диалогов для отправки в секунду (пачкой)
