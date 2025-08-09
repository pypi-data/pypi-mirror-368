//当前的课件号
var coursewarePageOrder = 0;
var coursewareNumber = 0;
var coursewareNext;

function getCourseWare(strurl) {
    var html;
    var url = getUrlWithQueryString(strurl);
    $.jxRequest(url, null, function(json) {
        document.title = json.title;
        coursewarePageOrder = json.order;
        coursewareNumber = json.num;
        //
        //java的base64编码函数会自动添加“\n”，由于javascript无法解析字符串中的回车符，所以后台
        //会将回车替换为--br--，而$.base64则不需要这个回车，所以需要将其全部删掉
        //
        var re1 = /--br--/gmi;
        var str = json.content.replace(re1, '');
        var s = $.base64.atob(str, true);
        var s2 = markdown.toHTML(s);
        var re2 = /<a /gmi;
        html = s2.replace(re2, '<a target="_blank" ');
        //alert(html);
    });
    return html;
}

function getCourseWareByName(name) {
    var html;
    var url = getUrlWithQueryString("/course/getCourseWareByName");
    $.jxRequest(url, null, function(json) {

        coursewareNext = json.next;
        document.title = json.title + "--PythonPi"

        //
        //java的base64编码函数会自动添加“\n”，由于javascript无法解析字符串中的回车符，所以后台
        //会将回车替换为--br--，而$.base64则不需要这个回车，所以需要将其全部删掉
        //
        var re1 = /--br--/gmi;
        var str = json.Content.replace(re1, '')
        var s = $.base64.atob(str, true);
        var s2 = markdown.toHTML(s);
        var re2 = /<a /gmi;
        html = s2.replace(re2, '<a target="_blank" ');
    });
    return html;
}

//控制器：显示课件
jx.controller('controller_coursePlay', function($scope, $http, $location) {

    $scope.dispCourseWare = function(num) {

        coursewarePageOrder = coursewarePageOrder + num;

        $scope.CurrentOrder = coursewarePageOrder;

        var name = getQueryString("Name");
        if (name)
            $("#course_content").html(getCourseWareByName());
        else
            $("#course_content").html(getCourseWare("/course/getCourseWare"));

        if (coursewarePageOrder == 1) {
            $("#coursePlayPrev").addClass('disabled');
            $("#coursePlayPrev_D").addClass('disabled');
        } else {
            $("#coursePlayPrev").removeClass('disabled');
            $("#coursePlayPrev_D").removeClass('disabled');
        }
        if (coursewarePageOrder < coursewareNumber) {
            $("#coursePlayNext").removeClass('disabled');
            $("#coursePlayNext_D").removeClass('disabled');
        } else {
            $("#coursePlayNext").addClass('disabled');
            $("#coursePlayNext_D").addClass('disabled');
        }

    };

    var pagenum = getQueryString("pageOrder");
    if (pagenum) {
        $scope.dispCourseWare(parseInt(pagenum));
    } else
        $scope.dispCourseWare(1);
});

//控制器：显示课件目录
jx.controller('controller_coursewareCatalogue', function($scope, $http, $location) {

    var url = getUrlWithQueryString("/course/listCourseWareCatalogue/");
    $.jxRequest(url, null, function(json) {

        var href = "course_play.html";
        var length = json.length;
        for (var i = 0; i < length; i++) {
            if (!json[i].authority) {
                json[i].href = getUrlWithQueryStringAndPamam(href, "pageOrder", i + 1);
                json[i].activeDesc = "开始学习";
            } else {
                json[i].href = "#";
                json[i].activeDesc = "没有权限";
            }
        }

        $scope.list = json;

    });

});

function coursePlay_return() {
    var url = getUrlWithQueryString("/course/getCourseID");
    //alert(url)
    $.jxRequest(url, null, function(json) {
        var url = getUrlAddSessionIDAndParam("courseware_list.html", "courseID", json.courseID);
        window.location.href = url;
    });
    //history.go(-1);
}

//
//导航条
//
//通用的菜单选项
jx.controller('controller_NavbarCtrl', function($scope, $http, $location) {

    //收集当前页面url中的session信息
    checkSession();
    //var sid=getQueryString("jxSessionID");
    //if(!sid)
    //	window.location.href="login.html";

    var array = [{
        "label": "首页",
        "href": "index.html",
        "children": []
    }, {
        "label": "课程列表",
        "href": "courseList.html",
        "children": []
    }];
    var title = "PythonPi";
    var length = array.length;
    for (var i = 0; i < length; i++) {
        array[i].href = getUrlAddSessionID(array[i].href);
        //alert(array[i].href)
        if (array[i].children && array[i].children.length > 0) {
            var ch = array[i].children;
            var len = ch.length;
            for (var j = 0; j < len; j++) {
                ch[j].href = getUrlAddSessionID(ch[j].href);
            }
        }
    }

    $scope.navbar = array;
    $scope.navTitle = title;
    $scope.editPersonInfo = getUrlAddSessionID("editPersonInfo.html");

    $scope.doFunc = function(funcName) {
        //执行用户指定的函数
        callFunc(funcName);
    };
});

//控制器：课程列表
//用名字来访问
jx.controller('controllerCourseList', function($scope, $http, $location) {
    checkSession();
    var url = "/course/listCourse/";
    $.jxRequest(url, null, function(json) {

        var href = "coursewareList.html";
        var length = json.length;
        for (var i = 0; i < length; i++) {
            json[i].href = getUrlWithQueryStringAndPamam(href, "course", json[i].Order);
        }

        $scope.list = json;

    });
});

