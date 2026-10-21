# Seedance 提示词库（中文分类版）

82 条 Seedance 2.5 热门提示词，按镜头类型分成 9 类。每条都有中文标题、X 原作者、原帖链接和完整英文提示词。

另外附两个脚本：把库存进 EverOS，然后用中文说一句需求就能搜出最接近的提示词。

## 这批提示词

- 82 条，来自 39 位 X 创作者，发布于 2026 年 7 月底到 10 月初
- 36 条带第三方复测结论：21 条复现成功，14 条效果有衰减，1 条失败
- 复测结论和稳定度分数来自 goodcase.ai，不是本仓库测的

完整内容见 [第一批.md](第一批.md)，结构化数据见 [第一批.json](第一批.json)。

## 9 类镜头速查

| 镜头类型 | 条数 | 这批提示词的共同写法 | 先试这几条（复测通过） |
|---|---|---|---|
| 手持 Vlog / DV 家庭录像 | 24 | 主动写设备瑕疵：手抖、对焦游移、DV 色彩、自拍视角 | @SimplyAnnisa、@nawalsehar、@AIwithkhan |
| 分秒分镜 / 多镜头叙事 | 27 | 按 0-4s、4-8s 切段，每段写清景别、动作、机位 | @itsSaira_1、@Zyrellix、@AiwithElisia |
| 一镜到底 / 长镜头 | 3 | 全程不切，一个连续运镜带完整情节 | @Just_sharon7 |
| 环绕 / 俯拍等特殊机位 | 3 | 360 度环绕、正上方俯拍 | 无 |
| 微距 / 延时 | 2 | 微距特写加时间压缩 | 无 |
| 特效 / 超现实 / 尺度反差 | 6 | 破框、空间折叠、巨物和微缩对比 | @Just_sharon7 |
| MV / 时尚群像 | 8 | 按节拍卡点，或一人静止、人群同步的反差 | @Zoyavelle |
| 3D 动画 / 儿童 / 动漫 | 7 | 皮克斯风、儿童教育、日式动漫 | @Zarnab_with_Ai |
| 带货 UGC / 角色锁定 | 2 | 先锁人物和产品，再生成口播种草 | @AIwithkhan |

## 用中文需求搜提示词

需要 Python 3.12 以上和一个 EverOS API key（在 https://everos.evermind.ai 控制台获取）。

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export EVEROS_API_KEY=你的key

python3 ingest.py                                      # 入库，重复跑会跳过已有条目
python3 demo.py search "雨夜 女生 手持 vlog 感"           # 搜最接近的 3 条
python3 demo.py search "打斗 分镜 动作戏" --full 1        # 展开第 1 条完整提示词
```

每条入库时都带了中文标题和镜头类型，所以用中文描述需求也能搜到英文提示词。

## 来源与授权

- 提示词整理自 [Nuos/awesome-seedance](https://github.com/Nuos/awesome-seedance)（整理内容 CC BY 4.0，数据来自 goodcase.ai），本仓库在此基础上做了中文标题、镜头分类和检索脚本
- 每条提示词的版权归 X 原作者，使用前请查看原帖
- 本仓库的分类整理内容按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 发布，脚本（ingest.py、demo.py）按 MIT 发布

整理：王大锤 · 本仓库的检索部分使用 EverOS Cloud，属于 EverOS 合作内容
