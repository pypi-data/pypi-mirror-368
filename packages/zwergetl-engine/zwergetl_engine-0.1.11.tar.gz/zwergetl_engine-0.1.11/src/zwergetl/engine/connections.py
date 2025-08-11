
class Connection:
    """
    Base class used to store connection parameters for databases
    and other database-like services.
    """
    def __init__(
        self,
        conn_id:str,
        host="",
        port="",
        database="",
        username="",
        password=""
    ):
        self.conn_id = conn_id
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def get_conn(self):
        """
        Gets a DBAPI database connection.

        :return: python DBAPI connection object
        """
        pass
