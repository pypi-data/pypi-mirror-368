class LarkResponseError(Exception):
    """lark api response error"""

    pass


class ImportTaskError(Exception):
    def __init__(self, job_status: int, job_error_msg: str):
        self.job_status = job_status
        self.job_error_msg = job_error_msg


class ExportTaskError(Exception):
    def __init__(self, job_status: int, job_error_msg: str):
        self.job_status = job_status
        self.job_error_msg = job_error_msg