//控制器：课件列表
//用名字来访问
jx.controller('controllerCourseWareList', function($scope, $http, $location) {
    checkSession();
    var url = getUrlWithQueryString("/course/listCourseWare/");
    $.jxRequest(url, null, function(json) {

        //var href="course_play.html";
        var href2 = "sectionList.html";
        var length = json.length;
        for (var i = 0; i < length; i++) {
            json[i].href2 = getUrlWithQueryStringAndPamam(href2, "courseware", json[i].Order);
        }

        $scope.list = json;

    });
});

//控制器：显示课件目录
//用名字来访问
jx.controller('controllerSectionList', function($scope, $http, $location) {
    checkSession();
    var url = getUrlWithQueryString("/course/listSection/");
    $.jxRequest(url, null, function(json) {

        var href = "coursePlay.html";
        var length = json.length;
        for (var i = 0; i < length; i++) {
            //var h1 = getUrlAddSessionIDAndParam(href, "course", json[i].course);
            //var h2 = getUrlAddSessionIDAndParam(h1, "courseware", json[i].courseware);
            json[i].href = getUrlWithQueryStringAndPamam(href, "section", json[i].Order);
        }

        $scope.list = json;

    });

});
//控制器：显示课件
jx.controller('controllerCoursePlay', function($scope, $http, $location) {
    checkSession();
    $scope.dispCourseWare = function(num) {

        coursewarePageOrder = coursewarePageOrder + num;

        $scope.CurrentOrder = coursewarePageOrder;

        var href = "/course/getCourseWare";
        var h2 = getUrlWithQueryStringAndPamam(href,'section',coursewarePageOrder);
        $("#course_content").html(getCourseWare(h2));

        if (coursewarePageOrder == 1) {
            $("#coursePlayPrev").addClass('disabled');
            $("#coursePlayPrev_D").addClass('disabled');
        } else {
            $("#coursePlayPrev").removeClass('disabled');
            $("#coursePlayPrev_D").removeClass('disabled');
        }
        if (coursewarePageOrder < coursewareNumber) {
            $("#coursePlayNext").removeClass('disabled');
            $("#coursePlayNext_D").removeClass('disabled');
        } else {
            $("#coursePlayNext").addClass('disabled');
            $("#coursePlayNext_D").addClass('disabled');
        }

    };
    $scope.dispCatalogue = function(num) {
        var url = getUrlWithQueryString("coursewareList.html");
        window.location.href = url;
    };

    var pagenum = getQueryString("section");
    if (pagenum) {
        $scope.dispCourseWare(parseInt(pagenum));
    } else
        $scope.dispCourseWare(1);
});

//控制器：课程总目录
jx.controller('controller_courseCatalogue', function($scope, $http, $location) {
    var url = getUrlWithQueryString("/course/listCourseWare/");
    $.jxRequest(url, {
        listCatalogue: true
    }, function(json) {

        $('#tree').treeview({
            data: json,
            enableLinks: true
        });

    });
});

//控制器：课件列表
jx.controller('controller_coursewareList', function($scope, $http, $location) {

    var url = getUrlWithQueryString("/course/listCourseWare/");
    $.jxRequest(url, null, function(json) {

        //var href="course_play.html";
        var href2 = "coursewareCatalogue.html";
        var length = json.length;
        for (var i = 0; i < length; i++) {
            //json[i].href=getUrlAddSessionIDAndParam(href,"coursewareID",json[i].ID);
            json[i].href2 = getUrlAddSessionIDAndParam(href2, "coursewareID", json[i].ID);
        }

        $scope.list = json;

    });
});


//控制器：发布消息
jx.controller('controller_issueMsg', function($scope, $http, $location) {

    var msgEditor = dispCodeEditor_ace("msg_editor", "markdown");

    $scope.issueMsg_ok = function() {
        var c1 = msgEditor.getValue();
        var url = getUrlWithQueryString("/msg/addMsg/");
        $.jxRequest(url, {
            msgSummary: $scope.msgSummary,
            msgDesc: $.base64.btoa(c1, true)
        }, function(json) {
            alert("消息已发布！");

        });
    };
});

//控制器：创建用户
jx.controller('controller_createUser', function($scope, $http, $location) {
    $scope.Saddress = "地址";
    $scope.Sdesc = "备注";

    $scope.setUserType = function() {
        if ($scope.userType) {
            //$("#userName").attr("disabled",false);
            $scope.Saddress = "部门";
            $scope.Sdesc = "职务";
        } else {
            $("#userName").attr("disabled", true);
            $scope.Saddress = "地址";
            $scope.Sdesc = "备注";
        }
    };

    $scope.createuser = function() {

        var url = getUrlWithQueryString("/system/createUser/");
        $.jxRequest(url, {
                Type: $scope.userType,
                Name: $scope.userName,
                Mobile: $scope.mobile,
                Mail: $scope.mail,
                Address: $scope.address,
                Descr: $scope.desc
            },
            function(json) {
                alert("用户已创建：" + json.Name + "/登陆密码：" + json.Passwd);

            });
    };

});
function getMinimumCut() {
	var html;
   var url=getUrlWithQueryString("/course/getMinimumCut");
    $.jxRequest(url,null,function (json) {
    	//
    	//java的base64编码函数会自动添加“\n”，由于javascript无法解析字符串中的回车符，所以后台
    	//会将回车替换为--br--，而$.base64则不需要这个回车，所以需要将其全部删掉
    	//
    	var re1 = /--br--/gmi;
    	var str=json.rules.content.replace(re1,'');
    	var s=$.base64.atob(str,true);
    	var s2= markdown.toHTML(s);
    	var re2 = /<a /gmi;
    	html= s2.replace(re2,'<a target="_blank" ');
    	//alert(html);
    });
    return html;
}
//控制器：显示规则
jx.controller('controller_minimumCut', function ($scope,$http,$location) {
	$("#course_content").html(getMinimumCut());
});
