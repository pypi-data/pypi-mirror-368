from .template import send_feishu_card_message, send_feishu_rich_text_message, send_feishu_group_shar_message, send_feishu_image_message, send_feishu_text_message, parse_markdown_to_feishu_post

# test
class FeishuGroupBot:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    # 发送文本消息
    def send_text(self, message):
        response = send_feishu_text_message(self.webhook_url, message)
        return response

    # 发送卡片消息
    def send_card(self, title, message):
        response = send_feishu_card_message(self.webhook_url, title, message)
        return response

    # 发送富文本消息
    def send_rich_text(self, title, content):
        response = send_feishu_rich_text_message(self.webhook_url, title, content)
        return response

    # 发送群名片消息
    def send_group_share(self, group_id):
        response = send_feishu_group_shar_message(self.webhook_url, group_id)
        return response

    # 发送图片消息
    def send_image(self, image_key):
        response = send_feishu_image_message(self.webhook_url, image_key)
        return response