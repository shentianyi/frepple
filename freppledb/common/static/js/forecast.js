var Forecast = {}

Forecast.operate = function (content_type, type, modalId) {
    if ($('#cancel').hasClass("disabled")) return;
    var sel = jQuery("#grid").jqGrid('getGridParam', 'selarrrow');
    if (sel.length > 0) {
        $("#"+ modalId).modal('show')

        $("#"+ modalId).on('show.bs.modal', function () {
            var title = "取消";
            switch (type){
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

            $("#"+modalId).find("#operateModalTitle").html(title);
        });

        $("#"+modalId).find("#operate_modal_confirm").unbind('click').bind('click', function () {
            var remark = $("#"+modalId).find("#operateModalRemark").val();

            // 再次确认弹框
            $("#confirmDialog").modal('show');
            $("#confirmDialog").on('show.bs.modal', function () {
                $("#confirmDialog").find("#confirmDialogTitle").html(title)
                $("#confirmDialog").find("#confirmDialogContent").html('是否确认'+title+'?')

            });

            $("#confirmDialog").find("#confirmDialogSubmit").unbind('click').bind('click', function () {
                $.ajax({
                    url: '/data/input/forecastcomment/',
                    method: 'post',
                    data: {
                        content_id: sel,
                        content_type: content_type,
                        operation: type,
                        comment: remark
                    },
                    success: function (data) {
                        console.log(data)
                    },
                    error: function (error) {
                        console.log(error)
                    }
                })
            })
        })
    }
};