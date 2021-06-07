import nonebot
import motor.motor_asyncio

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
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['steamdata']['app']
    req = await db.find_one({'appid':query_word})
    if (req == None):
        return ('未找到该游戏，请检查输入')
    return (str(req['name']))