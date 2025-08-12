# 说明
PyFeishuGroupBot 是一个基于飞书机器人API的Python库，用于发送消息到飞书群组。
# 安装
pip install PyFeishuGroupBot
# 使用
```python
from PyFeishuGroupBot import *
bot = FeishuGroupBot("your_webhook_url")
bot.send_text("Hello, Feishu!")
```
# 消息类型
- 文本消息
- 卡片消息
- 富文本消息
- 图片消息
- 群名片消息
# 消息演示
```python
from PyFeishuGroupBot import FeishuGroupBot
# 初始化机器人
bot = FeishuGroupBot("https://open.feishu.cn/open-apis/bot/v2/hook/******")
# 发送消息
bot.send_text("Hello, world!")
# 发送卡片消息
bot.send_card("标题", "消息")
# 发送图片
bot.send_image("img_ecffc3b9-8f14-400f-a014-05eca1a4310g")
# 发送富文本消息
bot.send_rich_text("Title", [{"tag": "text","text": "项目有更新: "}, {"tag": "a","text": "请查看","href": "http://www.example.com/"}, {"tag": "at", "user_id": "ou_18eac8********17ad4f02e8bbbb"}])
# 发送群名片
bot.send_group_share(["oc_f5b1a7eb27ae2****339ff"])
# Markdown转换富文本
from PyFeishuGroupBot import parse_markdown_to_feishu_post, FeishuGroupBot

result = parse_markdown_to_feishu_post("#你好\n测试")

bot = FeishuGroupBot("https://open.feishu.cn/open-apis/bot/v2/hook/******")

bot.send_rich_text("Title", result)
```
# 更新日志
2025年8月4日 更新 Github Actions \
2025年8月12日 更新 Markdown转换富文本