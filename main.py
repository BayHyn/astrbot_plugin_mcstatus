from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from mcstatus import JavaServer
from mcstatus.status_response import JavaStatusResponse

@register("mcstatus", "WhiteCloudCN", "一个获取MC服务器状态的插件", "1.0.0")
class mcstatus(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def get_server_status(self, server_addr: str):
        try:
            if ":" not in server_addr:
                server_addr = f"{server_addr}:25565"
            
            server = JavaServer.lookup(server_addr)
            status = await server.async_status()
            
            if hasattr(status.description, 'to_plain'):
                motd = status.description.to_plain()
            elif hasattr(status.description, 'to_minecraft'):
                motd = status.description.to_minecraft()
            else:
                motd = str(status.description)

            # TODO 添加颜色
            import re
            motd = re.sub(r'§[0-9a-fk-or]', '', motd)
            
            return {
                'online': status.players.online,
                'max': status.players.max,
                'latency': round(status.latency, 2),
                'motd': motd,
                'version': status.version.name
            }
        except Exception as e:
            logger.error(f"获取服务器状态出错, 原因: {str(e)}")
            return None

    @filter.command("motd")
    async def mcmotd(self, event: AstrMessageEvent):
        """获取JE服务器MOTD"""
        message = event.message_str
        message_parts = message.split(' ', 1)

        if len(message_parts) < 2:
            yield event.plain_result("❌格式错误！正确用法：/motd 服务器地址")
            return
        
        server_addr = message_parts[1].strip()
        
        yield event.plain_result(f"⏳ 正在查询服务器【{server_addr}】的状态...")
        
        server_status = await self.get_server_status(server_addr)
        
        if server_status is not None:
            result = (
                f"✅ 服务器【{server_addr}】状态：\n"
                f"📋 版本: {server_status['version']}\n"
                f"👥 玩家: {server_status['online']}/{server_status['max']}\n"
                f"📶 延迟: {server_status['latency']}ms\n"
                f"📝 MOTD: {server_status['motd']}"
            )
            yield event.plain_result(result)
        else:
            yield event.plain_result(f"❌ 无法获取服务器【{server_addr}】的状态\n"
                                  "请检查：\n"
                                  "1. 服务器地址是否正确\n"
                                  "2. 服务器是否在线\n"
                                  "3. 端口是否正确（默认25565）")