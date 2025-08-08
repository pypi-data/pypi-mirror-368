import time

from lark_helper.v1.bitable import (
    add_bitable_record,
    list_bitable_views_page,
    search_bitable_record_page,
    update_bitable_record,
)
from tests.config import doc_helper_token_manager

TEST_BITABLE_APP_TOKEN = "E9qsblnqjaET7YshawucoLkNnNg"
TEST_BITABLE_TABLE_ID = "tblXDeFgmlAfvQfB"
TEST_BITABLE_VIEW_ID = "vewNwXGkns"


def test_add_bitable_record():
    resp_data = search_bitable_record_page(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
        view_id=TEST_BITABLE_VIEW_ID,
    )
    records_count = resp_data.total
    
    add_bitable_record(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
        fields={
            "文本": "test",
            "单选": "选项1",
            "日期": int(1000*time.time()),
        },
    )
    
    resp_data = search_bitable_record_page(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
        view_id=TEST_BITABLE_VIEW_ID,
    )
    new_records_count = resp_data.total
    assert new_records_count == records_count + 1
    
    
def test_update_bitable_record():
    resp_data = search_bitable_record_page(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
        view_id=TEST_BITABLE_VIEW_ID,
    )
    records_count = resp_data.total
    assert records_count > 0
    
    record_id = resp_data.items[0].record_id
    value = resp_data.items[0].get_text_field("文本")
    new_value = f"{value}+1"
    if len(new_value) > 10:
        new_value = "test"
    
    update_bitable_record(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
        record_id=record_id,
        fields={
            "文本": new_value,
        },
    )
    
    resp_data = search_bitable_record_page(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
        view_id=TEST_BITABLE_VIEW_ID,
    )
    new_records_count = resp_data.total
    assert new_records_count == records_count
    
    record = resp_data.items[0]
    assert record.get_text_field("文本") == new_value
    
    
def test_list_bitable_views():
    resp_data = list_bitable_views_page(
        token_manager=doc_helper_token_manager,
        app_token=TEST_BITABLE_APP_TOKEN,
        table_id=TEST_BITABLE_TABLE_ID,
    )
    assert resp_data.total > 0