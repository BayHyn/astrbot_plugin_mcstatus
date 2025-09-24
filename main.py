from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api import AstrBotConfig
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from .core.data_manager import DataManager
from .core.draw import Draw
from mcstatus import JavaServer
from mcstatus.status_response import JavaStatusResponse
import re,os

plguin_version = "1.0.0"

@register("mcstatus", "WhiteCloudCN", "一个获取MC服务器状态的插件", plguin_version)
class mcstatus(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.datamanager = DataManager()
        self.datamanager.load_config()
        self.bot_config = context.get_config()
        self.admin_list = self.bot_config["admins_id"]
        
    

    @staticmethod
    def check_server_addr(server_addr: str) -> bool:
        if not server_addr or len(server_addr) > 253:
            return False
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(:[1-9][0-9]{0,4}|:[1-5][0-9]{4}|:6[0-4][0-9]{3}|:65[0-4][0-9]{2}|:655[0-2][0-9]|:6553[0-5])?$'
        return bool(re.match(pattern, server_addr))

    async def get_server_status(self, server_addr: str):
        try:
            if ":" not in server_addr:
                server_addr = f"{server_addr}:25565"
            
            if not self.check_server_addr(server_addr):
                return None
            
            server = await JavaServer.async_lookup(server_addr)
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
                'server_addr':server_addr,
                'online': status.players.online,
                'max': status.players.max,
                'latency': round(status.latency, 2),
                'motd': motd,
                'version': status.version.name
            }
        except Exception as e:
            logger.error(f"获取服务器状态出错, 原因: {str(e)}")
            return None
        
    def to_string(self, server_status: dict) -> str:
        """
        格式化的状态字符串，如果状态数据为None则返回错误信息
        """
        if server_status is None:
            return (f"❌ 无法获取服务器的状态\n"
                                  "请检查：\n"
                                  "1. 服务器地址是否正确\n"
                                  "2. 服务器是否在线\n"
                                  "3. 端口是否正确（默认25565）")
        
        return (
            f"✅ 服务器【{server_status['server_addr']}】状态：\n"
                f"📋 版本: {server_status['version']}\n"
                f"👥 玩家: {server_status['online']}/{server_status['max']}\n"
                f"📶 延迟: {server_status['latency']}ms\n"
                f"📝 MOTD: {server_status['motd']}"
        )


    @filter.command("motd")
    async def motd(self, event: AstrMessageEvent, server_addr: str):
        """获取JE服务器MOTD"""
        if server_addr is not None:
            server_status = await self.get_server_status(server_addr)
            yield event.plain_result(self.to_string(server_status))
        else:
            yield event.plain_result("❌格式错误！正确用法：/motd 服务器地址")
        
            
    @filter.command("mcstatus")
    async def mcstatus(self,
                       event: AstrMessageEvent,
                       subcommand: str = None,
                       command_text_a: str = None,
                       command_text_b: str = None):
        """
        插件主函数,子命令motd,add,del,list
        """
        if subcommand is None:
            yield event.plain_result("❌缺少参数，请输入/mcstatus help查询用法")
        if(subcommand == "motd"):
            """获取motd"""
            if command_text_a is not None:
                server_addr = command_text_a
                server_status = await self.get_server_status(server_addr)
                yield event.plain_result(self.to_string(server_status))
            else:
                yield event.plain_result("❌格式错误！正确用法：/mcstatus motd 服务器地址")
        elif(subcommand == "add"):
            """添加{服务器名:服务器地址}"""
            if command_text_a is None or command_text_b is None:
                yield event.plain_result("❌格式错误！正确用法：/mcstatus add [服务器名(任意)] [服务器地址]")
                return
            server_name = command_text_a
            server_addr = command_text_b
            if self.datamanager.add_server_addr(server_name,server_addr):
                yield event.plain_result(f"✅服务器{server_name} 添加成功！")
            else:
                yield event.plain_result("❌添加失败，发生内部错误")
        elif(subcommand == "del"):
            """删除{服务器名:服务器地址}"""
            if command_text_a is not None:
                server_name = command_text_a
                if self.datamanager.remove_server_addr(server_name):
                    yield event.plain_result(f"✅服务器{server_name} 删除成功！")
                else:
                    yield event.plain_result("❌删除失败，发生内部错误")
            else:
                yield event.plain_result("❌格式错误！正确用法：/mcstatus del [服务器名]")
        
        # 查询 
        elif(subcommand == "look"):
            """查询服务器名 返回motd信息"""
            if command_text_a is not None:
                server_name = command_text_a
                server_status = await self.get_server_status(self.datamanager.get_server_addr(server_name))
                data = self.to_string(server_status)
                if data is not None:
                    yield event.plain_result(data)
                else:
                    yield event.plain_result("❌未找到服务器，请检查服务器地址")
            else:
                yield event.plain_result("❌格式错误！正确用法：/mcstatus look [服务器名]") 
        elif(subcommand == "set"):
            if command_text_a is None or command_text_b is None:
                yield event.plain_result("❌格式错误！正确用法：/mcstatus set [服务器名] [新服务器地址]")
                return
            server_name = command_text_a
            server_addr = command_text_b
            if self.datamanager.update_server_addr(server_name,server_addr):
                yield event.plain_result(f"{server_name}更新成功，新地址为{server_addr}")
                return
            else:
                yield event.plain_result(f"❌{server_name}更新失败，请检查：\n"
                                         f"1.名称是否存在\n"
                                         f"2.地址是否合法")
        elif(subcommand == "list"):
            data = self.datamanager.get_all_configs()
            if data is not None:
                result = "✅已存储服务器：\n"
                cnt = 1
                for key in data:
                    result+=f"{cnt}.{key}: {data[key]}\n"
                    cnt += 1
                yield event.plain_result(result)
            else:
                yield event.plain_result("🐸暂无存储服务器，请用/mcstatus add添加")
        elif(subcommand == "clear"):
            self.admin_list = self.bot_config["admins_id"]
            if event.get_sender_id() not in self.admin_list:
                yield event.plain_result(f"❌清空失败，杂鱼 {event.get_sender_name()}(id:{event.get_sender_id()}) 的权限不足还妄想清空呢~")
                return
            if self.datamanager.clear_all_configs():
                yield event.plain_result("✅清空成功")
            else:
                yield event.plain_result("❌清空失败，请重试或手动清理")
        elif(subcommand == "help"):
             yield event.plain_result(f"💕MCStatus 插件帮助[v{plguin_version}]\n"
                                     "/motd [服务器地址] (获取服务器MOTD状态信息)\n"
                                     "/mcstatus\n"
                                     " ├─ help (获取帮助)\n"
                                     " ├─ motd (同/motd)\n"
                                     " ├─ list (显示所有已存储服务器，默认显示第一页)\n"
                                     " ├─ add [名称] [服务器地址] (存储新服务器)\n"
                                     " ├─ del [名称] (删除服务器)\n" 
                                     " └─ clear (删除所有存储服务器，管理员命令)\n")
        else:
            yield event.plain_result("❌无相关指令，请输入/mcstatus help查询用法")

    @filter.command("draw")
    async def draw(self, event: AstrMessageEvent, message: str = None):
        """
        绘图命令（测试）
        """
        if message is None:
            final_text = "AstrBot Plugin@清蒸云鸭WhiteCloudCN\nDraw Default Message~"
        else:
            final_text = str(message).strip()
            if final_text == "":
                final_text = "AstrBot Plugin@清蒸云鸭WhiteCloudCN\nDraw Default Message~"
        
        drawing = Draw()
        drawing.create_image_with_text(final_text,seted_font=self.config["font"])
        
        if os.path.exists(drawing.output):
            yield event.image_result(drawing.output)
        else:
            yield event.plain_result("图片生成失败，请检查日志")


    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''