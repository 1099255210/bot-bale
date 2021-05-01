import nonebot
import os
import aiofiles

bot = nonebot.get_bot()

@bot.on_message("group")
async def re(context):
    msg = context["message"]
    s_msg = str(msg)
    grp = context["group_id"]
    # qq = context["user_id"]
    is_msg_match = await match(s_msg)
    if (is_msg_match):
        await bot.send_group_msg(group_id=grp,message=s_msg)
        # await bot.send_private_msg(user_id=qq,message=s_msg)


async def match(str):
    file_path = 'nonebot/bot-03/copy_data/word.txt' # 路径请根据系统修改
    if (str == 'stop'):
        return 2
    if os.path.exists(file_path):
        async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if (str == line):
                    return 1
    return 0