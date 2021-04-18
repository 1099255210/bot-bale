from nonebot import on_command, CommandSession

@on_command('weather', aliases=('天气'))
async def weather(session: CommandSession):
    city = session.get('city', prompt='你想查询哪个城市的天气呢？')
    weather_report = await get_weather(city)
    await session.send(weather_report)


@weather.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['city'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('城市名不能为空')

    session.state[session.current_key] = stripped_arg


async def get_weather(city: str) -> str:
    return f'{city}的天气是：'