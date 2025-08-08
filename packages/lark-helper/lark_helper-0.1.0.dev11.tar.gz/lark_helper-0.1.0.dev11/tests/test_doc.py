from datetime import datetime

import pytest

from lark_helper.v1.doc import markdown_to_docx
from lark_helper.v1_async.doc import async_markdown_to_docx
from tests.config import doc_helper_token_manager


def test_markdown_to_docx():
    markdown_content = """# 学校名称校长需求画像

## 待解决问题

1. 生源规模不足（严重）
2. 优质生源流失（一般）
3. 管理层内部矛盾，团队协作凝聚力匮乏（严重）
4. 校园安保隐患（一般）


## 校长核心能力图谱

### 一级能力雷达图

![一级能力雷达图](https://hljydc-common.obs.cn-east-3.myhuaweicloud.com/temp/radar/20250620/3e862c606bc24936917aa1231390acb1.png)

## 校长细分能力图谱

### 二级能力雷达图

![二级能力雷达图](https://hljydc-common.obs.cn-east-3.myhuaweicloud.com/temp/radar/20250620/74642a86aa3f42e89a0201481bd437f1.png)

## 校长经验

1. 至少进校做过招生宣讲1场；有优生招录实际经验；主持或指导撰写有份量品宣文稿不低于2篇。
2. 一学年内组织过安全应急演练不低于3次，校长办公会上每月讨论安全管理工作至少1次，所管理学校未出现过重大安全事故。
3. 安全管理意识突出；安全管理体系构建经验丰富。
4. 熟悉公办学校管理，善于思想动员，沟通能力强。
5. 掌握多元沟通技巧，能与教师、学生、家长等不同群体有效交流；熟悉招生政策和流程，了解不同类型学生的招生需求和心理，擅长制定差异化招生方案（如特长生培养、奖学金激励、分班机制优化等），构建生源优化闭环，如招生吸引-分层培养-口碑反哺；擅长挖掘学校特色和优势提升学校社会口碑，通过多种渠道进行宣传推广，提升学校的知名度和美誉度，吸引更多生源；能精准解读教育政策（如"双减"、新课标等）将政策红利转化为学校发展资源（如专项经费申请）。
6. 公办学校任校长3年以上；熟悉教育行政主管部门运作程序。"""
    url = markdown_to_docx(
        doc_helper_token_manager,
        markdown_content,
        f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "XhM4fAYOjlknMQdqcbPcEkdXnde",
    )
    print(url)


@pytest.mark.asyncio
async def test_async_markdown_to_docx():
    markdown_content = """# 学校名称校长需求画像

    """
    url = await async_markdown_to_docx(
        doc_helper_token_manager,
        markdown_content,
        f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "XhM4fAYOjlknMQdqcbPcEkdXnde",
    )
    print(url)