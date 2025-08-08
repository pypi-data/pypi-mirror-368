from enum import IntEnum


class ImportTaskJobStatus(IntEnum):
    """导入任务作业状态枚举"""

    SUCCESS = 0  # 导入成功
    INITIALIZING = 1  # 初始化
    PROCESSING = 2  # 处理中
    INTERNAL_ERROR = 3  # 内部错误

    # 特定错误状态码
    ENCRYPTED_DOC = 100  # 导入文档已加密
    INTERNAL_ERROR_101 = 101  # 内部错误
    INTERNAL_ERROR_102 = 102  # 内部错误
    INTERNAL_ERROR_103 = 103  # 内部错误
    INSUFFICIENT_CAPACITY = 104  # 租户容量不足
    TOO_MANY_FOLDER_NODES = 105  # 文件夹节点太多
    INTERNAL_ERROR_106 = 106  # 内部错误
    PROCESSING_TIMEOUT = 108  # 处理超时
    INTERNAL_ERROR_109 = 109  # 内部错误
    NO_PERMISSION = 110  # 无权限
    UNSUPPORTED_FORMAT = 112  # 格式不支持
    UNSUPPORTED_OFFICE_FORMAT = 113  # office格式不支持
    INTERNAL_ERROR_114 = 114  # 内部错误
    FILE_TOO_LARGE = 115  # 导入文件过大
    NO_FOLDER_PERMISSION = 116  # 当前身份无导入至该文件夹的权限
    DIRECTORY_DELETED = 117  # 目录已删除
    FILE_SUFFIX_MISMATCH = 118  # 导入文件和任务指定后缀不匹配
    DIRECTORY_NOT_EXIST = 119  # 目录不存在
    FILE_TYPE_MISMATCH = 120  # 导入文件和任务指定文件类型不匹配
    FILE_EXPIRED = 121  # 导入文件已过期
    COPY_EXPORT_FORBIDDEN = 122  # 创建副本中禁止导出
    FILE_FORMAT_CORRUPTED = 129  # 文件格式损坏
    INTERNAL_ERROR_5000 = 5000  # 内部错误
    DOCX_BLOCK_COUNT_LIMIT = 7000  # docx block 数量超过系统上限
    DOCX_BLOCK_LEVEL_LIMIT = 7001  # docx block 层级超过系统上限
    DOCX_BLOCK_SIZE_LIMIT = 7002  # docx block 大小超过系统上限


IMPORT_TASK_JOB_STATUS_ERROR_MAP = {
    ImportTaskJobStatus.INTERNAL_ERROR: "内部错误",
    ImportTaskJobStatus.ENCRYPTED_DOC: "导入文档已加密",
    ImportTaskJobStatus.INTERNAL_ERROR_101: "内部错误",
    ImportTaskJobStatus.INTERNAL_ERROR_102: "内部错误",
    ImportTaskJobStatus.INTERNAL_ERROR_103: "内部错误",
    ImportTaskJobStatus.INSUFFICIENT_CAPACITY: "租户容量不足",
    ImportTaskJobStatus.TOO_MANY_FOLDER_NODES: "文件夹节点太多",
    ImportTaskJobStatus.INTERNAL_ERROR_106: "内部错误",
    ImportTaskJobStatus.PROCESSING_TIMEOUT: "处理超时",
    ImportTaskJobStatus.INTERNAL_ERROR_109: "内部错误",
    ImportTaskJobStatus.NO_PERMISSION: "无权限",
    ImportTaskJobStatus.UNSUPPORTED_FORMAT: "格式不支持",
    ImportTaskJobStatus.UNSUPPORTED_OFFICE_FORMAT: "office格式不支持",
    ImportTaskJobStatus.INTERNAL_ERROR_114: "内部错误",
    ImportTaskJobStatus.FILE_TOO_LARGE: "导入文件过大",
    ImportTaskJobStatus.NO_FOLDER_PERMISSION: "当前身份无导入至该文件夹的权限",
    ImportTaskJobStatus.DIRECTORY_DELETED: "目录已删除",
    ImportTaskJobStatus.FILE_SUFFIX_MISMATCH: "导入文件和任务指定后缀不匹配",
    ImportTaskJobStatus.DIRECTORY_NOT_EXIST: "目录不存在",
    ImportTaskJobStatus.FILE_TYPE_MISMATCH: "导入文件和任务指定文件类型不匹配",
    ImportTaskJobStatus.FILE_EXPIRED: "导入文件已过期",
    ImportTaskJobStatus.COPY_EXPORT_FORBIDDEN: "创建副本中禁止导出",
    ImportTaskJobStatus.FILE_FORMAT_CORRUPTED: "文件格式损坏。请另存为新文件后导入",
    ImportTaskJobStatus.INTERNAL_ERROR_5000: "内部错误",
    ImportTaskJobStatus.DOCX_BLOCK_COUNT_LIMIT: "docx block 数量超过系统上限",
    ImportTaskJobStatus.DOCX_BLOCK_LEVEL_LIMIT: "docx block 层级超过系统上线",
    ImportTaskJobStatus.DOCX_BLOCK_SIZE_LIMIT: "docx block 大小超过系统上限",
}


class ExportTaskJobStatus(IntEnum):
    """导出任务作业状态枚举"""

    SUCCESS = 0  # 成功
    INITIALIZING = 1  # 初始化
    PROCESSING = 2  # 处理中
    INTERNAL_ERROR = 3  # 内部错误
    EXPORT_FILE_TOO_LARGE = 107  # 导出文档过大
    PROCESSING_TIMEOUT = 108  # 处理超时
    EXPORT_BLOCK_NO_PERMISSION = 109  # 导出内容块无权限
    NO_PERMISSION = 110  # 无权限
    EXPORT_DOC_DELETED = 111  # 导出文档已删除
    COPY_EXPORT_FORBIDDEN = 122  # 创建副本中禁止导出
    EXPORT_DOC_NOT_EXIST = 123  # 导出文档不存在
    TOO_MANY_IMAGES = 6000  # 导出文档图片过多


EXPORT_TASK_JOB_STATUS_ERROR_MAP = {
    ExportTaskJobStatus.INTERNAL_ERROR: "内部错误",
    ExportTaskJobStatus.EXPORT_FILE_TOO_LARGE: "导出文档过大",
    ExportTaskJobStatus.PROCESSING_TIMEOUT: "处理超时",
    ExportTaskJobStatus.EXPORT_BLOCK_NO_PERMISSION: "导出内容块无权限",
    ExportTaskJobStatus.NO_PERMISSION: "无权限",
    ExportTaskJobStatus.EXPORT_DOC_DELETED: "导出文档已删除",
    ExportTaskJobStatus.COPY_EXPORT_FORBIDDEN: "创建副本中禁止导出",
    ExportTaskJobStatus.EXPORT_DOC_NOT_EXIST: "导出文档不存在",
    ExportTaskJobStatus.TOO_MANY_IMAGES: "导出文档图片过多",
}
