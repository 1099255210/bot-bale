import nonebot
import os
import aiofiles
import requests

bot = nonebot.get_bot()
file_path = './copy_data/word.txt'

@nonebot.on_command('起名', aliases=('给个名字'), only_to_me=0)
async def givename(session: nonebot.CommandSession):
    name = await give_name()
    await session.send(name)


async def give_name():
    key = 'CD9E6C82490946375A30AED089EFA53C'
    reqlink = 'http://hn216.api.yesapi.cn/?s=App.Common_Nickname.RandOne' + f'&app_key={key}'
    rep = requests.get(reqlink)
    rep.encoding = 'utf-8'
    jsr = rep.json()
    return (jsr['data']['nickname'])

