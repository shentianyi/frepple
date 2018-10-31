var Forecast = {}

Forecast.operate = function (content_type, type, modalId) {
    if ($('#cancel').hasClass("disabled")) return;
    var sel = jQuery("#grid").jqGrid('getGridParam', 'selarrrow');
    if (sel.length > 0) {
        $("#" + modalId).modal('show');

        // I18n
        var title =gettext(type);

        $("#" + modalId).find("#operateModalTitle").html(title);

        $("#" + modalId).find("#operate_modal_confirm").unbind('click').bind('click', function () {
            var remark = $("#" + modalId).find("#operateModalRemark").val();

            // 再次确认弹框
            $("#" + modalId).modal('hide');
            $('#' + modalId).on('hidden.bs.modal', function (e) {
                $("#" + modalId).find("#operateModalRemark").val('');
            });

            $("#confirmDialog").modal('show');
            $("#confirmDialog").on('show.bs.modal', function () {
                $("#confirmDialog").find("#confirmDialogTitle").html(title);
                $("#confirmDialog").find("#confirmDialogContent").html('是否确认' + title + '?');
            });

            $("#confirmDialog").find("#confirmDialogSubmit").unbind('click').bind('click', function () {
                const data = {
                    content_ids: sel,
                    content_type: content_type,
                    operation: type,
                    comment: remark
                }

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
            for(var i = 0; i< data.length; i++){
                // remarkDetailTbody
                html += '<tr><td>'+(i+1)+'</td>' +
                    '<td>'+data[i].operation+'</td>' +
                    '<td>'+data[i].user__username+'</td>' +
                    '<td>'+data[i].created_at+'</td>' +
                    '<td>'+data[i].comment+'</td></tr>';
            }

            $("#remarkDetailTbody").empty();
            $("#remarkDetailTbody").html(html);
        },
        error: function (error) {
            alert(error.status + "\n" + error.responseText)
        }
    })
};