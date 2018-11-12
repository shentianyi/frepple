var ItemDetail = {}
var itemId = parseInt(window.location.pathname.split('/item_detail/')[1]);

var locationArray = [];
var supplierArray = [];

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
                FillData('item_detail', data.content);

                locationArray = data.content.location;
                console.log(data.content)
                if (locationArray.length > 0) {
                    const buffer = locationArray[0].buffer;
                    FillData('item_detail', buffer);
                }
            } else {
                alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

ItemDetail.getMainSuppliersData = function () {
    $.ajax({
        url: '/data/input/item/mainsuppliersdata/' + itemId + "/",
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // 填充数据
            if (data.result) {
                console.log('data', data.content);
                FillData('item_detail_main', data.content);
            } else {
                // alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

ItemDetail.getSuppliers = function () {
    $.ajax({
        url: '/data/input/item/suppliers/' + itemId + "/",
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // 填充数据
            if (data.result) {
                console.log('supplierdata', data);

                FillData('item_detail_supplier', data.content[0]);

                // FillData({supplier: data.content});

                supplierArray = data.content;
                var html = '';
                if (supplierArray.length > 0) {
                    for (var i = 0; i < supplierArray.length; i++) {
                        html += "<option value=" + supplierArray[i].id + ">" + supplierArray[i].id + "</option>"
                    }
                    $("#item_detail_supplier_id" ).append(html);
                }
                // if (supplierArray.length > 0) {
                //     const buffer = locationArray;
                //     FillData(buffer);
                // }
            } else {
                alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

ItemDetail.locationChange = function () {
    var selectedValue = $("#item_detail_location").val();

    if (locationArray.length > 0) {
        for (var i = 0; i < locationArray.length; i++) {
            if (selectedValue == locationArray[i].id) {
                FillData(locationArray[i].buffer);
                return;
            }
        }
    }
};

/**
 * 界面填充数据
 * 输入框
 * 下拉框
 * 复选框 - 待定
 * @param data 界面值
 * @constructor
 */
function FillData(prefix, data) {
    Object.keys(data).map(function (t) {
        var key = t;
        var value = data[t];

        if (value === null) {
            return;
        }

        var valueType = typeof (value);
        // console.log('valueType', valueType)
        switch (valueType) {
            case "string":
                $("#" + prefix + "_" + key).val(value);
                break;
            case "number":
                $("#" + prefix + "_" + key).val(value);
                break;
            case "object":
                var html = '';

                // 这个是下拉框或者数组
                if (Array.isArray(value)) {
                    // 仓库代码

                    if (value.length > 0) {
                        for (var i = 0; i < value.length; i++) {
                            html += "<option value=" + value[i].id + ">" + value[i].nr + "</option>"
                        }

                        $("#" + prefix + "_" + key).append(html);
                    }
                } else {

                    var currentValue = value.current;
                    var valueArray = value.values;

                    if (valueArray.length > 0) {
                        for (var i = 0; i < valueArray.length; i++) {
                            if (valueArray[i].text == currentValue) {
                                html += "<option selected value=" + valueArray[i].value + ">" + valueArray[i].text + "</option>"
                            } else {
                                html += "<option value=" + valueArray[i].value + ">" + valueArray[i].text + "</option>"
                            }
                        }

                        $("#" + prefix + "_" + key).append(html);
                    }
                }

                break;
            default:
                break;
        }
    });
}

// ItemDetail.getMainSuppliersData()


