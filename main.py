import random
from astrbot.api.all import Star, Context, logger, AstrBotConfig, filter
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
class 消息回应(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        def 解析表情回应ID列表(raw:str):
            if not raw:
                return []
            try:
                return [ int(i) for i in ','.join(raw.split()).replace('，', ',').split(',') if i ]
            except Exception as e:
                logger.error(f"解析表情ID列表失败：{e}", exc_info=True)
                return []

        唤醒时回应 = config['唤醒时回应']
        self.私聊唤醒时回应方式 = 唤醒时回应['私聊回应方式']
        self.群聊唤醒时回应方式 = 唤醒时回应['群聊回应方式']
        self.唤醒时贴表情ID列表 = 解析表情回应ID列表(唤醒时回应.get('贴表情ID列表'))
        if self.群聊唤醒时回应方式 == '贴表情' and not self.唤醒时贴表情ID列表:
            logger.error("唤醒时回应选择了贴表情，但未填写有效的表情ID，该功能将关闭")
            self.群聊唤醒时回应方式 = '关闭'

        llm请求前回应 = config['llm请求前回应']
        self.私聊llm请求前回应方式 = llm请求前回应['私聊回应方式']
        self.群聊llm请求前回应方式 = llm请求前回应['群聊回应方式']
        self.llm请求前贴表情ID列表 = 解析表情回应ID列表(llm请求前回应.get('贴表情ID列表'))
        if self.群聊llm请求前回应方式 == '贴表情' and not self.llm请求前贴表情ID列表:
            logger.error("llm请求前回应选择了贴表情，但未填写有效的表情ID，该功能将关闭")
            self.群聊llm请求前回应方式 = '关闭'

        消息回复完成时 = config['消息回复完成时']
        self.私聊消息回复完成时回应方式 = 消息回复完成时['私聊回应方式']
        self.群聊消息回复完成时回应方式 = 消息回复完成时['群聊回应方式']
        self.消息回复完成时贴表情ID列表 = 解析表情回应ID列表(消息回复完成时.get('贴表情ID列表'))
        if self.群聊消息回复完成时回应方式 == '贴表情' and not self.消息回复完成时贴表情ID列表:
            logger.error("消息回复完成时回应选择了贴表情，但未填写有效的表情ID，该功能将关闭")
            self.群聊消息回复完成时回应方式 = '关闭'

    @filter.on_waiting_llm_request()
    async def llm队列时(self, event: AiocqhttpMessageEvent, *_, **__):
        """进入llm请求队列时执行响应策略（唤醒后）"""
        if not isinstance(event, AiocqhttpMessageEvent):
            return
        if event.get_group_id():
            if self.群聊唤醒时回应方式 == '关闭':
                return
            elif self.群聊唤醒时回应方式 == '戳一戳':
                await self.戳一戳(event)
            elif self.群聊唤醒时回应方式 == '贴表情':
                await self.贴表情(event, random.choice(self.唤醒时贴表情ID列表))
            else:
                return
        else:
            if self.私聊唤醒时回应方式 == '关闭':
                return
            elif self.私聊唤醒时回应方式 == '戳一戳':
                await self.戳一戳(event)
            else:
                return

    @filter.on_llm_request()
    async def llm请求前(self, event: AiocqhttpMessageEvent, *_, **__):
        """llm请求前执行响应策略"""
        if not isinstance(event, AiocqhttpMessageEvent):
            return
        if event.get_group_id():
            if self.群聊llm请求前回应方式 == '关闭':
                return
            elif self.群聊llm请求前回应方式 == '戳一戳':
                await self.戳一戳(event)
            elif self.群聊llm请求前回应方式 == '贴表情':
                await self.贴表情(event, random.choice(self.llm请求前贴表情ID列表))
            else:
                return
        else:
            if self.私聊llm请求前回应方式 == '关闭':
                return
            elif self.私聊llm请求前回应方式 == '戳一戳':
                await self.戳一戳(event)
            else:
                return

    @filter.after_message_sent()
    async def 消息发送后(self, event: AiocqhttpMessageEvent, *_, **__):
        """消息发送后执行相应策略"""
        if not isinstance(event, AiocqhttpMessageEvent):
            return
        result = event.get_result()
        if not result.is_model_result():
            return
        if event.get_group_id():
            if self.群聊消息回复完成时回应方式 == '关闭':
                return
            elif self.群聊消息回复完成时回应方式 == '戳一戳':
                await self.戳一戳(event)
            elif self.群聊消息回复完成时回应方式 == '贴表情':
                await self.贴表情(event, random.choice(self.消息回复完成时贴表情ID列表))
            else:
                return
        else:
            if self.私聊消息回复完成时回应方式 == '关闭':
                return
            elif self.私聊消息回复完成时回应方式 == '戳一戳':
                await self.戳一戳(event)
            else:
                return

    @staticmethod
    async def 贴表情(event: AiocqhttpMessageEvent, face_id: int):
        """对该事件的消息贴表情"""
        msg_id = event.message_obj.raw_message.get("message_id")
        if not msg_id:
            logger.warning("贴表情未找到有效消息ID")
            return

        try:
            result = await event.bot.call_action(
                action="set_msg_emoji_like",
                message_id=msg_id,
                emoji_id=face_id,
                set=True
            )
            return result
        except Exception as e:
            logger.error(f"群{event.get_group_id()}，消息「{event.get_message_outline()}」贴表情失败：{e}", exc_info=True)

    @staticmethod
    async def 戳一戳(event: AiocqhttpMessageEvent):
        """对该事件的发送者戳一戳"""
        user_id = event.get_sender_id()
        try:
            if event.get_group_id():
                result = await event.bot.call_action(
                    action="group_poke",
                    group_id=event.get_group_id(),
                    user_id=user_id
                )
            else:
                result = await event.bot.call_action(
                    action="friend_poke",
                    user_id=user_id
                )
            return result
        except Exception as e:
            if event.get_group_id():
                _id = f"群{event.get_group_id()}"
            else:
                _id = f"私聊{user_id}"
            logger.error(f"{_id}，消息「{event.get_message_outline()}」戳一戳失败：{e}", exc_info=True)