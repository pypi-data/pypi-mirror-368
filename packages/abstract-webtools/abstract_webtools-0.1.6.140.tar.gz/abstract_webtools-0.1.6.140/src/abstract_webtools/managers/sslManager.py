from ..abstract_webtools import *
class SSLManager:
    def __init__(self, ciphers=None, ssl_options=None, certification=None):
        self.ciphers = ciphers or CipherManager().ciphers_string
        self.ssl_options = ssl_options or self.get_default_ssl_settings()
        self.certification = certification or ssl.CERT_REQUIRED
        self.ssl_context = self.get_context()
    def get_default_ssl_settings(self):
        return ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_COMPRESSION
    def get_context(self):
        return ssl_.create_urllib3_context(ciphers=self.ciphers, cert_reqs=self.certification, options=self.ssl_options)

class SSLManagerSingleton:
    _instance = None
    @staticmethod
    def get_instance(ciphers=None, ssl_options_list=None, certification=None):
        if SSLManagerSingleton._instance is None:
            SSLManagerSingleton._instance = SSLManager(ciphers=ciphers, ssl_options_list=ssl_options_list, certification=certification)
        elif SSLManagerSingleton._instance.cipher_manager.ciphers_string != ciphers or SSLManagerSingleton._instance.ssl_options_list !=ssl_options_list or SSLManagerSingleton._instance.certification !=certification:
            SSLManagerSingleton._instance = SSLManager(ciphers=ciphers, ssl_options_list=ssl_options_list, certification=certification)
        return SSLManagerSingleton._instance
