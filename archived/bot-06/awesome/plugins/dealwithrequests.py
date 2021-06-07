import nonebot

bot = nonebot.get_bot()

@bot.on_request('friend')
async def permit_friendreq(context):
    msg = context['comment']
    msg = str(msg)
    if (msg == 'botbale'):
        await bot.set_friend_add_request(approve=True)


@bot.on_request('group')
async def permit_groupreq(context):
    user_id = context['user_id']
    user_id = str(user_id)
    if (user_id == '1099255210'):
        await bot.set_group_add_request(approve=True,reason='请联系1099255210')