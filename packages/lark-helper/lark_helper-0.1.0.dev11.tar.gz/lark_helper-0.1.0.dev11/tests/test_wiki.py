

from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1.wiki import get_file_meta, get_node_space

APP_ID = "cli_a4cd2759647ad00c"
APP_SECRET = "P7FoSIEJG7UDUmlHBhiTFfqQan3BbGzU"


def test_get_node():
    # https://hailiang.feishu.cn/wiki/PdG3wWa6JiUMxAkCCqucfrV5nHe?table=tblMF6PUGW7dVfHQ&view=vewJjoob5K
    token_manager = TenantAccessTokenManager(APP_ID, APP_SECRET)
    node = get_node_space(token_manager, "wiki", "PdG3wWa6JiUMxAkCCqucfrV5nHe")
    print(node)
    
    
def test_get_document():
    # https://hailiang.feishu.cn/docx/V1yqdT2Hyo9F3kxYqEDcxSQRnZy
    token_manager = TenantAccessTokenManager(APP_ID, APP_SECRET)
    document = get_file_meta(token_manager, "PeuMbsRN9oGibVxnEiCcqZuhnLe", "file")
    print(document)