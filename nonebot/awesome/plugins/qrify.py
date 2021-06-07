import platform
import nonebot
import qrcode
import os
import re

@nonebot.on_command('qr',aliases='二维码',only_to_me=0)
async def qrcode_sender(session:nonebot.CommandSession):
    qr_word = session.current_arg.strip()
    if re.search(r'//', qr_word):
        qr_word = qr_word.split('//')[-1]
    file_name = str(hash(qr_word))
    if re.search(r'\.', qr_word):
        qr_word = 'https://' + qr_word  # 做链接跳转
    if not os.path.exists(f'./qr_data/{file_name}.png'):
        qr_obj = qrcode.QRCode(
            border = 1,
        )
        qr_obj.add_data(qr_word)
        qr_obj.make(fit=True)
        qr_obj.make_image().save(f'./qr_data/{file_name}.png')
    cpath = os.path.abspath('')
    if platform.system() == 'Windows':
        await session.send({
            'type' : 'image',
            'data' : {
                'file' : f'file:///{cpath}\\qr_data\\{file_name}.png'
            }
        })
    else:
        await session.send({
            'type' : 'image',
            'data' : {
                'file' : f'file:///{cpath}/qr_data/{file_name}.png'
            }
        })

