var Forecast = {}

var title = "取消";
Forecast.operate = function (content_type, type, modalId) {
    if ($('#cancel').hasClass("disabled")) return;
    var sel = jQuery("#grid").jqGrid('getGridParam', 'selarrrow');
    if (sel.length > 0) {
        $("#" + modalId).modal('show');

        // I18n
        var title = gettext(type);

        $("#" + modalId).find("#operateModalTitle").html(title);
        $("#" + modalId).find("#operate_modal_confirm").unbind('click').bind('click', function () {
            var remark = $("#" + modalId).find("#operateModalRemark").val();

            // 再次确认弹框
            $("#" + modalId).modal('hide');
            $('#' + modalId).on('hidden.bs.modal', function () {
                $("#" + modalId).find("#operateModalRemark").val('');
            });

            $("#confirmDialog").modal('show');
            $("#confirmDialog").find("#confirmDialogTitle").html(title);
            $("#confirmDialog").find("#confirmDialogContent").html('是否确认' + title + '?');

            $("#confirmDialog").find("#confirmDialogSubmit").unbind('click').bind('click', function () {
                const data = {
                    content_ids: sel,
                    content_type: content_type,
                    operation: type,
                    comment: remark
                };

                $.ajax({
                    url: '/data/input/forecastcomment/',
                    method: 'post',
                    contentType: 'application/json; charset=utf-8',
                    dataType: "json",
                    data: JSON.stringify(data),
                    success: function (data) {
                        if (data.result) {
                            window.location.reload();
                        } else {
                            alert(data.message)
                        }
                    },
                    error: function (error) {
                        alert(error.status + "\n" + error.responseText)
                    }
                })
            })
        })
    }
};

Forecast.showDetail = function (id, type) {
    $("#remarkDetail").modal('show');

    $.ajax({
        url: '/data/input/forecastcomment/',
        type: 'get',
        contentType: 'application/json',
        dataType: 'json',
        data: {
            content_id: id,
            content_type: type
        },
        success: function (data) {
            var html = '';
            for (var i = 0; i < data.length; i++) {
                html += '<tr><td>' + (i + 1) + '</td>' +
                    '<td>' + data[i].operation + '</td>' +
                    '<td>' + data[i].comment + '</td>' +
                    '<td>' + data[i].user__username + '</td>' +
                    '<td>' + data[i].created_at + '</td>' +
                    '</tr>';
            }

            $("#remarkDetailTbody").empty();
            $("#remarkDetailTbody").html(html);
        },
        error: function (error) {
            alert(error.status + "\n" + error.responseText)
        }
    })
};

/**
 * 下载
 * @param querys 附带的查询条件, 是个String，开头用&连接
 */
Forecast.download = function (querys) {
    // $("#aggre").find('img').attr('src', '{{STATIC_URL}}img/forecast/aggre.png');
    // $("#detail").find('img').attr('src', '{{STATIC_URL}}img/forecast/detail.png');
    // $("#filter").find('img').attr('src', '{{STATIC_URL}}img/forecast/search.png');
    // $("#download").find('img').attr('src', '{{STATIC_URL}}img/forecast/download_active.png');

    $("#downloadDialog").modal('show');

    $("#downloadDialogSubmit").unbind('click').bind('click', function () {
        var postdata = $("#grid").jqGrid('getGridParam', 'postData');

        console.log('postdata', postdata);
        var format = $("[name=downloadType]:checked").val();

        var url = '/data/output/forecast/compare/?format=' + format + '&mode=' + currentMode + '&report_type=' + currentType;
        url += "&" + jQuery.param(postdata);
        url += querys;
        window.location.href = url;
    });
};

Forecast.downloadForecastVersion = function (querys) {

    $("#downloadDialog").modal('show');

    $("#downloadDialogSubmit").unbind('click').bind('click', function () {
        var format = $("[name=downloadType]:checked").val();
        var url = '/data/input/forecastversion/?format=' + format + "&nr=" + querys;
        console.log(url);
        window.location.href = url;
    });
};

Forecast.showItemDetail = function (key) {
    console.log(key);
    var url = '/data/input/item_detail/' + key +'/';
    window.location.href = url;
};