import plugins, threading
from flask import Flask
from bridge.context import ContextType, Context
from bridge.reply import Reply, ReplyType
from channel import channel_factory
from plugins import *

@plugins.register(
    name='Aligenie',
    desire_priority=10,
    hidden=False,
    desc='Aligenie plugin',
    version='0.1.0',
    author='liqwang'
)

class Aligenie(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info('[Aligenie] inited')

    def on_handle_context(self, e_context: EventContext) -> None:
        context = e_context['context']
        if not context['isgroup'] or context.type != ContextType.TEXT:
            return
        if context.content == '开启天猫精灵消息接收':
            groups.add(context['receiver'])
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = '✅天猫精灵消息接收已开启'
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS


groups = set()  # 开启天猫精灵消息接收的群聊ID
flask = Flask(__name__)  # 提供天猫精灵平台的HTTP回调接口

@flask.route('/aligenie', methods=['POST'])
def aligenie():
    reply = Reply()
    reply.type = ReplyType.TEXT
    reply.content = 'Hello, Aligenie!'
    channel = channel_factory.create_channel('wx')
    for group in groups:
        context = Context(ContextType.TEXT, '', {'receiver': group})
        channel.send(reply, context)
    return 'OK'

def run():  # 启动Flask的HTTP服务器
    flask.run(port=5000)

threading.Thread(target=run).start()
