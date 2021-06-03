import nonebot
import a2s

server_address = ('', 27015)

@nonebot.on_command('状态', only_to_me=0)
async def status(session: nonebot.CommandSession):
    await session.send(await status_back())


@nonebot.on_command('得分', only_to_me=0)
async def score(session: nonebot.CommandSession):
    await session.send(await score_back())


async def score_back():
    players_info = await a2s.aplayers(server_address)
    if not players_info:
        return ('服务器无玩家')
    s_playerlist = ''.join(f'[{player.name}] -- {player.score}\n' for player in players_info)
    return (f'得分：\n{s_playerlist}')


async def status_back():
    try:
        server_info = await a2s.ainfo(server_address)
    except:
        return ('服务器不在运行或者正在更新')
    else:
        players_info = await a2s.aplayers(server_address)
        if not server_info.player_count:
            return (
                f'服务器状态：\n'
                f'地图：{server_info.map_name}\n'
                f'目前没有玩家在线。'
            )
        s_playerlist = ''.join(str(player) + '||' for player in players_info)
        return (
            f'服务器状态：\n'
            f'地图：{server_info.map_name}\n'
            f'人数：{server_info.player_count}\n'
            f'在线玩家(包括机器人)：||{s_playerlist}'
        )

