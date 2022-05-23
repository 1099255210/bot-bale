import os
import platform
import datetime
import matplotlib.pyplot as plt
import nonebot
import aiohttp

city_info_query_link = 'https://geoapi.qweather.com/v2/city/lookup'
intime_weather_link = 'https://devapi.qweather.com/v7/weather/now'
future_weather_24_link = 'https://devapi.qweather.com/v7/weather/24h'
future_weather_3_link = 'https://devapi.qweather.com/v7/weather/3d'

apikey = 'f9922dc1a5d9437fa5b9850eb7f10934'
location_key_para = {
    'location' : '',
    'key' : apikey,
}
city_para = location_key_para
intime_weather_para = location_key_para
future_weather_3_para = location_key_para
future_weather_24_para = location_key_para

@nonebot.on_command('24',only_to_me=0)
async def precast24(session:nonebot.CommandSession):
    city = session.current_arg.strip()
    if not city:
        session.pause('城市名为空，请重新输入')
    future_weather_24_para['location'] = await get_locationid(city)
    if not future_weather_24_para['location']:
        await session.send(f'暂且查询不到{city}的天气，请检查输入')
        return

    weather_res_json = await get_weather_json(
        future_weather_24_link,
        future_weather_24_para
    )
    pic_name = await draw_weather_pic(weather_res_json, city)
    pic_url = await get_file_url(pic_name, 'weather_data')
    print(pic_url)
    await session.send({
        'type' : 'image',
        'data' : {
            'file' : f'{pic_url}'
        }
    })


@nonebot.on_command('天气',only_to_me=0)
async def weather(session:nonebot.CommandSession):
    city = session.current_arg.strip()
    if not city:
        session.pause('城市名为空，请重新输入')
    intime_weather_para['location'] = await get_locationid(city)
    if not intime_weather_para['location']:
        await session.send(f'暂且查询不到{city}的天气，请检查输入')
        return
    # get locationid through input.

    weather_res_json = await get_weather_json(intime_weather_link, intime_weather_para)
    weather_info = weather_res_json['now']
    print(f'[weather] : {weather_info}')

    temp, text, windDir, windScale, humidity, precip = [
        weather_info['temp'],
        weather_info['text'],
        weather_info['windDir'],
        weather_info['windScale'],
        weather_info['humidity'],
        weather_info['precip'],
    ]

    return_info = (
        f'{city}现在的天气情况：\n'
        f'气温{temp}摄氏度，{text}，\n'
        f'{windDir}{windScale}级，\n'
        f'相对湿度{humidity}%'
    )

    if float(precip) > 0.0:
        await session.send(f'{return_info}，小时累计降水量{precip}。')
    else:
        await session.send(f'{return_info}。')


async def draw_weather_pic(weather_res_json, city):
    weather_list = weather_res_json['hourly']
    temp_list = [
        int(hour_data['temp']) for hour_data in weather_list
    ]
    rain_list = [
        float(hour_data['precip']) for hour_data in weather_list
    ]
    time_hours_list = [
        hour_data['fxTime'] for hour_data in weather_list
    ]
    times_list_int = [i for i in range(0, 24)]
    for times in time_hours_list:
        times = datetime.datetime.fromisoformat(times)

    # drawing part
    Y = temp_list
    Y2 = rain_list
    X = times_list_int

    min_Y = min(temp_list)
    max_Y = max(temp_list)
    min_Y2 = min(rain_list)
    max_Y2 = max(rain_list)
    if min_Y % 2:
        min_Y = min_Y - 1
    y_scale = max(max_Y - min_Y, max_Y2 - min_Y2)

    plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('seaborn-notebook')
    fig = plt.figure(figsize=(7, 4), dpi=200)
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    line1, = ax1.plot(X, Y, marker='s', label='温度')
    bar1 = ax2.bar(X, Y2, color=(0,0,0,0.3), label='降水量')

    ax1.set_title(f'{city}未来24小时天气')
    ax1.set_ylim([min_Y - 3, min_Y + y_scale + 1])
    ax2.set_ylim([0, y_scale + 4])
    ax1.set_ylabel('每小时气温/摄氏度')
    ax2.set_ylabel('每小时降水量/毫升')

    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)

    plt.grid('on')
    plt.legend((line1, bar1), ('温度', '降水量'), loc='upper right', framealpha=0.5)
    print(city + time_hours_list[0])
    file_name = str(hash(city + time_hours_list[0])) + '.png'
    plt.savefig(fname=f'./weather_data/{file_name}')
    return f'{file_name}'


async def get_locationid(city):
    city_para['location'] = city;
    city_res_json = await get_weather_json(city_info_query_link, city_para)
    try:
        return(city_res_json['location'][0]['id'])
    except KeyError:
        return 0


async def get_weather_json(link, para):
    async with aiohttp.ClientSession() as httpsession:
        async with httpsession.get(
            link,
            params = para
        ) as res:
            res_json = await res.json()
    return(res_json)


async def get_file_url(file_name, folder):
    cpath = os.path.abspath('')
    if platform.system() == 'Windows':
        return f'file:///{cpath}\\{folder}\\{file_name}'
    return f'file:///{cpath}/{folder}/{file_name}'
