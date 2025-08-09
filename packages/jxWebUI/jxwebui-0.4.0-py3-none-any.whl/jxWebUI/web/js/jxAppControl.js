
var appClientID;
function setClient(id){
	appClientID=id;
}
function postToAppServer(name,value){
	var url="/app/input";
   $.jxREST("/app/input",{Source:"/webClient/"+name,Value:value,ClientID:appClientID});
}

//
//按钮控件
//
;
(function($) {
	var methods = {
		init: function(options) {
 			var defaults = {
 				Name: "jxAppButton",
				Text: '执行',
				Value: 0
			};
 			var settings = $.extend({}, defaults, options);
 			var d=$('<div style="width:320px;margin:10 10 10 10px;"></div>');
         d.appendTo($(this));
         
 			var div = $('<button type="button" style="width:320px;margin:10 10 10 10px;" class="btn btn-primary">'+settings.Text+'</button>');
         div.appendTo(d);
         div.click(function(event){
         	postToAppServer(settings.Name,settings.Value);
         });
 			div.data("jxAppButton", settings);
        return div;
		}
	};

	$.fn.jxAppButton = function() {
		var method = arguments[0];
 		if(methods[method]) {
			method = methods[method];
			arguments = Array.prototype.slice.call(arguments, 1);
		} else if( typeof(method) == 'object' || !method ) {
			method = methods.init;
		} else {
			$.error( 'Method ' +  method + ' does not exist on plugin:'+"jxAppButton" );
			return this;
		}
 		return method.apply(this, arguments);
 	}
})(jQuery);

//
//滑块控件
//
(function($) {
	var methods = {
		init: function(options) {
 			var defaults = {
 				Name: "jxAppSlider",
				Text: '滑块',
				Value: 0
			};
 			var settings = $.extend({}, defaults, options);
 			var d=$('<div style="width:320px;margin:10 10 10 10px;"></div>');
         d.appendTo($(this));
 			var h=$('<H3 >'+settings.Text+'</H3>');
         h.appendTo(d);
         
 			var div = $('<input type="text" style="width:320px;margin:10 10 10 10px;"/>');
         div.appendTo(d);
 			settings.jqObj=div.slider({
 				max:100
 			});
         settings.jqObj.slider('setValue', settings.Value);
         settings.jqObj.on("change",function(event){
         	postToAppServer(settings.Name,event.value.newValue);
         });
 			div.data("jxAppSlider", settings);
        	return div;
		},
		setVaue: function(value) {
		    var tobj = $(this).data("jxAppSlider");
          tobj.jqObj.slider('setValue', value);
		}
	};

	$.fn.jxAppSlider = function() {
		var method = arguments[0];
 		if(methods[method]) {
			method = methods[method];
			arguments = Array.prototype.slice.call(arguments, 1);
		} else if( typeof(method) == 'object' || !method ) {
			method = methods.init;
		} else {
			$.error( 'Method ' +  method + ' does not exist on plugin:'+"jxAppSlider" );
			return this;
		}
 		return method.apply(this, arguments);
 	}
})(jQuery);

//
//操纵舵控件
//
var HelmSize=320;
var barWidth=8;
(function($) {
	var methods = {
		init: function(options) {
 			var defaults = {
 				Name: "jxAppHelm",
				Text: '操纵舵'
			};
         var dual=false;
 			var settings = $.extend({}, defaults, options);
 			var d=$('<div style="width:320px;margin:10 10 10 10px;"></div>');
         d.appendTo($(this));
 			var h=$('<H3 >'+settings.Text+'</H3>');
         h.appendTo(d);
         
 			var div = $('<div style="margin:10 10 10 10px;"></div>');
         div.appendTo(d);
        	div.jxCanvas({Width: HelmSize,Height: HelmSize});
        	div.jxCanvas("setStrokeStyle","#0000ff");
        	div.jxCanvas("strokeRect",1,1,HelmSize-1,HelmSize-1);
         
         div.mousedown(function(){
         	dual=true;
         	postToAppServer(settings.Name,1);
         });
         div.mouseup(function(){
         	dual=false;
         	postToAppServer(settings.Name,0);
         });
         div.mousemove(function(e){
        		if(!dual)return;
        		var e = e ? e : window.event;
        		if(e.which == 1){
					var dx=e.offsetX - HelmSize/2;
					var dy=e.offsetY  - HelmSize/2;
        			var radian1=Math.atan2(dy,dx)+Math.PI/2;
        			var radian=Math.atan2(-dy,dx);
					var barLength=Math.pow((dx * dx + dy *dy), 0.5);
					if(barLength>HelmSize/2)
					barLength=HelmSize/2;					
        			div.jxCanvas("rotateRect",HelmSize/2,HelmSize/2,radian1,{width:barWidth,height:barLength});
        			div.jxCanvas("strokeRect",1,1,HelmSize-1,HelmSize-1);
         		postToAppServer(settings.Name+"_radian",radian);
         		postToAppServer(settings.Name+"_power",barLength*2*100/HelmSize);
        		}
         });
 			div.data("jxAppHelm", settings);
        	return div;
		}
	};

	$.fn.jxAppHelm = function() {
		var method = arguments[0];
 		if(methods[method]) {
			method = methods[method];
			arguments = Array.prototype.slice.call(arguments, 1);
		} else if( typeof(method) == 'object' || !method ) {
			method = methods.init;
		} else {
			$.error( 'Method ' +  method + ' does not exist on plugin:'+"jxAppHelm" );
			return this;
		}
 		return method.apply(this, arguments);
 	}
})(jQuery);

