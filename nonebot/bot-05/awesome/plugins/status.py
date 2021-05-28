import nonebot
import re
import a2s

bot = nonebot.get_bot()
server_address = ('', 27015)

@nonebot.on_command('状态', aliases=('服务器'), only_to_me=0)
async def status(session: nonebot.CommandSession):
    s_status = await status_back()
    await session.send(s_status)

@nonebot.on_command('得分', only_to_me=0)
async def score(session: nonebot.CommandSession):
    s_score = await score_back()
    await session.send(s_score)


async def score_back():
    players_info = await a2s.aplayers(server_address)
    s_playerlist = '得分：\n'
    for player in players_info:
        s_playerlist = s_playerlist + f'[{player.name}] - player.score\n'
    return (f'{s_playerlist}')


async def status_back():
    try:
        server_info = await a2s.ainfo(server_address)
    except:
        return (f'服务器不在运行')
    else:
        players_info = await a2s.aplayers(server_address)
        s_map = server_info.map_name
        s_players = server_info.player_count
        if (s_players == 0):
            s_playerlist = ''
        else:
            s_playerlist = '||'
            for player in players_info:
                s_playerlist = s_playerlist + player.name + '||'
        return (f'服务器状态：\n地图：{s_map}\n人数：{s_players}\n在线玩家(包括机器人)：{s_playerlist}')

