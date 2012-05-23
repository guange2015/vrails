 vrails
==

 what?
------

vrails用于增强在windows上使用virtual host + Sublime Text2的体验。

ChangeLog
------

**v0.2**

1. 修改http协议为长连接socket。
2. Log输出更加快速和稳定，目前能支持绝大部分rails命令。

**v0.1**

1. 采用node的http协议实现大致框架

how
----

1.  切换到你的SublimeText的Package目录，如(D:\soft\editor\sublime\Data\Packages).  将vrails通过git下载到此目录下。 
```git clone git://github.com/hhuai/vrails.git```

2. 将vrails下的server.js拷贝到虚拟机中，并配置好相应的rvm环境，确保在当前的shell下能跑通rails的命令, 然后运行node server.js

3. 打开sublimetext 中tools-> vrails ->settings菜单，配置好相对应的项目路径及服务器地址。

** 默认快捷键 **

* ``` ctrl + shift + x ``` 执行所有测试
* ``` ctrl + shift + l ``` 执行当前行测试
* ``` ctrl + shift + z ``` 执行远程自定义命令

problem
-------
* 请确保vmware中的共享已打开，项目能在win和linux中都能打开。
* 出现问题可以回vmware中看看输出。
