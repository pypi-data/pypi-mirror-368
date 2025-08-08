import uiautomation as uia

class Clipboard:
    @staticmethod
    def GetText():
        """
        读取剪贴板文本

        Clipboard.GetText()

        :return:剪贴板的文本内容
        """
    @staticmethod
    def SaveImage(savePath: str):
        '''
        保存剪贴板图像

        Clipboard.SaveImage(savePath)

        :param savePath:[必选参数]要将剪贴板的图像保存到的文件路径，如"D:\\1.png"
        :return:图像保存成功返回True，保存失败返回False
        '''
    @staticmethod
    def SetFile(paths: str | list):
        '''
        文件设置到剪贴板

        Clipboard.SetFile(paths)

        :param paths:[必选参数]文件的路径，单个文件用字符串类型，如"D:\x01.txt"，多个文件用 list 类型，其中每个元素用字符串，如["D:\x01.txt", "D:\x01.png"]
        :return:成功返回True，失败返回False
        '''
    @staticmethod
    def SetImage(picPath):
        '''
        图片设置到剪贴板

        Clipboard.SetImage(picPath)

        :param picPath:[必选参数]要放入剪贴板的图片路径，如"D:\\1.png"
        :return:成功返回True，失败返回False
        '''
    @staticmethod
    def SetText(content: str = ''):
        '''
        设置剪贴板文本

        Clipboard.SetText(\'\')

        :param content:[必选参数]新的剪贴板文本内容，默认""
        :return:成功返回True，失败返回False
        '''

class PrintToScreen:
    @staticmethod
    def DrawText(msg: str = '', showSec: int = 0):
        '''
        绘制屏幕中央正上方显示的红字

        PrintToScreen.DrawText(\'开始工作\', showSec=0)

        :param msg:[可选参数]文字内容，默认为""
        :param showSec:[可选参数]显示秒数。0:一直显示到程序结束，大于0:显示的时间，单位是秒
        :return:无
        '''
    @staticmethod
    def CleanText() -> None:
        """
        清除屏幕中央正上方显示的红字

        PrintToScreen.CleanText()

        :return:无
        """

class Dialog:
    @staticmethod
    def MsgBox(title: str, prompt: str) -> None:
        """
        消息框

        Dialog.MsgBox('提示', '这是一个消息框')

        :param title:[必选参数]弹框标题
        :param prompt:[必选参数]弹框提示内容
        :return: 无
        """
    @staticmethod
    def InputBox(title: str, prompt: str, default: str = '') -> str | None:
        """
        输入对话框

        Dialog.InputBox('输入对话框标题', '请输入内容：', default='请在这输入文本')

        :param title:[必选参数]弹框标题
        :param prompt:[必选参数]弹框提示内容
        :param default:[可选参数]输入框默认文本，默认''
        :return: 点确定按钮，返回用户输入的内容（字符串），点取消或关闭返回None
        """
    @staticmethod
    def PasswordBox(title: str, prompt: str) -> str | None:
        """
        密码输入对话框

        Dialog.PasswordBox('密码输入对话框标题', '请输入密码：')

        :param title:[必选参数]弹框标题
        :param prompt:[必选参数]弹框提示内容
        :return: 点确定按钮，返回用户输入的密码（字符串），点取消或关闭返回None
        """
    @staticmethod
    def NumberBox(title: str, prompt: str, default: str = '', minvalue: int = None, maxvalue: int = None, error_message: str = '请输入一个有效的整数！') -> int | None:
        '''
        整数输入对话框

        Dialog.NumberBox(\'整数对话框标题\', \'请输入整数：\', default=\'100\', minvalue=10, maxvalue=200, error_message="请输入一个有效的整数！")

        :param title:[必选参数]弹框标题
        :param prompt:[必选参数]弹框提示内容
        :param default:[可选参数]输入框默认文本，默认\'\'
        :param minvalue:[可选参数]最小值，默认None
        :param maxvalue:[可选参数]最大值，默认None
        :param error_message:[可选参数]输入非整数时的弹框提示语，默认"请输入一个有效的整数！"
        :return: 点确定按钮，返回用户输入的整数(int类型)，点取消或关闭返回None
        '''
    @staticmethod
    def YnBox(title: str, prompt: str) -> bool:
        """
        确认对话框

        Dialog.YnBox('确认对话框标题', '是否确认？')

        :param title:[必选参数]弹框标题
        :param prompt:[必选参数]弹框提示内容
        :return: 点是返回True，点否或关闭返回False
        """
    @staticmethod
    def MultenterBox(title: str, prompts: list) -> dict:
        """
        多行输入对话框

        Dialog.MultenterBox('多行输入对话框标题', ['请输入姓名：', '请输入年龄：'])

        :param title:[必选参数]弹框标题
        :param prompts:[必选参数]弹框多行的字段内容，例如['请输入姓名：', '请输入年龄：']
        :return: 点确定按钮，返回用户输入的内容，格式为字典，键为字段内容，值为用户输入的内容，关闭返回{}
        """
    @staticmethod
    def MultchoiceBox(title: str, prompt: str, choices: list) -> list:
        """
        多选框

        Dialog.MultchoiceBox('选择', '请选择：', ['选项1', '选项2'])

        :param title:[必选参数]弹框标题
        :param prompt:[必选参数]弹框提示内容
        :param choices:[必选参数]选项内容，例如['选项1', '选项2']
        :return: 点确定按钮，返回用户选择的内容，格式为列表，关闭返回[]
        """

