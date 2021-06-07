import nonebot

bot = nonebot.get_bot()
superadmin = ''

@bot.on_request('friend')
async def permit_friendreq(context):
    msg = str(context['comment'])
    reqflag = str(context['flag'])
    if msg == 'botbale':
        await bot.set_friend_add_request(flag=reqflag,approve=True)


@bot.on_request('group')
async def permit_groupreq(context):
    user_id = str(context['user_id'])
    reqflag = str(context['flag'])
    if user_id == superadmin:
        await bot.set_group_add_request(flag=reqflag,approve=True)
        return
    await bot.set_group_add_request(
        flag = reqflag,
        approve = False,
        reason = f'请联系{superadmin}'
    )

