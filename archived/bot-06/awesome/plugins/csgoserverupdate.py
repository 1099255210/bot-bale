import nonebot
import valve.rcon
import requests
import os
import re

valve.rcon.RCONMessage.ENCODING = 'utf-8'
url = ('', 27015)
rconpass = ''

@nonebot.on_command('更新', aliases=('服务器更新'), only_to_me=0)
async def update_server(session: nonebot.CommandSession):
    rconinfo = valve.rcon.execute(url, rconpass, 'status')
    version = re.findall(r'version.*?/(.*?) ', rconinfo)[0]
    link = 'https://api.steampowered.com/ISteamApps/UpToDateCheck/v1/'
    data = {
        'appid' : '730',
        'version' : version,
    }
    req = requests.get(link, params=data)
    req = req.json()
    if (req['response']['up_to_date'] == True):
        await session.send(f'已经是最新版本:{version}')
    else:
        await session.send('开始更新，预计需要等待 3-5 分钟，进入服务器前请先输入“状态”查询')
        await update_sh()


async def update_sh():
    status = os.system('expect ./update.sh')
    print(status)
