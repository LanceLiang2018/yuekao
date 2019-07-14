# yuekao

柳铁一中201702班暑假约考提交系统

# Todo List

- 建立`flask`框架...OK
- 上传服务...OK
- 验证码系统...OK
- 数据库...OK...回滚操作...OK
- 主页美化...OK
- CDN配置...OK
- 数据查找和下载...OK
- xlsx和csv数据解析生成...OK
- 考试管理...OK
- 学生信息管理...OK
- 图片打包下载...

#### 参考
```python
from torrentool.api import Torrent

'''Reading and modifying an existing file.'''
my_torrent = Torrent.from_file('/home/idle/some.torrent')
my_torrent.total_size  # Total files size in bytes.
my_torrent.magnet_link  # Magnet link for you.
my_torrent.comment = 'Your torrents are mine.'  # Set a comment.
my_torrent.to_file()  # Save changes.

'''Or we can create a new torrent from a directory.'''
new_torrent = Torrent.create_from('/home/idle/my_stuff/')  # or it could have been a single file
new_torrent.announce_urls = 'udp://tracker.openbittorrent.com:80'
new_torrent.to_file('/home/idle/another.torrent')
```

# 帮助

## 学生::数据提交过程

输入信息：

- 组长名字 `这个竟然没有限制...无妨`
- 自己学号
- 自己名字 `注意学号和名字不对应就没法上传`
- 学科
- 上传文件 `没有判断文件类型` `可能会有点慢，但是有时候很快`
- 分数 `注意要按照数字格式`
- (单次提交的)反馈/吐槽(关于作业内容)
- 验证码 `背景文字是《人间失格》的内容` `是一百以内的加减法（指的是左边两个数字一百以内）`

## 组长/班长::数据管理过程

访问主页中间左边的按钮`管 理`，或者直接打开<https://yuekao.herokuapp.com/data>

最终没有在这部分加上密码。

- `下载该数据`能够下载当前视图下的数据。
- `查看总结`是把提交的信息整理成单次考试数据。
- `查看提交情况`查看的是每一次提交信息的数据。这里能找到图片。
- `管理员`登陆为管理员操作。
- `数据筛选`

## 管理员::管理数据库

先访问`管理`下的`管理员`，将会提示输入密码（bHR5ejEzNTc5(加密)）。

- 开始新一轮考试`这将删除数据库内容！请确认数据已经下载！`
- 更新学生信息`这个用来给不同的班级使用。`
- 清空数据库！`调试用。`

# STAFF

- @LanceLiang2018：代码
- @乱七八糟、：设计建议