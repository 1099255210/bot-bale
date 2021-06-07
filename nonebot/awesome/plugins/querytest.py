import nonebot
import motor.motor_asyncio as amongo
import asyncio

@nonebot.on_notice('notify')
async def chuo(session: nonebot.NoticeSession):
    qq = str(session.event['target_id'])
    selfqq = str(session.event['self_id'])
    if session.event['sub_type'] == 'poke' and qq == selfqq:
        await session.send(f'怎么有啥b天天戳来戳去啊')
        await asyncio.sleep(10)
        await session.send(f'能不能爬啊')


@nonebot.on_notice('notify')
async def lucky(session: nonebot.NoticeSession):
    if session.event['sub_type'] == 'lucky_king':
        await session.send(f'有人运气这么好，能不能再发一个啊')
        await asyncio.sleep(10)
        await session.send(f'gkdgkd')


@nonebot.on_command('查询游戏', only_to_me=0)
async def user_query(session: nonebot.CommandSession):
    query_word = session.get('query_word', prompt='请输入游戏的appid')
    query_res = await query(query_word)
    await session.send(query_res)


@user_query.args_parser
async def _(session: nonebot.CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['query_word'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('输入为空，请重新输入')

    session.state[session.current_key] = stripped_arg


async def query(query_word:str):
    client = amongo.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['steamdata']['app']
    req = await db.find_one({'appid':query_word})
    if (req == None):
        return ('未找到该游戏，请检查输入')
    return (str(req['name']))