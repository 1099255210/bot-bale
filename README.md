# bot-罢了

**bot-罢了**是基于 nonebot + go-cqhttp 开发的qq机器人。

## 机器人的作用

下面分模块介绍功能：

### - 天气 weather

输入 `24 [城市]` 可以获取城市24小时内天气信息（温度与降水量），以图片形式返回

### - 直播通知 nana7mibot

定时检测指定up主是否开播，并进行播报

### - 服务器管理 csgoservermanager

实现csgo服务器的管理，详细信息会另建文档描述。

*计划合并到服务器管理csgoservermanager插件中*

### - 破防了 pofang

输入 `破防了` ，机器人结合上文随机回复破防消息。

### - 查询插件（测试阶段） querytest(Test)

输入 `查询账号 steamid64` 查询账号信息。

### - 复读机 repeatbot

输入 `学习 ××` 学习该词汇，此后群友发该词汇时机器人会智能复读。

### - steam个人信息 steamdb

输入 `绑定 steamid64` 可将steam账号和你的qq号绑定。

输入 `信息` 可以查询自己的steam个人资料信息。

输入 `刷新` 可以刷新自己的steam个人资料信息。

### - 生成二维码 qrify

输入 `qr 内容` 可将内容生成为二维码，支持网页链接跳转。

生成的图片在服务器中保存为 `$hash.png` 经过哈希编码 ，不会从文件名泄露信息。

### - 处理请求 dealwithrequests

处理对机器人的好友申请以及加群请求。

## 仓库目录结构

```
- bot-bale
	+ archived				// 已经废弃的机器人文件
	- go-cqhttp				// go-cqhttp 持续更新
		* go-cqhttp_version_linux_amd64.tar.gz
		* go-cqhttp_version_windows_amd64.zip
	- nonebot
		* bot.py
		* config.py
		- awesome\plugins	// 真正属于作者的内容
			* [plugins].py	
			* ...
		+ copy_data			// 复读机器人词典存放
		+ pofang_data		// 破防机器人词典存放
		+ qr_data			// 二维码图片存放
```

## 一些笔记

### 在线状态

| 状态   | 代码 |
| ------ | ---- |
| 在线   | 0    |
| 离开   | 1    |
| 隐身   | 2    |
| 学习中 | 13   |
| 熬夜中 | 14   |
| 游戏中 | 18   |
| 度假中 | 19   |

### 设备信息 (protocol 字段)

| 值   | 类型          | 限制                                     |
| ---- | ------------- | ---------------------------------------- |
| 0    | iPad          | 无                                       |
| 1    | Android Phone | 无                                       |
| 2    | Android Watch | 无法接收`notify`事件、口令红包、撤回消息 |
| 3    | MacOS         |                                          |

## 历史版本的机器人

全部存放在 `archived` 文件夹中了，机器人古老的版本，包含许多**不可直视**的代码，**慎入！！！**

## 未完成的工作

- [ ] 为插件添加足够多的注释

- [ ] 解释部分功能的工作原理
- [ ] 异步实现所有功能
- [ ] 添加一些笔记