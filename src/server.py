#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Modified by Anna Suvorova
#  reg.tobit@gmail.com
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class Handler(LineOnlyReceiver):
    """
    Класс для обработки подключений клиентов
    """

    factory: 'Server'  # свойство для доступа к серверу (фабрике)
    login: str  # тут мы будем хранить логин клиента (при успешном получении команды login:USER_LOGIN)

    def connectionLost(self, reason=connectionDone):
        """
        Метод для обработки отключения клиента (разрыв соединения, ручное отключение)
        :param reason:
        :return:
        """
        self.factory.clients.remove(self)  # удаляем клиента из списка подключенных
        print("Disconnected"+self.login)  # выводим в терминал сообщение об отключении

    def connectionMade(self):
        """
        Метод для обработки успешного подключения клиента
        :return:
        """
        self.login = None  # сбрасываем логин на начальное (пустое) значение
        self.factory.clients.append(self)  # добавим клиента в список подключенных
        #print("Connected" + self.login)  # выведем в терминал уведомление о новом подключении

    def lineReceived(self, line: bytes):
        """
        Метод обработки нового сообщения от клиента
        :param line:
        :return:
        """

        message = line.decode()  # декодируем байты в строку

        # если у клиента уже настроен логин (прошел авторизацию)
        if self.login is not None:
            self.factory.send_message_to_clients(self,message)

        # если у клиента еще нет логина (первый раз зашел)
        else:
            # проверяем, что прислал правильную команду (например - login:admin)
            if message.startswith("login:"):
                # убираем начальную часть
                login = message.replace("login:", "")

                # TODO: пометка для ДЗ (задание №1)
                #проверяем уникальность логина
                for user in self.factory.clients:
                    print('check',login, user.login)
                    if user.login==login:
                        print('Ununique username',self.login)
                        # отправим клиенту текст с ошибкой
                        self.sendLine(f"Логин {login} занят, попробуйте другой".encode())
                        # разрываем соединение с клиентом
                        self.transport.loseConnection()
                        return

                # записываем логин
                self.login=login
                print(f"New user {login}")
                self.sendLine(f"Добро пожаловать, {login}!!!".encode())

                # TODO: пометка для ДЗ (задание №2)
                # отправляем новому участнику последние 10 сообщений из чата
                self.factory.send_history(self)

            else:
                # если прислал неправильную команду
                # отправим клиенту текст с ошибкой
                self.sendLine("Неверный логин".encode())


class Server(ServerFactory):
    """
    Класс для работы сервера и создания новых подключений
    """

    protocol = Handler  # тип протокола для подключения
    clients: list  # список активных клиентов
    stock: list

    def __init__(self):
        """
        Конструктор сервера (инициализация пустого списка клиентов)
        """
        self.clients = []
        self.history=[]

    def startFactory(self):
        """
        Метод для обработки запуска сервера в режиме ожидания подключений
        :return:
        """
        print("Server started...")

    def send_message_to_clients(self,sender:Handler,message:str):
        """
        Метод для отправки сообщений всем клиентам
        :param message:
        :return:
        """
        # формируем сообщение для пересылки другим клиентам
        message=f"<{sender.login}>: {message}"
        # история сообщений
        self.history.append(message)

        # циклически отправляем остальным клиентам (кроме текущего)
        # TODO: смотри `send_message_to_client`
        for user in self.clients:
            if user is not sender:
                user.sendLine(message.encode())  # кодируем снова строку в байты

    def send_history(self, client:Handler,count=10):
        """
        Метод для отправки истории
        :param count:
        :return:
        """
        # TODO: пометка для ДЗ (задание №2)
        print("отправляем историю новичку ")
        story=self.history[-count:]
        for message in story:
            client.sendLine(message.encode())

# указание конфигурации реактора (порт и тип сервера)
reactor.listenTCP(    7410, Server())

# запуск реактора в работу
reactor.run()

