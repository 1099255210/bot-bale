import nonebot
import aiohttp
import motor.motor_asyncio as amongo
import time
from nonebot import session
from nonebot.command import CommandSession

mongostr = 'mongodb://localhost:27072'
url_user_info = 'https://api.bilibili.com/x/space/acc/info'
url_user_stat = 'https://api.bilibili.com/x/relation/stat'
user_mid = '434334701'
up_user_name = '七海Nana7mi'
user_para = {
    'mid' : user_mid,
}
user_para_fans = {
    'vmid' : user_mid,
}

bot = nonebot.get_bot()

@nonebot.on_command('粉丝数', only_to_me=0)
async def getfans(session:nonebot.CommandSession):
    res = await getjson(url_user_stat, user_para_fans)
    fan_num = res['data']['follower']
    await session.send(
        f'{up_user_name}现在有{fan_num}名粉丝。'
    )
    
@nonebot.scheduler.scheduled_job('interval',seconds=30)
async def check_liveroom_status():
    client = amongo.AsyncIOMotorClient(mongostr)
    db = client['liveroom'][user_mid]
    live_stat = await db.find_one()
    if not live_stat:
        db.insert_one({'live_status': 0})
        return
    live_status_d = live_stat['live_status']
    res = await getjson(url_user_info, user_para)
    room_info = res['data']['live_room']
    live_status = room_info['liveStatus']
    live_title = room_info['title']
    live_link = room_info['url']
    live_pic = room_info['cover']
    if (not live_status_d) and live_status:
        await bot.send_private_msg(
            user_id=1099255210,
            message=
            f'你关注的{up_user_name}开播啦，快去直播间看看吧！\n'
            f'直播标题间：{live_title}\n'
            # f'直播间封面：[CQ:image,file={live_pic}]'
            f'直播链接：{live_link}\n'
        )
        await db.update_one({'live_status': 0}, {'$set': {'live_status': 1, 'time': time.time()}})
        print('[nana7mibot] : liveroom opening.')
        return
    if live_status_d and live_status:
        print('[nana7mibot] : liveroom is open.')
        return
    if live_status_d and (not live_status):
        start_time = live_stat['time']
        end_time = time.time()
        seconds = end_time - start_time
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print ("%02d:%02d:%02d" % (h, m, s))
        live_time = f'{h}小时{m}分钟{s}秒'
        await bot.send_private_msg(
            user_id=1099255210,
            message=
            f'{up_user_name}关闭了直播间，今天的直播到此结束了，总计直播时长{live_time}。\n'
        )
        await db.update_one({'live_status': 1}, {'$set': {'live_status': 0}})
        print('[nana7mibot] : liveroom closing.')
        return
    print('[nana7mibot] : liveroom not open.')

async def getjson(link, param):
    '''
    Get json from [link, param].
    '''
    
    async with aiohttp.ClientSession() as httpsession:
        async with httpsession.get(link, params=param) as res:
            res_json = await res.json()
    return res_json
