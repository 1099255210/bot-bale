import nonebot
import re
import time
import random
import aiofiles
import motor.motor_asyncio as amongo

bot = nonebot.get_bot()
file_path = './pofang_data/pofang.txt'
patcq = r'\[CQ:.*?\]'
patkeyword = r'\{keyword\}'

@bot.on_message('group')
async def record(context):
    grp, qq, msg = map(str, [context['group_id'], context['user_id'], context['message']])
    if msg != '破防了':
        client = amongo.AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['chatcache'][grp]
        await db.delete_many({})
        await db.insert_one({
            'qq' : qq,
            'msg' : msg,
            'timestampint' : int(time.time())
        })


@nonebot.on_command('破防了', only_to_me=0)
async def pofang(session: nonebot.CommandSession):
    grp = str(session.event['group_id'])
    client = amongo.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['chatcache'][grp]
    cachedata = await db.find_one({})
    await session.send(await pofang_word(cachedata['msg']))


async def pofang_word(keyword:str):
    if len(keyword) > 50 or re.search(patcq, keyword):
        return ('你怎么像个小丑一样')
    return (await get_random_word(keyword))


async def get_random_word(keyword:str):
    random.seed(int(time.time()))
    word = ''
    linesum = 0
    async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file_r:
        async for line in file_r:
            linesum += 1
    linenum = random.randint(1, linesum)
    async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file_r:
        async for line in file_r:
            curline = int(line.split('@')[0])
            if linenum == curline:
                word = line.split('@')[-1]
                if re.search(patkeyword, word):
                    word = re.sub(patkeyword, keyword, word)
                return (word)

