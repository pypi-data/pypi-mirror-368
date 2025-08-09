
var mainDivCtl;
var auxDivCtl;
//各类型控件的属性窗口描述，key：type
var ctlAttrList = new Map();

var capaid;
var spacename;
var modelname;
var pagename;
var rootDesc;
var currentCtl;
var currentLocalData = new Map();

//返回值指示是否修改了控件的属性
function dualTextAttr(ctl,bind,v){
    switch (bind) {
        case 'ctlText':


            return true;
    }
    return false;
}
//属性显示的各属性值控件的name应等于bind
function dispTextCtlAttr(ctl){
    var ac;
    var js = allCtlJson.get(ctl.name);
    //显示text属性
    ac = allCtl.get('ctlText');
    ac.ctl.val(js.text);
    //显示text属性
    ac = allCtl.get('ctlText');
    ac.ctl.val(js.text);
}
//创建当前控件的子控件
function newSubCtl(type,place){
    var ctl;
    switch (ctl.type) {
        case 'text':
            ctl = newTextCtl(currentCtl);
            break;
    }
    if(ctl)
        ctlClickFunc(ctl);
}
function searchParent(subname){
    return searchParentName(rootDesc);
}
function searchParentName(desc,subname){
    var p = desc;
    if(p.cs && p.cs.length > 0)
        for (var i = 0; i < p.cs.length; i++) {
            var sd = p.cs[i];
            if(sd.name == subname)
                return p.name;
            else{
                var sp = searchParentName(sd,subname);
                if(sp)
                    return sp;
            }
        }
    if(p.ctls && p.ctls.length > 0)
        for (i = 0; i < p.ctls.length; i++) {
            sd = p.ctls[i];
            if(sd.name == subname)
                return p.name;
            else{
                var sp = searchParentName(sd,subname);
                if(sp)
                    return sp;
        }
    return null;
}
function getPlaceInParent(ctlname){
    var ss = getNumberFromStr(ctlname);
    return parseInt(ss[ss.length-1]);
}
//在当前控件的前面创建兄弟控件
function newBigBrotherCtl(type){
    var ctl;
    var pn = searchParent(currentCtl.name);
    var pc = allCtl.get(pn);
    var myPlace = getPlaceInParent(currentCtl.name);
    switch (ctl.type) {
        case 'text':
            ctl = newTextCtl(pc,myPlace);
            break;
    }
    if(ctl)
        ctlClickFunc(ctl);
}



function dispCtlAttr(ctl){
    switch (ctl.type) {
        case 'text':
            dispTextCtlAttr(ctl);
            break;
    }
}
//主界面控件点击事件响应函数
function ctlClickFunc(jxCtl){
    currentCtl = jxCtl;
    //jxCtl是根据json所生成的控件对象
    //点击该控件则显示其属性
    var cd = ctlAttrList.get(jxCtl.type);
    if(cd){
        auxDivCtl.empty();
        //点击该控件则在辅助区显示该控件的属性
        $.getWebObject(cd, auxDivCtl,function(bind,v){
            var b=false;
            //属性变化
            switch (currentCtl.type) {
                case 'text':
                    b = dualTextAttr(currentCtl,bing,v);
                    break;
                case 'input':
                    b = dualInputAttr(currentCtl,bing,v);
                    break;
            }
            if(b){
                //属性被调整，则删除原控件并重新创建
                var js = allCtlJson.get(currentCtl.name);
                jxCtl.ctl.remove();
                currentCtl = $.getWebObject(js,jxCtl.parent,null,ctlClickFunc);
            }
        });
        dispCtlAttr(currentCtl);
    }
}

function dualWeb(json) {
    //allCtlJson定义在jxTMS.js中，当其被声明，getWebObject就会将每个定义加入其中
    allCtlJson = new Map();
    allCtl = new Map();

    mainDivCtl.empty();
    $.getWebObject(json, mainDivCtl,null,ctlClickFunc);
}

function getResult(vn){
    currentLocalData.get(vn);
}
function dualResult(json) {
    if (!json) return;
    var out = json.out;
    if (out)
        for (var i = 0; i < out.length; i++) {
            var wo = out[i];
            switch (wo.woID) {
                case "localData":
                    currentLocalData.put(wo.attr, wo.data);
                    break;
            }
        }
    return null;
}
function doCapabilityCmd(demand,ps) {
    var param = {};
    param.capaid = capaid;
    param.type = 'cmd';
    param.demand = demand;
    var np ={};
    param.params = np;
    np.space = spacename;
    np.model = modelname;
    np.page = pagename;
    if(ps)
        np.data = ps;
    currentLocalData.put('execResult', false);
    $.jxREST("/ui/motion", param, function(json) {
        if (!json) return;
        dualResult(json);
    });
}
//控制器入口，采用此种方式为避免被uglifyjs使用-m参数【执行变量替换】压缩时无法识别这两个注入依赖
jx.controller('uiEdit', ['$scope', '$rootScope', function($scope, $rootScope) {

    var ie;
    if (document.all) ie = true;
    else ie = false; //判断是否为IE
    document.onkeydown = KeyPress; //设置键盘事件
    function KeyPress() {
        var key;
        if (ie) key = event.keyCode; //IE使用event.keyCode获取键盘码
        else key = KeyPress.arguments[0].keyCode; //firefox使用我们定义的键盘函数arguments[0].keyCode来获取键盘码
        if (key == 9) {
            window.event.returnValue = false;
        }
    }
    bootbox.setDefaults("locale", "zh_CN");

    $.setSessionID($.getUrlParam('jxSessionID'));
    capaid = $.getUrlParam('capaid');
    spacename = $.getUrlParam('space');
    modelname = $.getUrlParam('model');
    pagename = $.getUrlParam('page');

    allCtl = new Map();
    allCtlJson = new Map();

    doCapabilityCmd('initDisp');

    rootDesc = getResult('web');
    if(rootDesc)
        dualWeb(rootDesc, mainDivCtl);
    else
        rootDesc = {};

    $scope.save = function() {
        bootbox.confirm({
            message: '确定要保存吗?',
            callback: function(result) {
                if (result){
                    doCapabilityCmd('save');
                    var execResult = getResult('execResult');
                    if(execResult)
                        bootbox.alert("已保存！");
                    else
                        bootbox.alert("保存失败！");
                }
            }
        });
    };
}]);
