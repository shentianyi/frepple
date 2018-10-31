var Forecast = {}

Forecast.operate = function (content_type, type, modalId) {
    if ($('#cancel').hasClass("disabled")) return;
    var sel = jQuery("#grid").jqGrid('getGridParam', 'selarrrow');
    if (sel.length > 0) {
        $("#" + modalId).modal('show');

        var title = "取消";
        switch (type) {
            case "operation_forecast_ok":
                title = "审批";
                break;
            case "operation_forecast_nok":
                title = "打回";
                break;
            case "operation_forecast_cancel":
                title = "取消";
                break;
            case "operation_forecast_release":
                title = "放行";
                break;
            default:
                break;
        }

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
                    contentType : 'application/json; charset=utf-8',
                    dataType: "json",
                    data: JSON.stringify(data),
                    success: function (data) {
                        if(data.result){
                            window.location.reload();
                        }else{
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