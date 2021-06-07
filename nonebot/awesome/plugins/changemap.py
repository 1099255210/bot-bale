import valve.rcon
import nonebot

valve.rcon.RCONMessage.ENCODING = 'utf-8'
url = ('', 27015)
rconpass = ''

@nonebot.on_command('换图', aliases='切换', only_to_me=0)
async def changelevel(session: nonebot.CommandSession):
    mapname = session.current_arg_text.strip()
    if mapname:
        await session.send(await rcon_con(mapname))
    else:
        await session.send('命令格式为：\n换图/切换 地图名')


async def rcon_con(mapname:str) -> str:
    try:
        valve.rcon.execute(url, rconpass, f'changelevel {mapname}')
    except valve.rcon.RCONCommunicationError:
        return(f'已切换 {mapname}')
    else:
        return(f'未找到 {mapname}，请咨询群主')