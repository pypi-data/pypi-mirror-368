from setuptools import setup, find_packages
 
setup(
    name='jxWebUI',  # 你的库名
    version='0.4.0',    # 版本号
    packages=find_packages(include=["jxWebUI", "jxWebUI.ui_web", "jxWebUI.ui_web.web", "jxWebUI.ui_web.descr", "jxWebUI.ui_web.demo"]),  # 自动查找包
    include_package_data=True,  # 包含非Python文件
    package_dir={
        "jxWebUI": "jxWebUI",  # 指定包根目录
    },
    package_data={
        "": ["docs/**/*","web/**/*", ]
    },
    exclude_package_data={
        "": [".idea/", "__pycache__/"],
        "jxWebUI": ["__pycache__/", "jxTMS.js"],
    },
    install_requires=[  # 依赖项
        'importlib_resources==6.4.5',
        'pycryptodome',
        'pytz',
        'apscheduler',
        'antlr4-python3-runtime==4.7.2',
        'tornado',
    ],
    long_description='''


jxWebUI是为python程序员开发的简单易用的WebUI库，通过简单的文本定义即可定义各种web界面发布使用。适合不追求炫酷的界面，而是侧重快速实现功能的python程序员。

### 版本更新说明

0.4.0版本的修改：

1、修复了一些bug

2、capaInstance增加了一个修饰符：close，用于capaInstance注销时执行清理任务

3、条件查询根据我们的使用习惯：开始时间是指定时间的零点零分零秒，而结束时间则是指定时间的23点59分59秒，因此如果需要设置查询起止时间，则锁定了两个对应的输入变量：start_time、end_time。会以此习惯来调整起始时间，必须将起止时间的日期时间选择框所绑定的变量名分为设为这两个变量名

4、capaInstance的setAttr增加了一个参数：base64:bool，用于设置属性值是否需要base64编码

### 说明

jxWebUI的使用非常简单，主要包括几个步骤：

1、导入依赖

	from jxWebUI import jxWebLogger, jxWebServer, jxWebCapa, jxWebGetUser, jxWebSQLGetDBConnection

2、创建一个capa

	capa = jxWebCapa('test.first_page')

capa就是一个桥【可以理解为一个功能模块】，把web界面和python代码衔接起来。这里定义了一个名为【test.first_page】的capa。对于名字，capa本身并无特殊要求，这里是为了便于代码组织，采用了点分方式。

3、通过capa定义一个界面

	@capa.disp  
	def test_web(ci, db, ctx):  
		jxWebLogger.info(f'testUI_tms::test_web')  
	    ci.setOutput('input1', '测试输出3')

	@capa.web  
	def test_web(page):  
        t = page.table('table1').width(900)
        r = t.row()
        r.text('text1').bind('text1').width(200)
        r.input('input1').bind('input1').width(200)

这就定义了一个【test_web】的页面：

![test_web](http://115.29.52.95:10018/images/test_web_1.png)

4、定义一个打开这个界面的快捷栏菜单
  
	capa.shortCutTree_add_item('测试', '测试1', 'test_web')

这会在左侧的快捷工具栏中出现一个二级目录：测试->测试1

![test_web](http://115.29.52.95:10018/images/test_web_2.png)

点击【测试1】就会显示上面的【test_web】页面。

5、启动web服务

	jxWebServer.start(port=10068)

启动后，打开： http://127.0.0.1:10068/tms.html# 会弹出一个登录窗口，随便输入用户名和密码就会登入。

<font color=red size=3>注：</font>：用户认证，请参考【用户】一节

因为jxWebUI需要做一点初始化的工作，所以可能要等两三秒中，就会在左侧的快捷栏，出现【测试->测试1】。点击测试1就会弹出test_web界面。

<font color=red size=3>注：</font>：因python代码第一次执行时需进行编译，启动后第一次打开页面时，编译时间如果超过了这个等待时间，可能导致页面无法打开，多刷新几次即可。

需要注意的是，和上面的截图不同，输入框中会出现：【测试输出3】。这是因为我们还定义了一个用【@capa.disp】修饰的【test_web】事件函数。

jxWebUI在显示一个页面时，会调用这个函数来实现对该页面的初始化工作。

初始化test_web函数的代码：

	jxWebLogger.info(f'testUI_tms::test_web') 

会将字符串【testUI_tms::test_web】以info级别记入jxWebLogger。其对应的日志文件位于执行程序所在目录的子目录【./logs】中的【jxWebUI.log】。

	ci.setOutput('input1', '测试输出3')

是将一个字符串【测试输出3】输出到web界面的【input1】中，根据test_web函数中的定义，也就是输出到文本输入框中。

总的代码是：

	from jxWebUI import jxWebLogger, jxWebServer, jxWebCapa, jxWebGetUser, jxWebSQLGetDBConnection

	capa = jxWebCapa('test.first_page')

	@capa.disp  
	def test_web(ci, db, ctx):  
		jxWebLogger.info(f'testUI_tms::test_web')  
	    ci.setOutput('input1', '测试输出3')

	@capa.web  
	def test_web(page):  
        t = page.table('table1').width(900)
        r = t.row()
        r.text('text1').bind('text1').width(200)
        r.input('input1').bind('input1').width(200)
  
	capa.shortCutTree_add_item('测试', '测试1', 'test_web')

	jxWebServer.start(port=10068)

将上述代码保存为testUI_tms.py，然后在命令行执行：

	python3 testUI_tms.py

然后在浏览器中打开： http://127.0.0.1:10068/tms.html# 进行查看。

### jxWebUI编程指南

请在python解释器中执行：

    >>> from jxWebUI import startJxWebUIManualServer
    >>> startJxWebUIManualServer(port=10068, web_def=True)
    
然后在浏览器中打开： http://127.0.0.1:10068/tms.html# 随便输入用户名、密码登录后，就可以查看到编程手册的目录：

![编程手册](http://115.29.52.95:10018/images/sc_1.png)

整体说明菜单下是jxWebUI编程的总体概念和API说明等，web组件说明菜单下则详细介绍了已开放的web组件的说明和属性等。点击这二者的章节会以markdown的形式提供相应的说明：

![编程手册](http://115.29.52.95:10018/images/sc_2.png)

web组件定义菜单下则提供了一个jxWebUI自举的web组件定义和展示功能：

![编程手册](http://115.29.52.95:10018/images/sc_3.png)

![编程手册](http://115.29.52.95:10018/images/sc_4.png)

### 安装jxWebUI

	pip install jxWebUI

### 日志

启动jxWebUI后，会在当前目录下的logs子目录【没有则会自动创建】中会创建两个日志文件：

- jxWebUI.log：是jxWebUI的运行日志，包括用户的操作等
- web.log：jxWebUI的web服务所依赖的tornado的日志

这两种日志都是30个日志文件、每个日志文件500M进行循环，所以如长期运行需注意硬盘空间的使用情况。



    ''',
    long_description_content_type="text/markdown",
    author='徐晓轶',
    author_email='andrew@pythonpi.top',
    description='简单易用的python Web UI库',
    url='https://blog.csdn.net/jxandrew/article/details/148670848',  # 项目的URL
    python_requires=">=3.8",
)