class INI:
    @staticmethod
    def Read(iniPath: str, sectionName: str, keyName: str, defaultValue: str = '', encoding: str = 'GBK') -> str:
        '''
        读键值

        value = INI.Read(\'D:\\conf.ini\',\'section1\', \'key1\', defaultValue=\'\', encoding=\'GBK\')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param keyName:[必选参数]要访问 INI 配置文件的键名
        :param defaultValue:[可选参数]当 INI 配置文件键名不存在时，返回的默认内容。默认是空字符串
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: 返回读取的值，字符串类型
        '''
    @staticmethod
    def Write(iniPath: str, sectionName: str, keyName: str, value, encoding: str = 'GBK') -> None:
        '''
        写键值

        INI.Write(\'D:\\conf.ini\',\'section1\', \'key1\', \'value1\', encoding=\'GBK\')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param keyName:[必选参数]INI 文件中被写入的键值对中的键名，若为空字符串，则此键值对不被写入
        :param value:[必选参数]INI 文件中被写入的键值对中的键值
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: None
        '''
    @staticmethod
    def EnumSection(iniPath: str, encoding: str = 'GBK') -> list:
        '''
        枚举小节

        sections = INI.EnumSection(\'D:\\conf.ini\', encoding=\'GBK\')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: 返回一个列表，列表中每个元素为一个section的名字
        '''
    @staticmethod
    def EnumKey(iniPath: str, sectionName: str, encoding: str = 'GBK') -> list:
        '''
        枚举键

        keys = INI.EnumKey(\'D:\\conf.ini\', \'section1\', encoding=\'GBK\')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: 返回一个列表，列表中每个元素为一个key的名字
        '''
    @staticmethod
    def DeleteSection(iniPath: str, sectionName: str, encoding: str = 'GBK') -> None:
        '''
        删除小节

        INI.DeleteSection(\'D:\\conf.ini\',\'section1\', encoding=\'GBK\')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: None
        '''
    @staticmethod
    def DeleteKey(iniPath: str, sectionName: str, keyName: str, encoding: str = 'GBK'):
        '''
        删除键

        INI.DeleteKey(\'D:\\conf.ini\',\'section1\', \'key1\', encoding=\'GBK\')

        :param iniPath:[必选参数]INI 配置文件所在路径
        :param sectionName:[必选参数]要访问 INI 配置文件的小节名字
        :param keyName:[必选参数]要访问 INI 配置文件的键名
        :param encoding:[可选参数]文件编码，常用"GBK"， "UTF8"等。默认 GBK
        :return: None
        '''

class App:
    @staticmethod
    def Kill(processName: str | int) -> bool:
        """
        强制停止应用程序的运行（结束进程）

        App.Kill('chrome.exe')

        :param processName:[必选参数]应用程序进程名或进程PID，忽略大小写字母
        :return:命令执行成功返回True，失败返回False
        """
    @staticmethod
    def GetStatus(processName: str | int, status: int = 0) -> bool:
        """
        获取应用运行状态

        App.GetStatus('chrome.exe', status=0)

        :param processName:[必选参数]应用程序进程名或进程PID，忽略大小写字母
        :param status:[可选参数]筛选进程状态。0:所有状态 1:运行 2:暂停 3:未响应 4:未知。默认0
        :return:进程存在返回True，不存在返回False
        """
    @staticmethod
    def Run(exePath, waitType: int = 0, showType: int = 1, mode: int = 0):
        """
        启动应用程序

        App.Run('''C:\\Windows\\system32\\mspaint.exe''')

        :param exePath:[必选参数]应用程序文件路径
        :param waitType:[可选参数]0:不等待 1：等待应用程序准备好 2：等待应用程序执行到退出。默认0
        :param showType:[可选参数]程序启动后的显示样式（不一定生效） 0：隐藏 1：默认 3：最大化 6：最小化
        :param mode:[可选参数]启动模式，0:常规模式启动, 1:增强模式启动。当常规模式启动后无法拾取元素时，可尝试增强模式启动。默认0
        :return:返回应用程序的PID
        """
    @staticmethod
    def WaitProcess(processName, waitType: str = 'open', delayTime: int = 30000) -> bool:
        '''
        等待应用启动或关闭

        App.WaitProcess(\'chrome.exe\', waitType=\'open\', delayTime=30000)

        :param processName:[必选参数]进程名称，忽略大小写字母。如:"chrome.exe"
        :param waitType:[可选参数]期望应用状态。open:等待应用打开 close:等待应用关闭
        :param delayTime:[可选参数]最大等待时间，默认30000毫秒(即30秒)
        :return:等待时间内达到期望应用状态（开启/关闭）返回True，否则返回False
        '''

