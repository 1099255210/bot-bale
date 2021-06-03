import nonebot.argparse
import time
import motor.motor_asyncio as amongo
import aiohttp

mongolink = 'mongodb://localhost'
user_link = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
games_link = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
apikey = ''
user_paras = {
    'key' : apikey,
    'steamids' : '',
}
games_paras = {
    'key' : apikey,
    'steamid' : '',
}

@nonebot.on_command('绑定', only_to_me=0)
async def bind(session: nonebot.CommandSession):
    qq_id = str(session.event['user_id'])
    match_res = await send_userinfo(qq_id)
    if not match_res:
        accinfo = session.get('accinfo', prompt='请输入steam64位id')
        await session.send(await deal_accinfo(accinfo, qq_id))
    else:
        await session.send('账号已经绑定')


@nonebot.on_command('资料', only_to_me=0)
async def get_info(session: nonebot.CommandSession):
    qq_id = str(session.event['user_id'])
    match_res = await send_userinfo(qq_id)
    if not match_res:
        await session.send('未找到steamid，请先输入“绑定”')
    else:
        await session.send(match_res)


@nonebot.on_command('解绑', only_to_me=0)
async def disconnect(session: nonebot.CommandSession):
    qq_id = str(session.event['user_id'])
    match_res = await send_userinfo(qq_id)
    if not match_res:
        await session.send(f'未找到steamid，请先输入“绑定”')
        return
    client = amongo.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    userdata = await usercollection.find_one({'qq':qq_id})
    steamid64 = userdata['steamid64']
    await usercollection.delete_one({'qq':qq_id})
    await session.send(f'已解除对{steamid64}的绑定。')


@nonebot.on_command('刷新', only_to_me=0)
async def refresh(session: nonebot.CommandSession):
    qq_id = str(session.event['user_id'])
    client = amongo.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    match_res = await usercollection.find_one({'qq':qq_id})
    if not match_res:
        await session.send(f'未找到steamid，请先输入“绑定”')
        return
    steamid64 = match_res['steamid64']
    user_name = match_res['steamdata']['nickname']
    await refresh_info(qq_id, steamid64)
    curtime = await get_time_from_timestamp(str(time.time()))
    await session.send(f'于{curtime}完成对{user_name}资料的刷新')


@nonebot.on_command('查询账号', only_to_me=0)
async def querysteamid(session: nonebot.CommandSession):
    accinfo = session.get('accinfo', prompt='请输入steam64位id')
    client = amongo.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    match_res = await usercollection.find_one({'steamid64':accinfo})
    if not match_res:
        await session.send(await deal_accinfo(accinfo))
    else:
        word_back = await send_userinfo(steamid64=accinfo)
        await session.send(word_back)


async def get_maxtimegame_info(qq = '', steamid64 = ''):
    client = amongo.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    if not qq:
        userdata = await usercollection.find_one({'steamid64':steamid64})
    else:
        userdata = await usercollection.find_one({'qq':qq})
    appslist = [comps['appid'] for comps in userdata['steamdata']['gamedata']]
    timelist = [comps['playtime'] for comps in userdata['steamdata']['gamedata']]
    gametimelist_int = list(map(int, timelist))
    maxtimegameindex = gametimelist_int.index(max(gametimelist_int))
    maxtimegameid = appslist[maxtimegameindex]
    maxtimegamehour = int(gametimelist_int[maxtimegameindex] / 60)
    addition_word = ''
    if not maxtimegamehour:
        addition_word = '，请在steam个人资料页面公开游戏时长之后输入“刷新”'
    maxtimegamename = await get_game_name(maxtimegameid)
    return (f'游玩时间最长的是 {maxtimegamename}, 共游玩 {maxtimegamehour} 个小时{addition_word}')


async def send_userinfo(qq = '', steamid64 = ''):
    client = amongo.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    if not qq:
        userdata = await usercollection.find_one({'steamid64':steamid64})
        if not userdata:
            return 0
    else:
        userdata = await usercollection.find_one({'qq':qq})
        if not userdata:
            return 0
    personaname = userdata['steamdata']['nickname']
    if userdata['steamdata']['createdtime']:
        createdtime = await get_time_from_timestamp(userdata['steamdata']['createdtime'])
    refreshtime = 0
    if 'refreshtime' in userdata['steamdata']:
        refreshtime = await get_time_from_timestamp(userdata['steamdata']['refreshtime'])
    gamesnums = userdata['steamdata']['gamesnums']
    maxtimegameword = await get_maxtimegame_info(qq=qq, steamid64=steamid64)
    # Construct returnword
    returnword = f'{personaname}'
    if userdata['steamdata']['createdtime']:
        returnword = returnword + f'\n账号创建时间:{createdtime}'
    returnword = returnword + f'\n拥有{gamesnums}个游戏\n{maxtimegameword}'
    if refreshtime:
        returnword = returnword + f'\n资料刷新时间:{refreshtime}'
    return (returnword)


