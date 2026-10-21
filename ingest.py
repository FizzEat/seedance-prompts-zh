"""把 第一批.json 批量存进 EverOS 知识库。

用法：
    export EVEROS_API_KEY=你的key
    python ingest.py                 # 默认读 第一批.json
    python ingest.py 第二批.json      # 之后加新批次

重复跑不会重复入库：已存在同名文档会跳过。
知识库 id 记在同目录 .everos_state.json，demo.py 会读它。
"""
import json
import os
import sys
import time
from pathlib import Path

from everos_cloud import EverOS, EverOSError

HERE = Path(__file__).resolve().parent
STATE = HERE / ".everos_state.json"
KB_NAME = "Seedance 提示词库"


def doc_title(item):
    return f"{item['title_zh']} | {item['category']} | {item['author']}"


def doc_body(item):
    # 元数据放在正文开头，检索时分类、作者、复测结论也能被命中
    return "\n".join([
        f"标题：{item['title_zh']}（{item['title']}）",
        f"镜头类型：{item['category']}",
        f"作者：{item['author']}  原帖：{item['url']}",
        f"复测：{item.get('retest') or '未复测'}  稳定度：{item.get('stability') or '无'}",
        f"简介：{item.get('summary', '')}",
        "",
        "提示词：",
        item["prompt"],
    ])


def get_or_create_kb(client):
    if STATE.exists():
        return json.loads(STATE.read_text())["kb_id"]
    for kb in client.kb_list(page_size=100).knowledge_bases or []:
        if kb.name == KB_NAME:
            kb_id = kb.id
            break
    else:
        kb_id = client.kb_create(KB_NAME, description="按镜头类型分类的 Seedance 提示词，每条附 X 原作者和原帖链接").id
    STATE.write_text(json.dumps({"kb_id": kb_id}))
    return kb_id


def existing_titles(client, kb_id):
    titles, page = set(), 1
    while True:
        data = client.doc_list(kb_id, page=page, page_size=100)
        docs = data.documents or []
        titles.update(d.title for d in docs)
        if len(titles) >= (data.total or 0) or not docs:
            return titles
        page += 1


def main():
    api_key = os.environ.get("EVEROS_API_KEY")
    if not api_key:
        sys.exit("先设置环境变量 EVEROS_API_KEY")
    src = HERE / (sys.argv[1] if len(sys.argv) > 1 else "第一批.json")
    items = json.loads(src.read_text(encoding="utf-8"))

    client = EverOS(api_key=api_key)
    kb_id = get_or_create_kb(client)
    have = existing_titles(client, kb_id)
    todo = [it for it in items if it.get("prompt") and doc_title(it) not in have]
    print(f"知识库 {kb_id}：已有 {len(have)} 条，本次新增 {len(todo)} 条")

    tasks = []
    for n, it in enumerate(todo, 1):
        try:
            ack = client.doc_ingest(kb_id, doc_title(it), doc_body(it))
            tasks.append((it, ack.task_id))
            print(f"[{n}/{len(todo)}] 已提交  {it['category']}  {it['title_zh']}")
        except EverOSError as e:
            print(f"[{n}/{len(todo)}] 提交失败  {it['title_zh']}：{e}")
        time.sleep(0.3)

    # 入库是异步的，等全部处理完再录屏
    failed = 0
    for it, task_id in tasks:
        try:
            item = client.task_wait(task_id, raise_on_failure=False)
        except EverOSError as e:  # 超时不一定是失败，稍后去控制台确认
            failed += 1
            print(f"等待超时：{it['title_zh']}（{e}）")
            continue
        if item.status != "success":
            failed += 1
            print(f"处理失败：{it['title_zh']}（{item.status}）")
    print(f"完成：成功 {len(tasks) - failed} 条，失败 {failed} 条")


if __name__ == "__main__":
    main()
