from nonebot import *
import os
import aiofiles

bot = get_bot()

# @on_command('确实',aliases='[CQ:face,id=277]', only_to_me=False)
# async def weather(session: CommandSession):
#     weather_report = '确实'
#     await session.send(weather_report)


@bot.on_message("group")
async def re(context):
    msg = context["message"]
    s_msg = str(msg)
    # grp = context["group_id"]
    qq = context["user_id"]
    is_msg_match = await match(s_msg)
    if (is_msg_match):
        await bot.send_private_msg(user_id=qq,message=s_msg)


async def match(str):
    file_path = 'nonebot/bot-03/copy_data/word.txt'
    if (str == 'stop'):
        return 2
    if os.path.exists(file_path):
        async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if (str == line):
                    return 1
    return 0