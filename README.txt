Maixhub 目标检测训练结果 **使用说明**

* boot.py: 在 maixpy 上运行的代码
* *.kmodel 或者 *.smodel: 训练好的模型文件（ smodel 是加密模型 ）
* labels.txt: 分类标签
* startup.jpg: 启动图标
* report.jpg: 训练报告,包括了损失和准确度报告等
* warning.txt: 训练警告信息，如果有这个文件，务必阅读， 里面的原因可能会导致训练精度低

使用方法:

0. 按照文档(maixpy.sipeed.com)更新到最新的固件
   如果新固件出现bug,可以使用这个固件测试(选择minimum_with_ide_support.bin): 
   https://dl.sipeed.com/MAIX/MaixPy/release/master/maixpy_v0.5.1_124_ga3f708c
1. 准备一张 SD 卡, 将本目录下的文件拷贝到 SD 卡根目录
2. SD 卡插入开发板
3. 开发板上电启动
4. 摄像头对准训练的物体,
       屏幕左上角会显示 物体标签 和 概率
       屏幕左下角会显示 运行模型消耗的时间,单位是毫秒

如果没有 SD 卡:

* 按照 maixpy.sipeed.com 文档所述的方式, 将模型烧录到 flash
* 修改 boot.py 的 main 函数调用的参数: model 在 flash 中的地址
* 其它资源文件,比如 startup.jpg 可以通过工具发送到开发板的文件系统,或者不管, 没有会自动跳过显示
* 运行 boot.py
* 如果以上的步骤您不理解,那么应该先完整按照 maixpy.sipeed.com 的文档学习一遍使用方法就会了
