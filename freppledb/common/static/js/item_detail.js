var ItemDetail = {}
var itemId = parseInt(window.location.pathname.split('/item_detail/')[1]);


ItemDetail.getMainData = function () {
    $.ajax({
        url: '/data/input/item/maindata/' + itemId + "/",
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // 填充数据
            if (data.result) {
                // data.content

                //id 规则： item_detail + 字段名
                // input框： 直接填充

                // 下拉框： 需要匹配current， 默认选中

                // 复选框： 直接checked 或者 不是
                FillData(data.content)

            } else {
                alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

/**
 * 界面填充数据
 * 输入框
 * 下拉框
 * 复选框 - 待定
 * @param data 界面值
 * @constructor
 */
function FillData(data) {
    Object.keys(data).map(function (t) {
        var key = t;
        var value = data[t];

        if (value === null) {
            return;
        }

        var valueType = typeof (value);

        switch (valueType) {
            case "string":
                $("#item_detail_" + key).val(value);
                break;
            case "number":
                $("#item_detail_" + key).val(value);
                break;
            case "object":
                var html = '';

                // 这个是下拉框或者数组
                if (Array.isArray(value)) {
                    // 仓库代码

                    for (var i = 0; i < value.length; i++) {
                        html += "<option value=" + value[i].id + ">" + value[i].nr + "</option>"
                    }

                    $("#item_detail_" + key).append(html);
                } else {

                    var currentValue = value.current;
                    var valueArray = value.values;

                    for (var i = 0; i < valueArray.length; i++) {
                        if (valueArray[i].text == currentValue) {
                            html += "<option selected value=" + valueArray[i].value + ">" + valueArray[i].text + "</option>"
                        } else {
                            html += "<option value=" + valueArray[i].value + ">" + valueArray[i].text + "</option>"
                        }
                    }

                    $("#item_detail_" + key).append(html);
                }

                break;
            default:
                break;
        }
    });
}