async def refresh_info(qq = '', steamid64 = ''):
    client = amongo.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    if not qq:
        await usercollection.delete_one({'steamid64':steamid64})
        user_info = {
            'steamid64' : steamid64
        }
    else:
        await usercollection.delete_one({'qq':qq})
        user_info = {
            'qq' : qq,
            'steamid64' : steamid64                        
        }
    async with aiohttp.ClientSession() as httpsession:
        async with httpsession.get(user_link, params=user_paras) as response:
            req = await response.json()
            if not req['response']['players']:
                return (f'用户不存在，请检查你输入的id或链接')
            user_req = req
        async with httpsession.get(games_link, params=games_paras) as response:
            req = await response.json()
            games_req = req
    # Judge whether createtime exists or not
    timestamp = 0
    if user_req['response']['players'][0]['timecreated']:
        timestamp = str(user_req['response']['players'][0]['timecreated'])
    personaname = user_req['response']['players'][0]['personaname']
    gamesnums = games_req['response']['game_count']
    gameslist = games_req['response']['games']
    gamesid = [str(games['appid']) for games in gameslist]
    gamestime = [str(games['playtime_forever']) for games in gameslist]
    totalgamestime = int(sum(list(map(int, gamestime))) / 60)
    curtimestamp = str(time.time())
    gamedata = [{
        'appid' : gamesid[index],
        'playtime' : str(gamestime[index])     # minute
    } for index in range(len(gamesid))]
    user_info['steamdata'] = {
        'nickname' : personaname,
        'createdtime' : timestamp,
        'refreshtime' : curtimestamp,
        'gamesnums' : gamesnums,
        'gamedata' : gamedata,
        'totalgamestime' : totalgamestime
    }
    await usercollection.insert_one(user_info)
    createdtime = await get_time_from_timestamp(timestamp)
    maxtimegameword = await get_maxtimegame_info(qq=qq,steamid64=steamid64)
    refreshtime = await get_time_from_timestamp(curtimestamp)
    # Construct returnword
    returnword = f'昵称:{personaname}'
    if timestamp:
        returnword += f'\n创建日期:{createdtime}'
    returnword += f'\n拥有{gamesnums}个游戏\n{maxtimegameword}，游戏总时长{totalgamestime}小时'
    returnword += f'\n资料刷新时间:{refreshtime}'
    return returnword


async def deal_accinfo(accinfo = '', qq = ''):
    # steamid_pattern = r'steamcommunity'
    accinfo = accinfo.strip()
    if accinfo.isdigit() and len(accinfo) == 17:
        steamid64 = accinfo
    # elif (re.findall(steamid_pattern, accinfo) != []):
    #     link = accinfo + '?xml=1'
    #     xml_req = requests.get(link).content.decode('utf-8')
    #     xml_info = re.findall(r'<steamID64>(.*?)</steamID64>', xml_req)[0]
    #     steamid64 = str(xml_info).strip()
    else:
        return (f'非法输入，请检查你输入的id')
    # Get steamid64.
    user_paras['steamids'] = steamid64
    games_paras['steamid'] = steamid64
    # Get id verified plus get user_info.
    returnword = await refresh_info(qq, steamid64)
    if not qq:
        return(returnword)
    return ('绑定成功!\n' + returnword)


async def get_time_from_timestamp(timestamp: str):
    return (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(timestamp))))


async def get_game_name(appid: str):
    client = amongo.AsyncIOMotorClient(mongolink)
    steam_app = client['steamdata']['app']
    record = await steam_app.find_one({'appid':appid})
    return record['name']


@querysteamid.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['accinfo'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('输入为空，请重新输入')

    session.state[session.current_key] = stripped_arg


@bind.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['accinfo'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('输入为空，请重新输入')

    session.state[session.current_key] = stripped_arg