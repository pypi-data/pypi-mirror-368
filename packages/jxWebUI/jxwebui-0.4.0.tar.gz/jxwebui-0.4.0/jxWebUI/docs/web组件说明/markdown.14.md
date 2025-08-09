markdown格式的输出显示控件。

# markdown

## 定义格式

	markdown 控件名 属性列表 ;

## 属性

### bind
类型：string
缺省值：

markdown只用于输出，其为base64编码，所以输出内容应使用base64编码：

	capaInstance.setOutput_base64(bind_var_name, content)

### width
类型：int
缺省值：

控件的宽度。

宽度并非绝对量，而是根据表格行中各控件的width属性在所有控件的width总和的占比来分配各控件的实际宽度的。