class Image:
    @staticmethod
    def Exists(imagePath: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, accuracy: float = 0.9, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, matchType: str = 'GrayMatch', backgroundPic: bool = False) -> bool:
        '''
        判断图像是否存在

        Image.Exists(\'d:\\test.jpg\', target, anchorsElement=None, rect=None, accuracy=0.9, searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, matchType=\'GrayMatch\', backgroundPic=False)

        :param imagePath:[必选参数]要查找的图片路径
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行图片识别，如果范围传递为 None，则进行控件矩形区域范围内的图片识别，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的图片识别。默认None
        :param accuracy:[可选参数]查找图片时使用的相似度，相似度范围从 0.5 - 1.0，表示 50% - 100% 相似。默认0.9
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param matchType:[可选参数]指定查找图像的匹配方式，\'GrayMatch\':“灰度匹配”速度快，但在极端情况下可能会匹配失败，\'ColorMatch\':“彩色匹配”相对“灰度匹配”更精准但匹配速度稍慢。默认\'GrayMatch\'
        :param backgroundPic:[可选参数]是否后台识图片（图片需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :return:存在返回True，不存在返回False
        '''
    @staticmethod
    def FindPic(imagePath: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, accuracy: int | float = 0.9, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, matchType: str = 'GrayMatch', backgroundPic: bool = False, iSerialNo: int = 0, returnPosition: str = 'center') -> dict | list | None:
        '''
        查找图像

        Image.FindPic(\'d:\\test.jpg\', target, anchorsElement=None, rect=None, accuracy=0.9, searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, matchType=\'GrayMatch\', backgroundPic=False, iSerialNo=0, returnPosition="center")

        :param imagePath:[必选参数]要查找的图片路径
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行图片识别，如果范围传递为 None，则进行控件矩形区域范围内的图片识别，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的图片识别。默认None
        :param accuracy:[可选参数]查找图片时使用的相似度，相似度范围从 0.5 - 1.0，表示 50% - 100% 相似。默认0.9
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param matchType:[可选参数]指定查找图像的匹配方式，\'GrayMatch\':“灰度匹配”速度快，但在极端情况下可能会匹配失败，\'ColorMatch\':“彩色匹配”相对“灰度匹配”更精准但匹配速度稍慢。默认\'GrayMatch\'
        :param backgroundPic:[可选参数]是否后台识图片（图片需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :param iSerialNo:[可选参数]指定图像匹配到多个目标时的序号，序号为从1开始的正整数，在屏幕上从左到右从上到下依次递增，匹配到最靠近屏幕左上角的目标序号为1,如果是0，返回所有匹配图像的坐标。默认为0
        :param returnPosition:[可选参数]\'center\':返回图片中心坐标，\'topLeft\':返回图片左上角坐标,\'topRight\':返回图片右上角坐标,\'bottomLeft\':返回图片左下角坐标,\'bottomRight\':返回图片右下角坐标。默认\'center\'
        :return:返回图像的坐标，iSerialNo为0时，返回list，如[{\'x\':100, \'y\':100}, {\'x\':300,\'y\':300}]，iSerialNo大于0时，返回dict，如{\'x\':100, \'y\':100},匹配不到时返回None
        '''
    @staticmethod
    def Click(imagePath: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, accuracy: float = 0.9, button: str = 'left', clickType: str = 'click', searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, keyModifiers: list = None, simulateType: str = 'simulate', moveSmoothly: bool = False, matchType: str = 'GrayMatch', backgroundPic: bool = False, iSerialNo: int = 1):
        '''
        点击图像

        Image.Click(\'d:\\test.jpg\', target, anchorsElement=None, rect=None, accuracy=0.9, button=\'left\', clickType=\'click\', searchDelay=10000, continueOnError=False, delayAfter=100, delayBefore=100,
             setForeground=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, keyModifiers=None, simulateType=\'simulate\', moveSmoothly=False, matchType=\'GrayMatch\', backgroundPic=False, iSerialNo=1)

        :param imagePath:[必选参数]要查找的图片路径
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行图片识别，如果范围传递为 None，则进行控件矩形区域范围内的图片识别，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的图片识别。默认None
        :param accuracy:[可选参数]查找图片时使用的相似度，相似度范围从 0.5 - 1.0，表示 50% - 100% 相似。默认0.9
        :param button:[可选参数]鼠标点击。鼠标左键:"left" 鼠标右键:"right" 鼠标中键:"middle"。默认"left"
        :param clickType:[可选参数]点击类型。单击:"click" 双击:"dbclick" 按下:"down" 弹起:"up"。默认"click"
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param cursorPosition:[可选参数]光标位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param cursorOffsetX:[可选参数]横坐标偏移。默认0
        :param cursorOffsetY:[可选参数]纵坐标偏移。默认0
        :param keyModifiers:[可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param simulateType:[可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"simulate"
        :param moveSmoothly:[可选参数]是否平滑移动鼠标。默认False
        :param matchType:[可选参数]指定查找图像的匹配方式，\'GrayMatch\':“灰度匹配”速度快，但在极端情况下可能会匹配失败，\'ColorMatch\':“彩色匹配”相对“灰度匹配”更精准但匹配速度稍慢。默认\'GrayMatch\'
        :param backgroundPic:[可选参数]是否后台识图片（图片需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。注意：当simulateType为message时，该字段设置为True才会生效
        :param iSerialNo:[可选参数]指定图像匹配到多个目标时的序号，序号为从1开始的正整数，在屏幕上从左到右从上到下依次递增，匹配到最靠近屏幕左上角的目标序号为1,如果是0，匹配所有图片（即点击所有匹配到的图片）。默认为1
        :return:None
        '''
    @staticmethod
    def Hover(imagePath: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, accuracy: float = 0.9, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, keyModifiers: list = None, moveSmoothly: bool = False, matchType: str = 'GrayMatch', backgroundPic: bool = False, iSerialNo: int = 1):
        '''
        鼠标移动到图像上

        Image.Hover(\'d:\\test.jpg\', target, anchorsElement=None, rect=None, accuracy=0.9, searchDelay=10000, continueOnError=False, delayAfter=100, delayBefore=100,
             setForeground=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, keyModifiers=None, moveSmoothly=False, matchType=\'GrayMatch\', backgroundPic=False, iSerialNo=1)

        :param imagePath:[必选参数]要查找的图片路径
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行图片识别，如果范围传递为 None，则进行控件矩形区域范围内的图片识别，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的图片识别。默认None
        :param accuracy:[可选参数]查找图片时使用的相似度，相似度范围从 0.5 - 1.0，表示 50% - 100% 相似。默认0.9
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param cursorPosition:[可选参数]光标位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param cursorOffsetX:[可选参数]横坐标偏移。默认0
        :param cursorOffsetY:[可选参数]纵坐标偏移。默认0
        :param keyModifiers:[可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param moveSmoothly:[可选参数]是否平滑移动鼠标。默认False
        :param matchType:[可选参数]指定查找图像的匹配方式，\'GrayMatch\':“灰度匹配”速度快，但在极端情况下可能会匹配失败，\'ColorMatch\':“彩色匹配”相对“灰度匹配”更精准但匹配速度稍慢。默认\'GrayMatch\'
        :param backgroundPic:[可选参数]是否后台识图片（图片需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :param iSerialNo:[可选参数]指定图像匹配到多个目标时的序号，序号为从1开始的正整数，在屏幕上从左到右从上到下依次递增，匹配到最靠近屏幕左上角的目标序号为1,如果是0，匹配所有图片（即鼠标将移动经过所有匹配到的图片）。默认为1
        :return:None
        '''
    @staticmethod
    def Wait(imagePath: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, accuracy: float = 0.9, waitType: str = 'show', searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, matchType: str = 'GrayMatch', backgroundPic: bool = False):
        '''
        等待图像显示或消失

        Image.Wait(\'d:\\test.jpg\', target, anchorsElement=None, rect=None, accuracy=0.9, waitType="show", searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, matchType=\'GrayMatch\', backgroundPic=False)

        :param imagePath:[必选参数]要查找的图片路径
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行图片识别，如果范围传递为 None，则进行控件矩形区域范围内的图片识别，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的图片识别。默认None
        :param accuracy:[可选参数]查找图片时使用的相似度，相似度范围从 0.5 - 1.0，表示 50% - 100% 相似。默认0.9
        :param waitType:[可选参数]等待方式。 等待显示："show" 等待消失:"hide"。默认"show"
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param matchType:[可选参数]指定查找图像的匹配方式，\'GrayMatch\':“灰度匹配”速度快，但在极端情况下可能会匹配失败，\'ColorMatch\':“彩色匹配”相对“灰度匹配”更精准但匹配速度稍慢。默认\'GrayMatch\'
        :param backgroundPic:[可选参数]是否后台识图片（图片需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :return:None
        '''
    @staticmethod
    def ComColor(color: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, beginPosition: str = 'center', positionOffsetX: int = 0, positionOffsetY: int = 0, backgroundPic: bool = False):
        '''
        目标内指定位置比色

        Image.ComColor(\'FF0000\', target, anchorsElement=None, searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, beginPosition=\'center\', positionOffsetX=0, positionOffsetY=0, backgroundPic=False)

        :param color:[必选参数]指定位置是否为此颜色，十六进制颜色，RGB色值，例如："FF0000"，支持偏色，如"FF0000-101010"
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param beginPosition:[可选参数]起始位置。center:中心, topLeft:左上角, topRight:右上角, bottomLeft:左下角, bottomRight:右下角。默认"center"
        :param positionOffsetX:[可选参数]横坐标偏移。默认0
        :param positionOffsetY:[可选参数]纵坐标偏移。默认0
        :param backgroundPic:[可选参数]是否后台识图片（指定位置的颜色与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :return:匹配返回True，不匹配返回False
        '''
    @staticmethod
    def GetColor(target, anchorsElement: uia.Control | None = None, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, beginPosition: str = 'center', positionOffsetX: int = 0, positionOffsetY: int = 0, backgroundPic: bool = False):
        '''
        获取目标指定位置的颜色值（16进制RGB字符）

        Image.GetColor(target, anchorsElement=None, searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, beginPosition=\'center\', positionOffsetX=0, positionOffsetY=0, backgroundPic=False)

        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param beginPosition:[可选参数]起始位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param positionOffsetX:[可选参数]横坐标偏移。默认0
        :param positionOffsetY:[可选参数]纵坐标偏移。默认0
        :param backgroundPic:[可选参数]是否后台识图片（图片需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :return:返回颜色值（16进制的RGB字符），如"FF0000"
        '''
    @staticmethod
    def FindColor(colors: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, backgroundPic: bool = False, searchOrder: str = 'topLeft', relativeType: str = 'screen'):
        '''
        查找颜色

        Image.FindColor(\'FF0000\', target, anchorsElement=None, rect=None, searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, backgroundPic=False, searchOrder=\'topLeft\', relativeType=\'screen\')

        :param colors: [必选参数]需要查找的颜色值字符串，十六进制颜色，支持偏色，支持同时多个颜色，例如 "FF0000" 或 "FF0000-101010" 或 "FF0000-101010|0000FF-101010"
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行颜色识别，如果范围传递为 None，则进行控件矩形区域范围内的颜色识别，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的颜色识别。默认None
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param backgroundPic:[可选参数]是否后台识图片（颜色需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :param searchOrder:[可选参数]搜索顺序，除“all”以外，其余方式返回首个匹配的颜色坐标，可组合使用，返回多个匹配坐标。
                            topLeft:从上到下由左至右,leftTop:从左到右由上至下,topRight:从上到下由右至左,rightTop:从右到左由上至下,
                            bottomLeft:从下到上由左至右,leftBottom:从左到右由下至上,bottomRight:从下到上由右至左,rightBottom:从右到左由下至上,
                            all:返回找到的所有颜色坐标。默认topLeft。
        :param relativeType:[可选参数]查找坐标相对类型。screen:返回相对屏幕的坐标，以屏幕左上角0,0为坐标原点。 image:返回相对查找范围的坐标，以查找范围的左上角0,0为坐标原点。默认screen
        :return:返回按照搜索顺序匹配到的颜色坐标, 匹配不到时返回None
        '''
    @staticmethod
    def FindMultColor(colorDes: str, target: str | uia.Control, anchorsElement: uia.Control | None = None, rect: dict | None = None, accuracy: int | float = 1.0, searchDelay: int = 10000, continueOnError: bool = False, delayAfter: int = 0, delayBefore: int = 100, setForeground: bool = True, backgroundPic: bool = False, relativeType: str = 'screen'):
        '''
        多点找色

        Image.FindMultColor(colorDes, target, anchorsElement=None, rect=None, accuracy=1.0, searchDelay=10000, continueOnError=False, delayAfter=0, delayBefore=100, setForeground=True, backgroundPic=False, relativeType=\'screen\')

        :param colorDes:[必选参数]多点颜色描述，如"40b7ff-101010,-16|-14|58c0ff-101010,-17|5|4ebbff-101010,17|-3|26adff-101010,17|15|42b7ff-101010", 解释：以40b7ff-101010颜色为锚点，符合向左偏移16像素，向上偏移14像素，且颜色符合58c0ff-101010，向...向...且颜色符合...等等。推荐使用<大漠综合工具>获取颜色描述
        :param target:[必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement:[可选参数]从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param rect:[可选参数]需要查找的范围，程序会在控件这个范围内进行多点找色，如果范围传递为 None，则进行控件矩形区域范围内的多点找色，如果范围传递为 {"x":10,"y":5,"width":200,"height":100}，则进行控件矩形区域范围内以左上角向右偏移10像素、向下偏移5像素为起点，向右侧200，向下100的范围内的多点找色。默认None
        :param accuracy:[可选参数]多点找色时使用的相似度，相似度范围从 0.5 - 1.0，表示 50% - 100% 相似。默认1.0
        :param searchDelay:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认0
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param setForeground:[可选参数]激活窗口。默认True
        :param backgroundPic:[可选参数]是否后台识图片（颜色描述需与查找范围在同一窗口）。True为后台识别图片，False为前台识别图片。默认False。
        :param relativeType:[可选参数]查找坐标相对类型。screen:返回相对屏幕的坐标，以屏幕左上角0,0为坐标原点。 image:返回相对查找范围的坐标，以查找范围的左上角0,0为坐标原点。默认screen
        :return:返回找到的坐标，如{"x":int, "y":int}。找不到返回None
        '''
    @staticmethod
    def CaptureScreen(filePath: str, rect: dict | None = None, continueOnError: bool = False, delayAfter: int = 300, delayBefore: int = 100) -> None:
        '''
        屏幕截图

        Image.CaptureScreen("E:/1.png", rect=None, continueOnError=False, delayAfter=300, delayBefore=100)

        :param filePath:[必选参数]保存的图片路径，如"E:/1.png"
        :param rect:[可选参数]需要截取的范围。{"x": int, "y": int, "width": int, "height": int}：程序会在屏幕这个范围内进行截图。如果范围传递为 None，则进行屏幕截图
        :param continueOnError:[可选参数]错误继续执行。
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认300
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:None
        '''

