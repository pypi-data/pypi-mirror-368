jxWebUI初版的web界面定义是格式化字符串方式，对新手程序员不太友好。所以在0.2版本，jxWebUI提供了编程式web界面定义。

原理非常简单，就是套个壳，将用代码描述的界面翻译成初版中相应的格式化web界面定义字符串，然后再解释为web界面描述对象。

先看一下代码，有个感性的认识：

	@capa.web  
	def list_user(page):  
	    t = page.dataTable('table_user').width(900).title('用户列表')  
	    t.col('createTime').head('创建时间').width(300)  
	    t.col('username').head('用户名').width(200)  
	    t.col('op1').head('操作').width(80).a().text('删除').motion('cmd').demand('del_user').require(['username']).confirm('确定要删除用户吗？')  
	    t.col('op2').head('操作').width(80).a().text('重置密码').motion('cmd').demand('reset_passwd').require(['username']).confirm('确定要重置用户密码吗？')

界面显示效果如下：

![用户列表](http://115.29.52.95:10018/images/bcsw_1.png)


为实现编程式web界面定义，jxWebUI在capa中增加了一个新的修饰符：web。其修饰的函数将带入一个名为page的参数，开发者就可以在page上创建各种web组件了。

如list_user函数所示，编程式web界面定义是**流式编程**，一行就可以完整的定义完一个web组件。其代码形如：

	(子组件 =)? [page或page创建的容器型web组件].web组件类型(可选组件名).属性定义列表[属性名(属性值)]

其中：

只有后继需在其中创建子组件的容器型组件才需要被赋值，非容器型组件不需要被赋值【即忽略掉上面等式的左部(子组件 = )】。

容器型组件包括：page、table、dataTable、row。

web组件类型请查看编程手册中的【web组件说明】。

各web组件的属性及其属性值的相关说明也请查看编程手册中的【web组件说明】。

### 查看jxWebUI编程手册
  
请在python解释器中执行：

    >>> from jxWebUI import startJxWebUIManualServer
    >>> startJxWebUIManualServer(port=10068, web_def=True)
    
然后在浏览器中打开： http://127.0.0.1:10068/tms.html# 随便输入用户名、密码登录后，就可以查看到编程手册的目录。

### 为实现编程式web界面所做的调整
  
编程式web界面定义相比格式化字符串web界面定义有一个冲突点：格式化字符串web界面定义的界面描述是在page修饰的函数的doc的字符串中，所以其一个函数同时承担了两个职能：

1、函数的doc字符串描述了所定义的web界面

2、函数体的代码就是该页面在显示时的初始化代码，用来完成界面打开时的数据装订任务

而编程式web界面定义则由于web界面的描述也是通过函数代码实现，所以格式化字符串web界面定义用page修饰一个函数所能完成的工作，在编程式web界面定义就必须用两个函数来完成。

用了两个函数，就引出了一个问题：函数同名冲突。为了减少混淆与困惑，jxWebUI都是用函数名来指代界面名，那么现在就会出现两个同名函数，一个用来定义界面、一个用来初始化界面。

因此，为支持编程式web界面定义，0.2版本的jxWebUI在enevt修饰符之外专门为界面初始化启用了disp修饰符，以修饰web界面初始化事件函数；为避免语义的含糊，又专门增加了cmd修饰符则专门用于按钮点击事件响应函数。

<font color=red size=3>注：</font>event和cmd具有相同的功能。建议用语义更明确的cmd取代event

概括来说，为支持编程式web界面定义，0.2版本的jxWebUI做了如下的调整：

1、新增capa.web修饰符，供开发者以编程的方式来描述web界面

2、新增capa.disp修饰符，用来关联web界面初始化事件响应

3、新增capa.cmd修饰符，用来关联web界面中各按钮的点击事件响应

### 示例说明--用户管理

	_user_list ={
		'admin':{
			'createTime': '2025-01-01 00:00:00',
			'password': '123456'
		},
		'user1':{
			'createTime': '2025-02-01 00:00:00',
			'password': '123456'
		},
	}
	#创建capa
	capa = jxWebCapa('mgr.user')
	
	#添加快捷栏入口
	#只有admin用户能查看用户、添加用户
	capa.shortCutTree_add_item('用户管理', '查看用户', 'list_user', authority='admin')
	capa.shortCutTree_add_item('用户管理', '添加用户', 'add_user', authority='admin')
	#所有用户都能修改自己的密码
	capa.shortCutTree_add_item('用户管理', '修改密码', 'change_passwd')

	#列表所有用户
	def disp_list_user(ci):
		#生成列表数据
	    rs = []
	    for k, v in _user_list.items():
	        rs.append({'username':k, 'createTime':v.get('createTime', '')})
		#将列表数据发送到table_user表
	    ci.set_output_datatable('table_user', rs)
	
	#list_user界面显示后的数据装订函数
	@capa.disp
	def list_user(ci, db, ctx):
	    disp_list_user(ci)
	
	#list_user界面定义函数。注意：list_user函数有两个，上面是用disp修饰的界面初始化函数
	#本函数则是用web修饰的web界面描述函数
	@capa.web
	def list_user(page):
	    #在page中创建一个数据表，表名table_user，然后指定width、title属性
	    t = page.dataTable('table_user').width(900).title('用户列表')
	    #table_user中创建两列，分别用于显示本行用户的用户名和创建时间
	    t.col('createTime').head('创建时间').width(300)
	    t.col('username').head('用户名').width(200)
	    #table_user中继续创建两个操作列，分别用于删除用户和重置用户密码
	    t.col('op1').head('操作').width(80).a().text('删除').motion('cmd').demand('del_user').require(['username']).confirm('确定要删除用户吗？')
	    #操作列，需要用require属性来指定本操作所关联的特征参数，这里是username，同时由于删除和重置密码都会严重影响用户的使用，所以都使用了confirm属性要求操作前确认
	    t.col('op2').head('操作').width(80).a().text('重置密码').motion('cmd').demand('reset_passwd').require(['username']).confirm('确定要重置用户密码吗？')
	
	#删除用户的按钮点击事件响应函数
	@capa.cmd
	def del_user(ci, db, ctx):
	    #获取经由前述【删除】按钮定义中的require属性处理后关联到的要删除的用户名
	    username = ci.getInput('username')
	    if username=='admin':
	        #当要删除admin用户时，弹窗告警，然后退出
	        ci.web_info('警告', '不能删除admin用户')
	        return
	    #删除用户操作
	    
	    #删除用户后，需要刷新用户列表。这个动作分为两步，先清除原表，然后再次显示
	    ci.setAttr('table_user', 'clear', True)
	    disp_list_user(ci)

	#重置密码的按钮点击事件响应函数
	@capa.cmd
	def reset_passwd(ci, db, ctx):
	    username = ci.getInput('username')
	    init_passwd(username, _default_passwd_normal)
	
	#修改密码的界面定义函数，不需要初始化
	@capa.web
	def change_passwd(page):
	    #在page中创建一个容器表，和前面的list_user相比，这里没有给出表名【list_user中是dataTable('table_user')】
	    #所有的web组件如果不给出名字，则jxWebUI会自动起一个内部的名字，list_user中的table_user需要显式给出一个名字的
	    #原因是因为要用set_output_datatable输出数据与清空表，所以必须知道表名，当不需要操作组件时，就不需要显式给出组件名
	    t = page.table().width(900).title('修改用户密码')
	    #在容器表中创建一行
	    r = t.row()
	    #在行中添加各种组件，这些组件行列对齐
	    r.text().width(200).text('新密码')
	    #作为输入控件，bind了一个数据名：new_password，用户的输入在事件函数中，就能用ci.getInput函数读取到了
	    r.input().width(200).bind('new_password')
	    r.text().width(200).text('再次输入密码')
	    r.input().width(200).bind('new_password_2')
	    #在容器表再中创建一行
	    r = t.row()
	    #在行再添加一个按钮，注意宽度不同，但行列还是对齐了
	    r.button().width(100).text('修改').motion('cmd').demand('change_passwd').confirm('确定要修改用户密码吗？')

	#修改密码的按钮点击事件响应函数，虽然和界面定义函数同名，但现在因为event改为了disp和cmd的分流，所以虽然同名但不会影响事件的正确响应
	@capa.cmd
	def change_passwd(ci, db, ctx):
	    pwd1 = ci.getInput('new_password')
	    pwd2 = ci.getInput('new_password_2')
	    if pwd1 != pwd2:
	        ci.web_info('警告', '两次输入的密码不一致')
	        return
		#本页面是从快捷栏打开的，而快捷栏无法如数据表行那样带有用户名参数，这些就需要从ctx【上下文】中获取到用户名
		username = ctx.user.abbr()
	    #修改密码
	    #change_password(username, pwd1)
	
	#添加用户的界面定义和按钮点击响应，同修改密码
	@capa.web
	def add_user(page):
	    t = page.table().width(900).title('创建用户')
	    r = t.row()
	    r.text().width(200).text('用户名')
	    r.input().width(200).bind('username')
	    r = t.row()
	    r.button().width(100).text('创建').motion('cmd').demand('add_user').confirm('确定要创建用户吗？')
	
	@capa.cmd
	def add_user(ci, db, ctx):
	    username = ci.getInput('username')
	    #添加用户

对应的web界面显示效果如下：

列表用户：

![用户列表](http://115.29.52.95:10018/images/bcsw_1.png)

添加用户：

![用户列表](http://115.29.52.95:10018/images/bcsw_2.png)

修改密码：

![用户列表](http://115.29.52.95:10018/images/bcsw_3.png)