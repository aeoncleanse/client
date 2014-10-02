
import json

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

from client import networkAccessManager

class RESTResponse(QObject):

    error = pyqtSignal(dict)
    done = pyqtSignal(dict)

    def __init__(self, reply):
        super(RESTResponse, self).__init__()

        self.reply = reply
        reply.finished.connect(self._onFinished)

    def _onFinished(self):
        resData = str(self.reply.readAll())
        if self.reply.error():
            if len(resData) == 0:
                self.error.emit({ 'statusMessage': self.reply.errorString() })
            else:
                self.error.emit( json.loads(resData) )
        else:
            resp = json.loads(resData)

            self.done.emit(resp)

class IRESTService:
    @staticmethod
    def _get( url):
        req = QNetworkRequest( QUrl(url) )
        return RESTResponse(networkAccessManager.get( req ))

    @staticmethod
    def _post( url, postData):
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        return RESTResponse(networkAccessManager.post( req, json.dumps(postData).encode()))
