"""按需求检索 Seedance 提示词，录屏用。

用法：
    export EVEROS_API_KEY=你的key

    # 1. 查提示词库，--full 2 展开第 2 条的完整提示词
    python demo.py search "雨夜 女生 手持 vlog 感" --full 2

    # 2. 以后自己跑了 Seedance，把结果存回去，再搜时加 --memory 看经验
    python demo.py log --need "雨夜 女生 手持 vlog" --prompt "实际用的提示词" \
        --result "手抖自然，第 8 秒脸崩" --score 3

库里的条目来自 ingest.py；经验记在 agent 记忆里，多了会被提炼成 Skill。
"""
import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

from everos_cloud import EverOS

HERE = Path(__file__).resolve().parent
STATE = HERE / ".everos_state.json"
AGENT_ID = "seedance_prompt_agent"
USER_ID = "wangdachui"

BOLD, DIM, CYAN, YELLOW, RESET = "\033[1m", "\033[2m", "\033[36m", "\033[33m", "\033[0m"


def load_local():
    # 本地 json 用来补全作者、原帖链接和完整提示词，按入库时的标题对上
    items = {}
    for f in sorted(HERE.glob("第*批.json")):
        for it in json.loads(f.read_text(encoding="utf-8")):
            items[f"{it['title_zh']} | {it['category']} | {it['author']}"] = it
    return items


def doc_titles(client, kb_id):
    titles, page = {}, 1
    while True:
        data = client.doc_list(kb_id, page=page, page_size=100)
        docs = data.documents or []
        titles.update({d.id: d.title for d in docs})
        if len(titles) >= (data.total or 0) or not docs:
            return titles
        page += 1


def cmd_search(client, query, top_k, full=0, with_memory=False):
    kb_id = json.loads(STATE.read_text())["kb_id"]
    local = load_local()

    print(f"\n{BOLD}需求：{query}{RESET}\n")
    print(f"{CYAN}一、提示词库里最接近的{RESET}")
    t0 = time.time()
    hits = client.kb_search(kb_id, query, top_k=top_k * 3).hits
    titles = doc_titles(client, kb_id)
    seen = []
    for h in hits:  # 一篇文档会切出多个 topic，按文档去重
        if h.doc_id not in seen:
            seen.append(h.doc_id)
    for n, doc_id in enumerate(seen[:top_k], 1):
        it = local.get(titles.get(doc_id, ""))
        if not it:
            print(f"  {n}. {titles.get(doc_id, doc_id)}")
            continue
        print(f"  {BOLD}{n}. {it['title_zh']}{RESET}  {DIM}{it['category']}{RESET}")
        print(f"     {it['author']}  {it['url']}")
        print(f"     复测：{it.get('retest') or '未复测'}  稳定度：{it.get('stability') or '无'}")
        print(f"     {DIM}{it['prompt'][:160].replace(chr(10), ' ')}...{RESET}")
    print(f"  {DIM}耗时 {time.time() - t0:.1f}s{RESET}")

    if full and 1 <= full <= len(seen):
        it = local.get(titles.get(seen[full - 1], ""))
        if it:
            print(f"\n{CYAN}第 {full} 条完整提示词{RESET}  {DIM}{it['author']} {it['url']}{RESET}\n")
            print(it["prompt"])

    if with_memory:
        print(f"\n{CYAN}二、我自己跑过的经验{RESET}")
        mem = client.search(query, agent_id=AGENT_ID, top_k=top_k)
        skills, cases = mem.agent_skills or [], mem.agent_cases or []
        if not skills and not cases:
            print(f"  {DIM}还没有相关经验，跑完用 log 存一条{RESET}")
        for s in skills:
            print(f"  {YELLOW}Skill：{s.name}{RESET}  {s.description}")
            print(f"     {DIM}{s.content[:200]}{RESET}")
        for c in cases:
            print(f"  Case：{c.task_intent}")
            print(f"     {DIM}{c.approach[:200]}{RESET}")
    print()


def cmd_log(client, need, prompt, result, score):
    session_id = f"seedance_{uuid.uuid4().hex[:8]}"
    now = int(time.time() * 1000)
    client.add(
        session_id=session_id,
        messages=[
            {"sender_id": USER_ID, "role": "user", "timestamp": now,
             "content": f"帮我写一条 Seedance 提示词，需求：{need}"},
            {"sender_id": AGENT_ID, "role": "assistant", "timestamp": now + 1,
             "content": f"使用的提示词：{prompt}"},
            {"sender_id": USER_ID, "role": "user", "timestamp": now + 2,
             "content": f"生成结果：{result}。评分 {score}/5"},
        ],
        async_mode=False,
    )
    client.flush(session_id)
    print(f"已存入经验 {session_id}，提取需要几秒到几十秒")


def main():
    api_key = os.environ.get("EVEROS_API_KEY")
    if not api_key:
        sys.exit("先设置环境变量 EVEROS_API_KEY")
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--top", type=int, default=3)
    s.add_argument("--full", type=int, default=0, help="展开第几条的完整提示词")
    s.add_argument("--memory", action="store_true", help="同时查自己跑过的经验")
    l = sub.add_parser("log")
    l.add_argument("--need", required=True)
    l.add_argument("--prompt", required=True)
    l.add_argument("--result", required=True)
    l.add_argument("--score", type=int, choices=range(1, 6), required=True)
    a = p.parse_args()

    client = EverOS(api_key=api_key)
    if a.cmd == "search":
        cmd_search(client, a.query, a.top, a.full, a.memory)
    else:
        cmd_log(client, a.need, a.prompt, a.result, a.score)


if __name__ == "__main__":
    main()
