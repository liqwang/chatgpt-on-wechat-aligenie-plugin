import plugins, threading
from flask import Flask, request, jsonify, send_file
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
channel = channel_factory.create_channel('wx')

@flask.route('/aligenie/<file>', methods=['GET'])
def aligenie(file):
    return send_file(f'{file}', as_attachment=True)

# https://aligenie.com/doc/20255408/mxi8t9
@flask.route('/voice', methods=['POST'])
def voice() -> flask.json:
    data: str = request.get_data(as_text=True)
    print(f'data: {data}')
    message = json.loads(data)
    text = message['utterance']
    reply = Reply()
    reply.type = ReplyType.TEXT
    reply.content = f'收到天猫精灵消息：\n{text}'
    for group in groups:
        context = Context(ContextType.TEXT, '', {'receiver': group})
        channel.send(reply, context)
    return jsonify({  # https://aligenie.com/doc/20255408/ehac4c
        'returnCode': '0',
        'returnErrorSolution': '',
        'returnMessage': '',
        'returnValue': {
            'reply': '消息发送成功！',
            'resultType': 'RESULT',
            'executeCode': 'SUCCESS'
        }
    })

def run():  # 启动Flask的HTTP服务器
    flask.run(host='0.0.0.0', port=80)

threading.Thread(target=run).start()
