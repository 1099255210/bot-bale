import nonebot
import aiohttp

link = 'https://api.lolicon.app/setu/'
data = {
    "apikey":'',  #添加apikey
    'r18':0,   #添加r18参数 0为否，1为是，2为混合
    'keyword': '',   #若指定关键字，将会返回从插画标题、作者、标签中模糊搜索的结果
    'num': 1,          #一次返回的结果数量，范围为1到10，不提供 APIKEY 时固定为1
    'size1200':1     #是否使用 master_1200 缩略图，以节省流量或提升加载速度
}


@nonebot.on_command('涩图', aliases=('setu'), only_to_me=0)
async def givename(session: nonebot.CommandSession):
    setu_link = await get_setulink()
    await session.send(f'[CQ:image,file={setu_link}]')


async def get_setulink():
    async with aiohttp.ClientSession() as session:
        while(1):
            async with session.get(link, params=data) as response:
                resjson = await response.json()
                url = resjson['data'][0]['url']
                pic_id = url.split('/')[-1].split('_')[0]
                url = 'https://pixiv.cat/' + pic_id + '.jpg'
                return (url)
            