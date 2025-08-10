import logging, sys, requests, base64, threading, time, queue, hashlib

def _get_logger(logname):
    log = logging.getLogger(logname)
    log.setLevel(logging.INFO)
    console_handle = logging.StreamHandler(sys.stdout)
    console_handle.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s',
                                                  datefmt='%Y-%m-%d %H:%M:%S'))
    log.addHandler(console_handle)
    return log

lingtaiAgent_logger = _get_logger("lingtaiAgent")

class LingtaiBot(object):
    # 信息初始化，需要传入 bot 的 bot_identity
    def __init__(self, bot_identity, base_url="https://lingtai.deeptest.fun"):
        self.bot_identity = bot_identity
        self.base_url = base_url
        self.receivingInterval = 5
        self.msgList = queue.Queue()
        self.functionDict = {'Msg': {}}

    # 启动进程
    def run(self):
        lingtaiAgent_logger.info("进程已启动")

        # 配置消息处理方法
        def reply_fn():
            lingtaiAgent_logger.info("开始配置消息处理函数")

            while True:
                try:
                    msg = self.msgList.get()
                except queue.Empty:
                    pass
                else:
                    replyFn = self.functionDict['Msg'].get("handler_msg")

                    if replyFn is None:
                        lingtaiAgent_logger.warning("消息处理函数缺失")
                    else:
                        try:
                            replyFn(msg)
                        except Exception as e:
                            lingtaiAgent_logger.warning("消息处理函数异常")
                            lingtaiAgent_logger.warning(e)

        # 启动消息处理
        replyThread = threading.Thread(target=reply_fn)
        replyThread.start()

    # 消息处理
    def msg_register(self):
        def _msg_register(fn):
            self.functionDict['Msg']['handler_msg'] = fn
            return fn
        return _msg_register

    # 接收消息
    def start_receiving(self):
        # 启动消息接收
        lingtaiAgent_logger.info("start_receiving")
        def maintain_loop():
            # 循环获取消息
            while True:
                lingtaiAgent_logger.info("每 {} 秒获取一次消息".format(self.receivingInterval))
                # 获取消息
                try:
                    received_msg_list = requests.request(
                        method="POST",
                        url="{}/api/v1/bot/getRobotMessage".format(self.base_url),
                        json={
                            "bot_identity":self.bot_identity,
                            "msg_status":"init"
                        },
                    ).json()["data"]
                except:
                    received_msg_list = []
                # received_msg_list = [{"text": "测试的文本消息1"}, {"text": "测试的文本消息2"}]
                lingtaiAgent_logger.info("消息内容为：{}".format(received_msg_list))
                # 如果时间线消息的数据不为空，则更新 lastId
                if len(received_msg_list) == 0:
                    pass
                else:
                    for msg in received_msg_list:
                        self.msgList.put(msg)
                time.sleep(self.receivingInterval)

        maintainThread = threading.Thread(target=maintain_loop)
        maintainThread.start()

    # 更改消息状态为已处理
    def set_robot_message_done(self, id):
        try:
            requests.request(
                method="POST",
                url="{}/api/v1/bot/updateRobotMessage".format(self.base_url),
                json={
                    "id": id,
                    "msg_status": "done"
                },
            )
            lingtaiAgent_logger.info("将消息「{}」状态置为已处理".format(id))
        except:
            lingtaiAgent_logger.error("将消息「{}」状态置为已处理失败".format(id))

    def send_text(self, text):
        try:
            requests.request(
                method="POST",
                url="{}/api/v1/bot/addRobotAction".format(self.base_url),
                json={
                    "bot_identity":self.bot_identity,
                    "action_name": "send_text",
                    "action_params": text
                },
            )
            lingtaiAgent_logger.info("发送消息[{}]成功".format(text))
        except:
            lingtaiAgent_logger.error("发送消息[{}]失败".format(text))
