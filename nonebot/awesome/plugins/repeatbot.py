import nonebot
import re
import time
import random
import asyncio
import aiofiles
import motor.motor_asyncio as amongo

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
    await session.send(await learn_word(word))


@nonebot.on_command('忘记', aliases=('删除'), only_to_me=0)
async def forget(session: nonebot.CommandSession):
    word = session.get('word', prompt='你想忘记哪个词？')
    await session.send(await forget_word(word))


@nonebot.on_command('拉黑', only_to_me=0, permission=nonebot.permission.GROUP_OWNER)
async def ban(session: nonebot.CommandSession):
    user_id = session.get('userid', prompt='你想禁言谁？')
    await session.send(await ban_user(user_id))


@nonebot.on_command('恢复', only_to_me=0, permission=nonebot.permission.GROUP_OWNER)
async def recover(session: nonebot.CommandSession):
    user_id = session.get('userid', prompt='你想恢复谁？')
    await session.send(await recover_user(user_id))


# 使用全局 Nonebot 对象
@bot.on_message("group")
async def receive_message(context):
    grp, qq, msg = map(str, [context['group_id'], context['user_id'], context['message']])
    user_info = await bot.get_group_member_info(group_id=int(grp),user_id=int(qq))
    nickname = user_info['nickname']
    if await find_line_in_file(qq, file_path_blacklist):
        return
    client = amongo.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['repeatcache'][grp]
    dbregmsg = client['chatcache'][grp]
    msgres = await db.find_one()
    if msgres and msgres['msg'] == msg:
        print('[RepeatSystem] : repeated.')
        return
    if not msgres:
        db.insert_one({'msg' : '@'})
    msg_type = await match_word(msg)
    user_banned = await match_id(qq)
    if not msg_type:
        await db.delete_many({})
        db.insert_one({'msg' : '@'})
        return
    if msg_type == 3:
        await bot.send_group_msg(group_id=int(grp),message=f'{nickname}，害搁这学我说话呢？')
        return
    if msg_type == 2 or user_banned:
        return
    random.seed(int(time.time()))
    randnum = random.randint(5, 15)
    print(f'[RepeatSystem] : {randnum}')
    if not randnum % 6:
        return
    await asyncio.sleep(randnum)
    regmsgres = await dbregmsg.find_one()
    if msg != regmsgres['msg']:
        print('[RepeatSystem] : canceled.')
        return
    print(f'[RepeatSystem] : currentword - [{msg}]')
    await db.delete_many({})
    await db.insert_one({
        'msg' : msg,
        'timestampint' : int(time.time()), 
    })
    await bot.send_group_msg(group_id=int(grp),message=msg)


async def learn_word(word_raw:str):
    img = ''
    imglen = 0
    finallen = len(re.sub(patcq, '', word_raw)) + len(re.findall(patcq, word_raw))
    word = word_raw
    if re.search(patimg, word_raw):
        imglen = len(re.findall(patimg, word_raw))
        img = re.findall(patimg, word_raw)[0]
        word = re.sub(patcq, img, word_raw)
    if finallen > 10:
        return ('这么长，爷不学')
    if imglen > 1:
        return ('发这么多图，真行')
    res = await match_word(word)
    if res == 1:
        return ('这个我已经会了，爬')
    if res == 2:
        return (f'{word}?我可不学。')
    if res == 3:
        return ('我天天都在说，别让我复读这个了')
    await save_word(word)
    return (f'已学习: {word_raw}')


async def forget_word(word_raw:str):
    img = ''
    word = word_raw
    if re.search(patimg, word_raw):
        img = re.findall(patimg, word_raw)[0]
        word = re.sub(patcq, img, word_raw)
    if await delete_line_in_file(word, file_path):
        return ('已经忘记')
    return (f'我印象里好像没有{word_raw}')


async def ban_user(user_id:str):
    if await find_line_in_file(user_id, file_path_blacklist):
        return ('拉黑过了')
    await add_line_in_file(user_id, file_path_blacklist)
    return (f'已经拉黑{user_id}')


async def recover_user(user_id:str):
    if await delete_line_in_file(user_id, file_path_blacklist):
        return (f'已解除对{user_id}的封禁')
    return (f'未在黑名单里找到此人')


async def match_word(word_raw:str):
    word = word_raw
    if re.search(patimg, word_raw):
        img = re.findall(patimg, word_raw)[0]
        word = re.sub(patcq, img, word_raw)
    if await find_line_in_file(word, file_path_exp):
        return 2
    if await find_line_in_file(word, file_path_selfwords):
        return 3
    return(await find_line_in_file(word, file_path))


async def match_id(user_id:str):
    return (await find_line_in_file(user_id, file_path_blacklist))


async def save_word(word_raw:str):
    word = word_raw
    if re.search(patimg, word_raw):
        word = re.findall(patimg, word_raw)[0]
    await add_line_in_file(word, file_path)


async def add_line_in_file(word:str, file_p:str):
    async with aiofiles.open(file=file_path,mode='a',encoding='utf-8') as file:
        await file.write(f'{word}\n')


async def find_line_in_file(word:str, file_p:str):
    async with aiofiles.open(file=file_p,mode='r',encoding='utf-8') as file:
        async for line in file:
            if word.strip() == line.strip():
                return 1
    return 0


async def delete_line_in_file(word:str, file_p:str):
    flag = 0
    async with aiofiles.open(file=file_p,mode='r',encoding='utf-8') as file_r:
        lines = await file_r.readlines()
    async with aiofiles.open(file=file_p,mode='w',encoding='utf-8') as file_w:
        for line in lines:
            if word.strip() == line.strip():
                flag = 1
                continue
            await file_w.write(line)
    return (flag)


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