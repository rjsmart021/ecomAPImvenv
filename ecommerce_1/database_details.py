import os


class DataBaseDetails:

    def __init__(self):
        self.__host = os.environ.get("db_host", default="localhost")
        self.__user = os.environ.get("db_user")
        self.__database = os.environ.get("database")
        self.__password = os.environ.get("db_password")


    @property
    def get_password(self):
        return self.__password

    @property
    def get_host(self):
        return self.__host

    @property
    def get_user(self):
        return self.__user

    @property
    def get_database(self):
        return self.__database
