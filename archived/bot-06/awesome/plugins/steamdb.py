import nonebot.argparse
import time
import motor.motor_asyncio
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


async def get_maxtimegame_info(qq = '0', steamid64 = '0'):
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    if (qq == '0'):
        userdata = await usercollection.find_one({'steamid64':steamid64})
    else:
        userdata = await usercollection.find_one({'qq':qq})
    appslist = []
    timelist = []
    addition = ''
    for comps in userdata['steamdata']['gamedata']:
        appslist.append(comps['appid'])
        timelist.append(comps['playtime'])
    timelistInt = list(map(int, timelist))
    maxtimegameindex = timelistInt.index(max(timelistInt))
    maxtimegameid = appslist[maxtimegameindex]
    maxtimegamehour = int(timelistInt[maxtimegameindex] / 60)
    if (maxtimegamehour == 0):
        addition = '，请在steam个人资料页面公开游戏时长之后输入“刷新”'
    maxtimegamename = await get_game_name(maxtimegameid)
    return (f'游玩时间最长的是 {maxtimegamename}, 共游玩 {maxtimegamehour} 个小时{addition}')


async def send_userinfo(qq = '0', steamid64 = '0'):
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    if (qq == '0'):
        userdata = await usercollection.find_one({'steamid64':steamid64})
        if (userdata == None):
            return 0
    else:
        userdata = await usercollection.find_one({'qq':qq})
        if (userdata == None):
            return 0
    personaname = userdata['steamdata']['nickname']
    if (userdata['steamdata']['createdtime'] != 0):
        createdtime = await get_time_from_timestamp(userdata['steamdata']['createdtime'])
    if ('refreshtime' in userdata['steamdata']):
        refreshtime = await get_time_from_timestamp(userdata['steamdata']['refreshtime'])
    else:
        refreshtime = 0
    gamesnums = userdata['steamdata']['gamesnums']
    maxtimegameword = await get_maxtimegame_info(qq=qq, steamid64=steamid64)
    # Construct returnword
    returnword = f'{personaname}'
    if (userdata['steamdata']['createdtime'] != 0):
        returnword = returnword + f'\n账号创建时间:{createdtime}'
    returnword = returnword + f'\n拥有{gamesnums}个游戏\n{maxtimegameword}'
    if (refreshtime != 0):
        returnword = returnword + f'\n资料刷新时间:{refreshtime}'
    return (returnword)
    


async def get_time_from_timestamp(timestamp: str):
    timearray = time.localtime(float(timestamp))
    strtime = time.strftime('%Y-%m-%d %H:%M:%S', timearray)
    return strtime


async def get_game_name(appid: str):
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    steam_app = client['steamdata']['app']
    record = await steam_app.find_one({'appid':appid})
    return record['name']


async def refresh_info(qq = '0', steamid64 = '0'):
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    if (qq == '0'):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(user_link, params=user_paras) as response:
            req = await response.json()
            if (req['response']['players'] == []):
                return (f'用户不存在，请检查你输入的id或链接')
            user_req = req
        async with session.get(games_link, params=games_paras) as response:
            req = await response.json()
            games_req = req
    # Judge whether createtime exists or not
    if (user_req['response']['players'][0]['timecreated'] != []):
        timestamp = str(user_req['response']['players'][0]['timecreated'])
    else:
        timestamp = 0
    personaname = user_req['response']['players'][0]['personaname']
    gamesnums = games_req['response']['game_count']
    gameslist = games_req['response']['games']
    gamesid = []
    gamestime = []
    for games in gameslist:
        gamesid.append(str(games['appid']))
        gamestime.append(games['playtime_forever'])
    totalgamestime = (sum(gamestime) / 60)
    curtimestamp = str(time.time())
    gamedata = []
    for index in range(len(gamesid)):
        gamedata.append({
            'appid':gamesid[index],
            'playtime':str(gamestime[index])     # minute
        })
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
    maxtimegameword = await get_maxtimegame_info(qq=qq, steamid64=steamid64)
    refreshtime = await get_time_from_timestamp(curtimestamp)
    # Construct returnword
    returnword = f'昵称:{personaname}'
    if (timestamp != 0):
        returnword = returnword + f'\n创建日期:{createdtime}'
    returnword = returnword + f'\n拥有{gamesnums}个游戏\n{maxtimegameword}，游戏总时长{totalgamestime}小时'
    returnword = returnword + f'\n资料刷新时间:{refreshtime}'
    return returnword


@nonebot.on_command('绑定', only_to_me=0)
async def bind(session: nonebot.CommandSession):
    qq_id = str(session.event['user_id'])
    match_res = await send_userinfo(qq_id)
    if (match_res == 0):
        accinfo = session.get('accinfo', prompt='请输入steam64位id')
        word_back = await deal_accinfo(accinfo, qq_id)
        await session.send(word_back)
    else:
        await session.send(f'账号已经绑定')


@nonebot.on_command('资料', only_to_me=0)
async def get_info(session: nonebot.CommandSession):
    qq_id = str(session.event['user_id'])
    match_res = await send_userinfo(qq_id)
    if (match_res == 0):
        await session.send(f'未找到steamid，请先输入“绑定”')
    else:
        await session.send(match_res)


@nonebot.on_command('解绑', only_to_me=0)
async def disconnect(session: nonebot.CommandSession):
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    qq_id = str(session.event['user_id'])
    match_res = await send_userinfo(qq_id)
    if (match_res == 0):
        await session.send(f'未找到steamid，请先输入“绑定”')
    else:
        usercollection = client['steamdb']['user']
        userdata = await usercollection.find_one({'qq':qq_id})
        steamid64 = userdata['steamid64']
        await usercollection.delete_one({'qq':qq_id})
        await session.send(f'已解除对{steamid64}的绑定。')


@nonebot.on_command('刷新', only_to_me=0)
async def refresh(session: nonebot.CommandSession):
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    qq_id = str(session.event['user_id'])
    usercollection = client['steamdb']['user']
    match_res = await usercollection.find_one({'qq':qq_id})
    if (match_res == None):
        await session.send(f'未找到steamid，请先输入“绑定”')
    else:
        steamid64 = match_res['steamid64']
        user_name = match_res['steamdata']['nickname']
        await refresh_info(qq_id, steamid64)
        curtime = await get_time_from_timestamp(str(time.time()))
        await session.send(f'于{curtime}完成对{user_name}资料的刷新')


@nonebot.on_command('查询账号', only_to_me=0)
async def querysteamid(session: nonebot.CommandSession):
    accinfo = session.get('accinfo', prompt='请输入steam64位id')
    client = motor.motor_asyncio.AsyncIOMotorClient(mongolink)
    usercollection = client['steamdb']['user']
    match_res = await usercollection.find_one({'steamid64':accinfo})
    if (match_res == None):
        word_back = await deal_accinfo(accinfo)
        await session.send(word_back)
    else:
        word_back = await send_userinfo(steamid64=accinfo)
        await session.send(word_back)


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


async def deal_accinfo(accinfo = '0', qq = '0'):
    # steamid_pattern = r'steamcommunity'
    accinfo = accinfo.strip()
    if (accinfo.isdigit() and len(accinfo) == 17):
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
    if (qq == '0'):
        return(returnword)
    returnword = '绑定成功!\n' + returnword 
    return (returnword)