import nonebot
import requests

@nonebot.on_command('起名', aliases=('给个名字'), only_to_me=0)
async def givename(session: nonebot.CommandSession):
    await session.send(give_name())


async def give_name():
    key = ''
    reqlink = 'http://hn216.api.yesapi.cn/?s=App.Common_Nickname.RandOne' + f'&app_key={key}'
    rep = requests.get(reqlink)
    rep.encoding = 'utf-8'
    jsr = rep.json()
    return (jsr['data']['nickname'])

