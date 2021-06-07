import nonebot
import aiofiles
import re
import os
import random
import motor.motor_asyncio
import time

bot = nonebot.get_bot()
file_path = './pofang_data/pofang.txt'
patcq = r'\[CQ:.*?\]'

@bot.on_message('group')
async def record(context):
    msg = str(context['message'])
    if (msg == '破防了'):
        return
    grp = str(context['group_id'])
    qq = str(context['user_id'])
    curtimeint = int(time.time())
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['chatcache'][grp]
    await db.delete_many({})
    chat_info = {
        'qq' : qq,
        'msg' : msg,
        'timestampint' : curtimeint
    }
    await db.insert_one(chat_info)


@nonebot.on_command('破防了', only_to_me=0)
async def pofang(session: nonebot.CommandSession):
    grp = str(session.event['group_id'])
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['chatcache'][grp]
    cachedata = await db.find_one({})
    keyword = cachedata['msg']
    keyword_back = await pofang_word(keyword)
    await session.send(keyword_back)


async def pofang_word(keyword:str):
    if (len(keyword) > 50 or re.findall(patcq, keyword) != []):
        return (f'你怎么像个小丑一样')
    else:
        pfword = await get_random_word(keyword)
        return (pfword)


async def get_random_word(keyword:str):
    word = ''
    linesum = 0
    if os.path.exists(file_path):
        async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file_r:
            async for line in file_r:
                linesum += 1
        random.seed(int(time.time()))
        linenum = random.randint(1, linesum)
        async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file_r:
            async for line in file_r:
                curline = int(line.split('@')[0])
                if (linenum == curline):
                    word = line.split('@')[-1]
                    if (re.findall(r'\{keyword\}', word) == []):
                        return (word)
                    word = re.sub(r'\{keyword\}', keyword, word)
                    return (word)
