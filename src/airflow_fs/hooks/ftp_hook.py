import ftplib

try:
    import ftputil
    from ftputil import session as ftp_session
except ImportError:
    ftputil, ftp_session = None, None

from . import FsHook


class FtpHook(FsHook):
    """Hook for interacting with files over FTP."""

    def __init__(self, conn_id):
        super().__init__()
        self._conn_id = conn_id
        self._conn = None

    def get_conn(self):
        if ftputil is None:
            raise ImportError("ftputil must be installed to use the FtpHook")

        if self._conn is None:
            config = self.get_connection(self._conn_id)

            secure = config.extra_dejson.get("tls", False)
            base_class = ftplib.FTP_TLS if secure else ftplib.FTP

            session_factory = ftp_session.session_factory(
                base_class=base_class,
                port=config.port or 21,
                encrypt_data_channel=secure,
            )

            self._conn = ftputil.FTPHost(
                config.host,
                config.login,
                config.password,
                session_factory=session_factory,
            )

        return self._conn

    def disconnect(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def open(self, file_path, mode="rb"):
        return self.get_conn().open(file_path, mode=mode)

    def exists(self, file_path):
        return self.get_conn().path.exists(file_path)

    def makedirs(self, dir_path, mode=0o755, exist_ok=True):
        if not exist_ok and self.exists(dir_path):
            raise ValueError("Directory already exists")
        self.get_conn().makedirs(dir_path)

    def glob(self, pattern):
        raise NotImplementedError()

    def remove(self, file_path):
        self.get_conn().remove(file_path)

    def rmtree(self, dir_path):
        self.get_conn().rmtree(dir_path, ignore_errors=False)