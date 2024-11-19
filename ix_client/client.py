from functools import wraps
import logging

from socketio import Client
from socketio.exceptions import ConnectionError, ConnectionRefusedError, SocketIOError, TimeoutError

socketio_exceptions = (ConnectionError, ConnectionRefusedError, SocketIOError, TimeoutError)
logging.basicConfig(format="%(levelname)s:     %(message)s", level=logging.INFO)


class IxClient(object):
    """An ORANOS Ix Client.

    This class implements an ORANOS Ix client that enables xApp communication to their respective Ix server.
    It uses socket.io websockets and long-polling requests to achieve minimal transmit latency.

    :param url: Root URL of the xApp's local Ix server.
    :param username: The `ix_username` provided by the Ix server after registering the xApp.
    :param password: The `ix_password` provided by the Ix server after registering the xApp.
    :param data_logging: (Optional) If True, a copy of the trasported data will be printed in the logs. Default is False.
    """

    def __init__(self, url: str, username: str, password: str, data_logging: bool = False):
        self._url = url
        self._username = username
        self._password = password
        self._client = Client(reconnection_delay=0)
        self._is_connected = False
        self._emit_path = None
        self._data_logging = data_logging

        @self._client.event
        def connect():
            logging.info("Connected to Ix!")
            self._is_connected = True

        @self._client.event
        def disconnect():
            logging.info("Disconnected from Ix.")
            self._is_connected = False

        @self._client.event
        def connect_error(message):
            logging.error("Ix Error:", message)

    @property
    def is_connected(self) -> bool:
        """Returns the current connection status of the Ix client."""
        return self._is_connected

    def socketio_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except socketio_exceptions as ex:
                logging.error(ex)

        return wrapper

    @socketio_wrapper
    def connect(self, relation_id: str = ""):
        """Initiate the Ix client's connection to the Ix server.

        :param relation_id: (Optional) If a relation_id is provided, the Ix server will create a 
        pipeline to the remote Ix server and xApp found in the relation details.
        """
        auth = {"ix_username": self._username, "ix_password": self._password}
        self._emit_path = "xapp_local_emit"
        if relation_id:
            auth["relation_id"] = relation_id
            self._emit_path = "xapp_relation_emit"
        self._client.connect(url=self._url, socketio_path="/internal/ws",  auth=auth)

    @socketio_wrapper
    def disconnect(self):
        """Terminate the Ix client's connection to the Ix server."""
        if self._is_connected:
            self._client.disconnect()

    @socketio_wrapper
    def send(self, data: dict):
        """Transmit data to the Ix server. If the connection was made with a relation_id, 
        the data will also be forwarded to the remote Ix server and xApp found in the relation details.

        :param data: Data in the form of a dictionary.

        Example usage::

            while IxClient.is_connected:
                IxClient.send(data={"attenuation": 69, "health": 0.74})
        """
        if not self._is_connected:
            logging.error("Please make a client connection before sending any data.")
            return
        if not dict:
            logging.error("Data cannot be empty. Please send a valid dict.")
            return
        if self._data_logging:
            logging.info(f"Sending {data}")
        self._client.emit(self._emit_path, data)
