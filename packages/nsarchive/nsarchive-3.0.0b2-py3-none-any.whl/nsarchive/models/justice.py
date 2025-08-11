import requests
import time

from .base import NSID

from .. import errors

class Report:
    def __init__(self, id: NSID):
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = id
        self.author: NSID = NSID('0')
        self.target: NSID = NSID('0')
        self.date: int = round(time.time())
        self.status: int = 0 # 0: En attente, 1: Accepté, 2: Rejeté
        self.reason: str = None # Raison proposée par le bot
        self.details:str = None # Description des faits

    def _load(self, _data: dict, url: str, headers: str) -> None:
        self._url = url
        self._headers = headers

        self.id = NSID(_data['id'])
        self.author = NSID(_data['author'])
        self.target = NSID(_data['target'])
        self.date = _data['date']
        self.status = _data['status']
        self.reason = _data.get('reason', None)
        self.details = _data.get('details', None)

    def update(self, status: str | int):
        __statuses = [
            'pending',
            'accepted',
            'rejected'
        ]

        if status not in __statuses:
            if isinstance(status, int) and 0 <= status <= 2:
                status = __statuses[status]

            else:
                raise ValueError(f"Invalid status: {status}. Must be one of {__statuses} or an integer between 0 and 2.")

        res = requests.post(f"{self._url}/update?status={status}", headers = self._headers)

        if res.status_code == 200:
            self.status = status
        elif 500 <= res.status_code < 600:
            raise errors.globals.ServerDownError()

        _data = res.json()

        if res.status_code == 400:
            if _data['message'] == "MissingParam":
                raise errors.globals.MissingParamError(f"Missing parameter '{_data['param']}'.")
            elif _data['message'] == "InvalidParam":
                raise errors.globals.InvalidParamError(f"Invalid parameter '{_data['param']}'.")
            elif _data['message'] == "InvalidToken":
                raise errors.globals.AuthError("Token is not valid.")

        elif res.status_code == 401:
            raise errors.globals.AuthError(_data['message'])

        elif res.status_code == 403:
            raise errors.globals.PermissionError(_data['message'])

        elif res.status_code == 404:
            raise errors.globals.NotFoundError(_data['message'])

class Sanction:
    def __init__(self, id: NSID):
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = id
        self.target: NSID = NSID('0')
        self.type: str = None
        self.date: int = round(time.time())
        self.duration: int = 0
        self.title: str = None
        self.lawsuit: NSID = NSID('0')

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url
        self._headers = headers

        self.id = NSID(_data['id'])
        self.target = NSID(_data['target'])
        self.type = _data['type']
        self.date = _data['date']
        self.duration = _data['duration']
        self.title = _data['title']
        self.lawsuit = NSID(_data['lawsuit'])

class Lawsuit:
    def __init__(self, id: NSID):
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = id
        self.target: NSID = NSID('0')
        self.judge: NSID = NSID('0')
        self.title: str = None
        self.date: int = round(time.time())
        self.report: NSID = NSID('0')
        self.is_private: bool = False
        self.is_open: bool = False

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url
        self._headers = headers

        self._url = url
        self._headers = headers

        self.id = NSID(_data['id'])
        self.target = NSID(_data['target'])
        self.judge = NSID(_data['judge'])
        self.title = _data.get('title')
        self.date = _data.get('date', round(time.time()))

        report = _data.get('report')
        self.report = NSID(report) if report else NSID('0')

        self.is_private = bool(_data.get('private', 0))
        self.is_open = _data.get('status', 0) == 0