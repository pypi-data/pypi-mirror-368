from pydantic import BaseModel


class ImportTaskResult(BaseModel):
    job_status: int
    token: str | None = None
    url: str | None = None
    job_error_msg: str | None = None


class TmpDownloadUrl(BaseModel):
    file_token: str
    tmp_download_url: str


class ExportTaskResult(BaseModel):
    job_status: int
    file_token: str | None = None
    job_error_msg: str | None = None