class Mail:
    @staticmethod
    def SendMail(user: str = '', pwd: str = '', sender: str = '', title: str = '', content: str = '', to: str | list = '', cc: str | list = None, attr: str | list = None, server: str = 'smtp.qq.com', port: int = 465, ssl: bool = True, timeout: int = 10, continueOnError: bool = False) -> None:
        '''
        发送邮件

        Mail.SendMail(user=\'\', pwd=\'\', sender=\'\', title=\'\', content=\'\', to=\'\', cc=None, attr=None, server="smtp.qq.com", port=465, ssl=True, timeout=10, continueOnError=False)

        :param user: [必选参数]邮箱登录帐号，比如普通QQ邮箱的登录帐号与邮箱地址相同
        :param pwd: [必选参数]登录密码
        :param sender: [必选参数]发件人邮箱地址
        :param title: [必选参数]邮件的标题
        :param content: [必选参数]邮件正文内容，支持HTML类型的正文内容
        :param to: [必选参数]收件人邮箱地址，多个地址可用["xxx@qq.com","xxx@163.com"]列表的形式填写, 也可以是单个邮箱地址字符串
        :param cc: [可选参数]抄送邮箱地址，多个地址可用["xxx@qq.com","xxx@163.com"]列表的形式填写, 也可以是单个邮箱地址字符串, None:不需要抄送，默认None
        :param attr: [可选参数]邮件附件，多个附件可以用["附件一路径","附件二路径"]列表的形式填写，也可以是单个附件路径字符串, None:不需要附件，默认None
        :param server: [可选参数]SMTP服务器地址，默认smtp.qq.com
        :param port: [可选参数]SMTP服务器端口，常见为 25、465、587，默认465
        :param ssl: [可选参数]是否使用SSL协议加密，True为使用，False为不使用，默认True
        :param timeout: [可选参数]超时时间(秒)，默认10
        :param continueOnError: [可选参数]发生错误是否继续，True为继续，False为不继续。默认False
        :return:None
        '''

