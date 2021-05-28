import nonebot
import os
import aiofiles
import random
import re

bot = nonebot.get_bot()
file_path = './copy_data/word.txt'
file_path_exp = './copy_data/exception.txt'
file_path_blacklist = './copy_data/blacklist.txt'
file_path_selfwords = './copy_data/selfwords.txt'
patcq = r'\[CQ:.*?\]'
patimg = r'\[CQ:image,file=(.*?).image.*\]'

@nonebot.on_command('学习', aliases=('复读'), only_to_me=0)
async def learn(session: nonebot.CommandSession):
    word = session.get('word', prompt='你想复读哪个词？')
    word_back = await learn_word(word)
    await session.send(word_back)


@nonebot.on_command('拉黑', only_to_me=0, permission=nonebot.permission.GROUP_OWNER)
async def ban(session: nonebot.CommandSession):
    user_id = session.get('userid', prompt='你想禁言谁？')
    ban_back = await ban_word(user_id)
    await session.send(ban_back)


@nonebot.on_command('恢复', only_to_me=0, permission=nonebot.permission.GROUP_OWNER)
async def recover(session: nonebot.CommandSession):
    user_id = session.get('userid', prompt='你想恢复谁？')
    recover_back = await recover_word(user_id)
    await session.send(recover_back)


@nonebot.on_command('忘记', aliases=('删除'), only_to_me=0)
async def forget(session: nonebot.CommandSession):
    word = session.get('word', prompt='你想忘记哪个词？')
    word_back = await forget_word(word)
    await session.send(word_back)


@ban.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['userid'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('用户为空，请重新输入')

    session.state[session.current_key] = stripped_arg


@recover.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['userid'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('用户为空，请重新输入')

    session.state[session.current_key] = stripped_arg


@forget.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['word'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('单词为空，请重新输入')

    session.state[session.current_key] = stripped_arg


@learn.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['word'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('单词为空，请重新输入')

    session.state[session.current_key] = stripped_arg


async def learn_word(word_raw:str) -> str:
    word_sub = word_raw
    shortened_str = re.sub(patcq, '', word_sub)
    finallen = len(shortened_str) + len(re.findall(patcq, word_sub))
    img = ''
    imglen = 0
    if (re.findall(patimg, word_raw) != []):
        imglen = len(re.findall(patimg, word_raw))
        img = re.findall(patimg, word_raw)[0]
        exc_img = re.sub(patcq, img, word_raw)
        word = exc_img
    else:
        word = word_raw

    if (finallen > 10):
        return (f'这么长，爷不学')
    if (imglen > 1):
        return (f'发这么多图，真行')
    res = await find_in_list(word)
    if (res == 2):
        return (f'{word}?我可不学。')
    if (res == 3):
        return (f'我天天都在说，别让我复读这个了')
    if (res == 1):
        return (f'这个我已经会了，爬')
    await save_word(word)
    return (f'已学习: {word_raw}')


async def forget_word(word_raw:str) -> str:
    flag = 0
    img = ''
    if (re.findall(patimg, word_raw) != []):
        img = re.findall(patimg, word_raw)[0]
        exc_img = re.sub(patcq, img, word_raw)
        word = exc_img
    else:
        word = word_raw
    if os.path.exists(file_path):
        async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file_r:
            lines = await file_r.readlines()
        async with aiofiles.open(file=file_path,mode='w',encoding='utf-8') as file_w:
            for line in lines:
                line_s = line.strip()
                if (line_s == word):
                    flag = 1
                    continue
                await file_w.write(line)
        if (flag == 1):
            return (f'已经忘记')
        else:
            return (f'我印象里好像没有{word_raw}')
    else:
        return (f'未找到单词表')


async def ban_word(user_id:str) -> str:
    if os.path.exists(file_path_blacklist):
        async with aiofiles.open(file=file_path_blacklist,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if (user_id == line):
                    return (f'拉黑过了')
        async with aiofiles.open(file=file_path_blacklist,mode='a+',encoding='utf-8') as file:
            await file.write(f'{user_id}\n')
            return (f'已经拉黑{user_id}')
    else:
        return (f'未找到单词表')


async def recover_word(user_id:str) -> str:
    flag = 0
    if os.path.exists(file_path_blacklist):
        async with aiofiles.open(file=file_path_blacklist,mode='r',encoding='utf-8') as file_r:
            lines = await file_r.readlines()
        async with aiofiles.open(file=file_path_blacklist,mode='w',encoding='utf-8') as file_w:
            for line in lines:
                line = line.strip()
                if (line == user_id):
                    flag = 1
                    continue
                await file_w.write(line)
        if (flag == 1):
            return (f'已解除对{user_id}的封禁')
        else:
            return (f'未在黑名单里找到此人')
    else:
        return (f'未找到单词表')



@bot.on_message("group")
async def receive_message(context):
    msg = context["message"]
    s_msg = str(msg)
    grp = context["group_id"]
    qq = context["user_id"]
    s_qq = str(qq)
    user_info = await bot.get_group_member_info(group_id=grp,user_id=qq)
    nickname = user_info['nickname']
    is_msg_match = await find_in_list(s_msg)
    is_id_match_blacklist = await matchid(s_qq)
    if (is_msg_match == 3):
        await bot.send_group_msg(group_id=grp,message=f'{nickname}，害搁这学我说话呢？')
    if (is_msg_match == 1 and is_id_match_blacklist != 1):
        await bot.send_group_msg(group_id=grp,message=f'{s_msg}')


async def find_in_list(word_raw:str):
    if (re.findall(patimg, word_raw) != []):
        img = re.findall(patimg, word_raw)[0]
        exc_img = re.sub(patcq, img, word_raw)
        word = exc_img
    else:
        word = word_raw
    if os.path.exists(file_path_exp):
        async with aiofiles.open(file=file_path_exp,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if (word == line):
                    return 2
    if os.path.exists(file_path_selfwords):
        async with aiofiles.open(file=file_path_selfwords,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if (word == line):
                    return 3
    if os.path.exists(file_path):
        async with aiofiles.open(file=file_path,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if (word == line):
                    return 1
    else:
        return (f'未找到单词表')


async def matchid(str):
    if os.path.exists(file_path_blacklist):
        async with aiofiles.open(file=file_path_blacklist,mode='r',encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                # await bot.send_private_msg(user_id=user, message=f'user:{user},line:{line}')
                if (str == line):
                    return 1


async def save_word(word_raw:str):
    img = ''
    if (re.findall(patimg, word_raw) != []):
        img = re.findall(patimg, word_raw)[0]
        word = img
    else:
        word = word_raw
    if os.path.exists(file_path):
        async with aiofiles.open(file=file_path,mode='a',encoding='utf-8') as file:
            await file.write(f'{word}\n')

