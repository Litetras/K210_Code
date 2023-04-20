import sensor, image, lcd, time
import KPU as kpu
import gc, sys
from machine import UART    #导入UART模块
from fpioa_manager import fm
# 串口 设置 P7 RX P8 TX
fm.register(7, fm.fpioa.UART1_RX, force = True)      # 配置 7 脚为 UART2_RX 强制注册
fm.register(8, fm.fpioa.UART1_TX, force = True)      # 配置 8 脚为 UART2_TX 强制注册
uart_A = UART(UART.UART1, 115200, 8, 1, 0, timeout=100000, read_buf_len=4096)#数据位 8 停止位 1 校验位 0 超时时间 100000ms 缓冲区大小 4096

def lcd_show_except(e):
    import uio
    err_str = uio.StringIO()
    sys.print_exception(e, err_str)
    err_str = err_str.getvalue()
    img = image.Image(size=(224,224))
    img.draw_string(0, 10, err_str, scale=1, color=(0xff,0x00,0x00))
    lcd.display(img)

def main(anchors, labels = None, model_addr="/sd/m.kmodel", sensor_window=(224, 224), lcd_rotation=0, sensor_hmirror=False, sensor_vflip=False):
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)   # QVGA=320x240
    sensor.set_windowing(sensor_window) # 224x224
    sensor.set_hmirror(sensor_hmirror)
    sensor.set_vflip(sensor_vflip)
    sensor.run(1)   #启动摄像头

    lcd.init(type=1)    #初始化LCD
    lcd.rotation(lcd_rotation)  #旋转LCD
    lcd.clear(lcd.WHITE)    #清屏

    if not labels:  #如果没有标签文件，就用默认标签
        with open('labels.txt','r') as f:   #打开标签文件
            exec(f.read())  #执行标签文件
    if not labels:  #如果还是没有标签文件，就显示错误信息
        print("no labels.txt")
        img = image.Image(size=(320, 240))  #创建一个320x240的图片
        img.draw_string(90, 110, "no labels.txt", color=(255, 0, 0), scale=2)   #在图片上写入错误信息
        lcd.display(img)    #显示图片
        return 1
    try:
        img = image.Image("startup.jpg")    #创建一个图片，图片内容是startup.jpg
        lcd.display(img)                    #LCD显示图片
    except Exception:
        img = image.Image(size=(320, 240))  #创建一个320x240的图片
        img.draw_string(90, 110, "loading model...", color=(255, 255, 255), scale=2)    #在图片上写入错误信息
        lcd.display(img)    #显示图片

    task = kpu.load(model_addr) #加载模型
    kpu.init_yolo2(task, 0.5, 0.3, 5, anchors) # threshold:[0,1], nms_value: [0, 1]
    try:
        while 1:
            uart_A.write("detecting"+ '\r\n')################################
            img = sensor.snapshot()
            t = time.ticks_ms()
            objects = kpu.run_yolo2(task, img)
            t = time.ticks_ms() - t
            if objects:     #如果检测到物体
                for obj in objects: #遍历检测到的物体
                    pos = obj.rect()    #获取物体的位置，返回一个坐标元组（x,y,w,h）
                    img.draw_rectangle(pos) #在图片上画出物体的位置
                    img.draw_string(pos[0], pos[1], "%s : %.2f" %(labels[obj.classid()], obj.value()), scale=2, color=(255, 0, 0))
                    uart_A.write(labels[obj.classid()]+ '\r\n') #将检测到的物体发送到串口########################
                    print('检测到'+labels[obj.classid()] + '\r\n')
            img.draw_string(0, 200, "t:%dms" %(t), scale=2, color=(255, 0, 0))  #在图片上写入检测时间
            lcd.display(img)    #LCD显示图片
    except Exception as e:  #如果出现错误
        raise e #抛出错误
    finally:
        kpu.deinit(task)    #释放模型


if __name__ == "__main__":
    try:
        labels = ['1', '2', '3', '4', '5', '6', '7', '8']   #标签
        anchors = [1.40625, 1.8125000000000002, 5.09375, 5.28125, 3.46875, 3.8124999999999996, 2.0, 2.3125, 2.71875, 2.90625]   #锚点
        main(anchors = anchors, labels=labels, model_addr="/sd/m.kmodel", lcd_rotation=2, sensor_window=(224, 224)) #调用main函数
    except Exception as e:
        sys.print_exception(e)  #打印错误信息
        lcd_show_except(e)  #显示错误信息
    finally:
        gc.collect()    #垃圾回收