class HTTP:
    @staticmethod
    def SetCookies(cookies: dict = None) -> None:
        '''
        设置cookies

        HTTP.SetCookies(None)

        :param cookies:[可选参数]字典类型的cookies，例如：{"name":"value","name2":"value2"}，默认None
        :return:None
        '''
    @staticmethod
    def SetHeaders(headers: dict = None) -> None:
        '''
        设置Headers

        HTTP.SetHeaders(None)

        :param headers:[可选参数]字典类型的请求头，例如：{"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"}，默认None
        :return:None
        '''
    @staticmethod
    def Get(url: str, form: str | dict = None, delayTime: int = 60000) -> str:
        '''
        Get获取数据

        text = HTTP.Get("", None, 60000)

        :param url:[必选参数]Get页面的链接地址
        :param form:[可选参数]Get时传递的表单数据，可以是字符串或字典，默认None
        :param delayTime:[可选参数]超时时间，单位毫秒，默认60000毫秒
        :return:获取的网络数据的结果
        '''
    @staticmethod
    def Post(url: str, form: str | dict = None, delayTime: int = 60000) -> str:
        '''
        Post提交表单

        text = HTTP.Post("", None, 60000)

        :param url:[必选参数]Post页面的链接地址
        :param form:[可选参数]Post时传递的表单数据，可以是字符串或字典，默认None
        :param delayTime:[可选参数]超时时间，单位毫秒，默认60000毫秒
        :return:向网页提交表单的结果
        '''
    @staticmethod
    def PostJson(url: str, form: str | dict = None, delayTime: int = 60000) -> str:
        '''
        Post提交JSON表单

        text = HTTP.PostJson("", None, 60000)

        :param url:[必选参数]Post页面的链接地址
        :param form:[可选参数]Post时传递的表单数据，可以是字符串或字典，默认None
        :param delayTime:[可选参数]超时时间，单位毫秒，默认60000毫秒
        :return:向网页提交JSON表单的结果
        '''
    @staticmethod
    def GetFile(url: str, file: str, form: str | dict = None, delayTime: int = 60000) -> bool:
        '''
        Get下载文件

        result = HTTP.GetFile("","",None,60000)

        :param url:[必选参数]下载文件的链接地址
        :param file:[必选参数]保存的文件路径
        :param form:[可选参数]Get时传递的表单数据，可以是字符串或字典，默认None
        :param delayTime:[可选参数]超时时间，单位毫秒，默认60000毫秒
        :return:是否下载成功
        '''

