import valve.rcon
import nonebot

valve.rcon.RCONMessage.ENCODING = 'utf-8'
url = ('', 27015)
rconpass = ''

@nonebot.on_command('换图', aliases='切换', only_to_me=0)
async def changelevel(session: nonebot.CommandSession):
    mapname = session.args['mapname']
    word_back = await rcon_con(mapname)
    await session.send(word_back)


@changelevel.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['mapname'] = stripped_arg
        return

    if not stripped_arg:
        session.send('?')


async def rcon_con(mapname:str) -> str:
    command = f'changelevel {mapname}'
    try :
        valve.rcon.execute(url, rconpass, command)
    except valve.rcon.RCONCommunicationError:
        req = f'已切换 {mapname}'
    else :
        req = f'未找到 {mapname}，请咨询群主'
    return(req)