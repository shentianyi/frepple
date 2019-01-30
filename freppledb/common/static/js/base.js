// 日期转化
var Base = {}

// 日期格式化,不是插件的代码,只用于处理时间格式化
Date.prototype.format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1, //月份
        "D+": this.getDate(), //日
        "d+": this.getDate(), //日
        "H+": this.getHours(), //小时
        "h+": this.getHours(), //小时
        "m+": this.getMinutes(), //分
        "s+": this.getSeconds(), //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds() //毫秒
    };
    if (/([Y,y]+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    }
    for (var k in o) {
        if (new RegExp("(" + k + ")").test(fmt)) {
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        }
    }
    return fmt;
};

// 日期+时间
$(".datetime-picker").datetimepicker({
    timepicker: true,
    step: 1,
    format: 'Y-m-d H:i:s',
    formatDate: 'Y-m-d H:i:s',
});

$.datetimepicker.setLocale('ch');


// ajax全局拦截器
$.ajaxSetup({
    cache: false,
    complete: function (XMLHttpRequest) {
        let res = XMLHttpRequest.responseText;
        const status = XMLHttpRequest.status;
        const resData = JSON.parse(res);
        try {
            switch (status) {
                case 200:
                    console.log('AJAX STATUS 200', resData);
                    break;
                case 401:
                    $('#status-401').modal('show');

                    let timer = window.setInterval(function () {
                        $('#status-401').modal('hide');
                        window.location.href = '/data/login/';
                        window.clearInterval(timer);
                    }, 3000);
                    break;
            }

        } catch (e) {
        }
    }
});