class Log:
    @staticmethod
    def SetInit(level: int = 2, maxsize: int = 10, path: str = None) -> None:
        """
        设置日志初始条件

        Log.SetInit(level=2, maxsize=10, path=None)

        :param level:[可选参数]整数型(0~3)，日志记录级别。0：只可记录错误信息；1：只可记录警告信息、错误信息；2：只可记录一般信息、警告信息、错误信息；3：可记录调试信息、一般信息、警告信息、错误信息。默认2
        :param maxsize:[可选参数]整数型，日志文件超过该数值MB就建立新的日志，日志的文件名会增加“_序号”。默认10
        :param path:[可选参数]字符串型，日志存放的目录，如果填写None则为当前文件所在目录下建立Log文件夹。默认None
        :return:None
        """
    @staticmethod
    def CleanOldLogs(days: int = 30) -> None:
        """
        清理旧的日志文件

        Log.CleanOldLogs(days=30)

        :param days:[可选参数]整数型，清理多少日前的日志文件。默认30
        :return:None
        """
    @staticmethod
    def Debug(content: str) -> None:
        '''
        写入调试信息至日志文件中

        Log.Debug("")

        :param content:[必选参数]字符串型，具体调试信息
        :return:None
        '''
    @staticmethod
    def Info(content: str) -> None:
        '''
        写入一般日志信息

        Log.Info("")

        :param content:[必选参数]字符串型，具体一般日志信息
        :return:None
        '''
    @staticmethod
    def Warn(content: str) -> None:
        '''
        写入警告日志

        Log.Warn("")

        :param content:[必选参数]字符串型，具体警告信息
        :return:None
        '''
    @staticmethod
    def Error(content: str) -> None:
        '''
        写入错误日志

        Log.Error("")

        :param content:[必选参数]字符串型，具体错误信息
        :return:None
        '''

