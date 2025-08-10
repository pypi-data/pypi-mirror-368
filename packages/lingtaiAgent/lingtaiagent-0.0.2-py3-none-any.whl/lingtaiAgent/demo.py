from lingtaiAgent.lingtai import LingtaiBot,lingtaiAgent_logger

lingtaiBot = LingtaiBot(bot_identity="钉钉_一飞的机器人")
lingtaiBot.receivingInterval = 30

@lingtaiBot.msg_register()
def msg_register(msg):
    lingtaiAgent_logger.info("收到消息：", msg)
    # 此处编写各种处理逻辑
    lingtaiBot.send_text("你好，世界")
    lingtaiBot.set_robot_message_done(msg["id"])

if __name__ == '__main__':
    lingtaiBot.start_receiving()
    lingtaiBot.run()