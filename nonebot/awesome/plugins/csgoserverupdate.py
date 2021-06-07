import nonebot
import aiohttp
import valve.rcon
import os
import re

server_url = ('', 27015)
rconpass = ''
link = 'https://api.steampowered.com/ISteamApps/UpToDateCheck/v1/'
data = {
    'appid' : '730',
    'version' : '',
}
valve.rcon.RCONMessage.ENCODING = 'utf-8'

@nonebot.on_command('更新', aliases=('服务器更新'), only_to_me=0)
async def update_server(session: nonebot.CommandSession):
    rcon_info = valve.rcon.execute(server_url, rconpass, 'status')
    version = re.findall(r'version.*?/(.*?) ', rcon_info)[0]
    data['version'] = version
    async with aiohttp.ClientSession() as httpsession:
        async with httpsession.get(link, params=data) as response:
            res = await response.json()
    if res['response']['up_to_date']:
        await session.send(f'已经是最新版本:{version}')
    else:
        await session.send(
            '开始更新，预计需要等待 3-5 分钟，去看会b站吧。\n'
            '进入服务器前请先输入“状态”查询。'
        )
        await update_sh()


async def update_sh():
    status = os.system('expect ./update.sh')
    print(status)