class File:
    @staticmethod
    def BaseName(path: str, bext: bool = True) -> str:
        """
        获取名称

        File.BaseName(r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', bext=True)

        :param path:[必选参数]路径。可以是文件路径，也可以是文件夹路径
        :param bext:[可选参数]是否包含扩展名。True:包含，False:不包含。默认True
        :return: 文件或文件夹名称
        """
    @staticmethod
    def DirFileOrFolder(path: str, ftype: str = 'fileandfolder', haspath: bool = True) -> list:
        '''
        获取文件或文件夹列表

        File.DirFileOrFolder(r\'C:\\Program Files\\Google\\Chrome\\Application\', ftype="fileandfolder", haspath=True)

        :param path:[必选参数]文件夹路径
        :param ftype:[可选参数]获取类型。fileandfolder:文件和文件夹。file:文件。folder:文件夹。默认“fileandfolder”
        :param haspath:[可选参数]是否包含路径。True:包含，False:不包含。默认True
        :return: 文件或文件夹列表
        '''
    @staticmethod
    def CopyFile(pathSrc: str, pathDst: str, overWrite: bool = False) -> bool:
        """
        复制文件

        File.CopyFile(r'D:\\新建文本文档.txt', r'D:\\新建文件夹', overWrite=False)

        :param pathSrc:[必选参数]源文件的路径
        :param pathDst:[必选参数]目标文件夹的路径
        :param overWrite:[可选参数]是否覆盖文件。True:覆盖，False:不覆盖。默认False
        :return: bool
        """
    @staticmethod
    def CopyFolder(pathSrc: str, pathDst: str, overWrite: bool = False) -> bool:
        """
        复制文件夹

        File.CopyFolder(r'D:\\新建文件夹', r'D:\\新建文件夹2', overWrite=False)

        :param pathSrc:[必选参数]源文件夹的路径
        :param pathDst:[必选参数]目标文件夹的路径
        :param overWrite:[可选参数]是否覆盖文件。True:覆盖，False:不覆盖。默认False
        :return: bool
        """
    @staticmethod
    def CreateFolder(path: str) -> bool:
        """
        创建文件夹

        File.CreateFolder(r'D:\\新建文件夹')

        :param path:[必选参数]文件夹路径。如果已存在，会抛出异常
        :return: bool
        """
    @staticmethod
    def DeleteFile(path: str) -> bool:
        """
        删除文件

        File.DeleteFile(r'D:\\新建文本文档.txt')

        :param path:[必选参数]文件路径
        :return: bool
        """
    @staticmethod
    def DeleteFolder(path: str) -> bool:
        """
        删除文件夹

        File.DeleteFolder(r'D:\\新建文件夹')

        :param path:[必选参数]文件夹路径
        :return: bool
        """
    @staticmethod
    def ExtensionName(path: str) -> str:
        """
        获取文件扩展名

        File.ExtensionName(r'D:\\新建文本文档.txt')

        :param path:[必选参数]文件路径
        :return: str
        """
    @staticmethod
    def FileExists(path: str) -> bool:
        """
        判断文件是否存在

        File.FileExists(r'D:\\新建文本文档.txt')

        :param path:[必选参数]文件路径
        :return: bool
        """
    @staticmethod
    def FileSize(path: str) -> int:
        """
        获取文件大小

        File.FileSize(r'D:\\新建文本文档.txt')

        :param path:[必选参数]文件路径
        :return: int，文件的字节大小
        """
    @staticmethod
    def FolderExists(path: str) -> bool:
        """
        判断文件夹是否存在

        File.FolderExists(r'D:\\新建文件夹')

        :param path:[必选参数]文件夹路径
        :return: bool
        """
    @staticmethod
    def FolderSize(path: str) -> int:
        """
        获取文件夹大小

        File.FolderSize(r'D:\\新建文件夹')

        :param path:[必选参数]文件夹路径
        :return: int，文件夹的字节大小
        """
    @staticmethod
    def IsFile(path: str) -> bool:
        """
        判断路径是否为文件

        File.IsFile(r'D:\\新建文本文档.txt')

        :param path:[必选参数]文件路径
        :return: bool
        """
    @staticmethod
    def IsFolder(path: str) -> bool:
        """
        判断路径是否为文件夹

        File.IsFolder(r'D:\\新建文件夹')

        :param path:[必选参数]文件夹路径
        :return: bool
        """
    @staticmethod
    def MoveFile(pathSrc: str, pathDst: str, overWrite: bool = False) -> bool:
        """
        移动文件

        File.MoveFile(r'D:\\新建文本文档.txt', r'D:\\新建文件夹', overWrite=False)

        :param pathSrc:[必选参数]源文件路径
        :param pathDst:[必选参数]目标文件夹路径
        :param overWrite:[可选参数]是否覆盖目标文件，默认False
        :return: bool
        """
    @staticmethod
    def MoveFolder(pathSrc: str, pathDst: str, overWrite: bool = False) -> bool:
        """
        移动文件夹

        File.MoveFolder(r'E:\\新建文件夹', r'D:', overWrite=False)

        :param pathSrc:[必选参数]源文件夹路径
        :param pathDst:[必选参数]目标文件夹路径
        :param overWrite:[可选参数]是否覆盖目标文件夹，默认False
        :return: bool
        """
    @staticmethod
    def ParentPath(path: str) -> str:
        """
        获取父级路径

        File.ParentPath(r'D:\\新建文件夹')

        :param path:[必选参数]文件夹路径
        :return: str，父文件夹路径
        """
    @staticmethod
    def Read(path: str, setchar: str = 'auto') -> str:
        '''
        读取文件内容

        File.Read(r\'D:\\新建文本文档.txt\', setchar="auto")

        :param path:[必选参数]文件路径
        :param setchar:[可选参数]文件字符集编码，例如gbk、utf-8等，默认auto，自动识别文件字符集
        :return: str，文件内容
        '''
    @staticmethod
    def RenameEx(pathSrc: str, newName: str) -> bool:
        """
        重命名文件或文件夹

        File.RenameEx(r'D:\\新建文件夹', '新文件夹')

        :param pathSrc:[必选参数]文件或文件夹路径
        :param newName:[必选参数]新名称
        :return: bool
        """
    @staticmethod
    def SearchFile(path: str, fileName: str, deepIter: bool = False) -> list:
        """
        查找文件，支持通配符与是否深度遍历

        File.SearchFile(r'D:\\新建文件夹', '*.txt', True)

        :param path:[必选参数]文件夹路径
        :param fileName:[必选参数]要查找的文件名，支持通配符*，例如：*.xlsx、*.*、*等
        :param deepIter:[可选参数]是否深度遍历，默认False
        :return: list，文件路径列表
        """
    @staticmethod
    def WriteFile(path: str, text: str, setchar: str = 'gbk') -> bool:
        """
        写入文件内容

        File.WriteFile(r'D:\\新建文本文档.txt', '这是要写入的内容', setchar='gbk')

        :param path:[必选参数]文件路径
        :param text:[必选参数]要写入的内容
        :param setchar:[可选参数]文件字符集编码，例如gbk、utf-8等，默认gbk
        :return: bool
        """
    @staticmethod
    def Append(path: str, text: str, setchar: str = 'gbk') -> bool:
        """
        追加写入文件内容

        File.Append(r'D:\\新建文本文档.txt', '这是要追加写入的内容', setchar='gbk')

        :param path:[必选参数]文件路径
        :param text:[必选参数]要追加写入的内容
        :param setchar:[可选参数]文件字符集编码，例如gbk、utf-8等，默认gbk
        :return: bool
        """

def retry(num: int = 2, delay: int | float = None, wait: int | float = None):
    """
    重试装饰器

    :param num:[可选参数]重试次数，数字代表尝试次数，None:不限尝试次数。默认2次
    :param delay:[可选参数]重试延时秒数（超过此秒数重试不了），默认None
    :param wait:[可选参数]重试间隔秒数，默认None
    """
