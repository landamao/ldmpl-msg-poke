具体消息ID可参考[https://www.landamao.xyz/qq-face-id/face_list.html](https://www.landamao.xyz/qq-face-id/face_list.html)

## 贴表情的撤回

贴出去的表情是「处理中」的反馈。如果这条消息最终一条回复都没发出去（事件被 `/reset`、`/stop`
或其他插件终止，模型报错，空回复），插件会在事件收尾时把表情撤回；正常回复过的消息保留表情。

自动撤回依赖框架的事件收尾钩子 `on_event_completed`（ldm_AstrBot v4.27.56 起提供）。旧版框架上
插件照常加载，只是不会撤回。撤回用的是同一个 OneBot 接口 `set_msg_emoji_like` 带 `set=false`，
需要协议端支持（NapCat / Lagrange 均支持）。
