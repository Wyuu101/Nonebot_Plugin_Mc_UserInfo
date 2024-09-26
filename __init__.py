from nonebot import get_driver
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="plugin_mc_userinfo",
    description="",
    usage="",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)



#参考MC文档 https://geekdaxue.co/books/Minecraft-doc-zh
from nonebot import  on_command#调用消息检测模块
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
import requests
from datetime import datetime
import json
import base64

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39'}
hyp_apikey='4c3c2751-8fd8-4666-8bb1-13dcce0071de'
ornaments_api='https://sessionserver.mojang.com/session/minecraft/profile/'
used_name_api='https://api.mojang.com/user/profiles/'
uuid_api='https://api.mojang.com/users/profiles/minecraft/'


MC = on_command('MC',aliases={"mc", "Mc"},priority=10, block=True)
@MC.handle()
async def handle(args:Message=CommandArg()):

        if name:=args.extract_plain_text():
            global uuid_api,header
            uuid=''
            uuid_url = uuid_api + name
            response = requests.get(url=uuid_url, headers=header)
            if response.status_code == 200:
                data = response.json()
                if 'legacy' in data and data['legacy'] == 'true':
                    await MC.finish('✗未把账户迁移到mojang')
                else:
                    uuid= data['id']
                    name=data['name']
            elif response.status_code == 404:
                await MC.finish('✗错误:非正版账户')
            else:
                await MC.finish('✗错误:服务器未响应，稍后重试')
        else:
            await MC.finish('缺少参数[用户名称]')

        ornaments_url = ornaments_api + uuid
        response = requests.get(url=ornaments_url, headers=header)
        if response.status_code == 200:
            encode_data = response.json()['properties'][0]['value']
            decode_data = base64.b64decode(encode_data)
            date_dic = json.loads(decode_data)
            textures_dic = date_dic['textures']
            skin_url='*'
            cape_url='*'
            if 'SKIN' in textures_dic:
                skin_url= textures_dic['SKIN']['url']
                if 'metadata' in textures_dic['SKIN']:
                    arm_msg='✓手臂:纤细'
                else:
                    arm_msg = '✓手臂:粗壮'
            else:
                pass
            if 'CAPE' in textures_dic:
                cape_url=textures_dic['CAPE']['url']
            else:
                pass
        else:
            await MC.finish('✗请求皮肤错误')

        if skin_url!='*' and cape_url!='*':
            message=Message('---------用户档案---------\n')+Message(f'✓玩家ID:\n{name}\n')+Message('✓皮肤:\n')+Message(MessageSegment.image(skin_url))+Message('\n')+Message('✓披风:\n')+Message(MessageSegment.image(cape_url))+Message('\n')+Message(arm_msg)+Message('\n------数据来自Mojang------')
        elif skin_url=='*' and cape_url!='*':
            message=Message('---------用户档案---------\n')+Message(f'✓玩家ID:\n{name}\n')+Message('✗皮肤:')+Message('未查找到')+Message('\n')+Message('✓披风:\n')+Message(MessageSegment.image(cape_url))+Message('\n')+Message(arm_msg)+Message('\n------数据来自Mojang------')
        elif skin_url!='*' and cape_url=='*':
            message=Message('---------用户档案---------\n')+Message(f'✓玩家ID:\n{name}\n')+Message('✓皮肤:\n')+Message(MessageSegment.image(skin_url))+Message('\n')+Message('✗披风:')+Message('未查找到')+Message('\n')+Message(arm_msg)+Message('\n------数据来自Mojang------')
        await MC.finish(message=message)

