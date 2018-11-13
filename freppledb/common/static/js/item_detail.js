var ItemDetail = {}
var itemId = parseInt(window.location.pathname.split('/item_detail/')[1]);

var locationArray = [];
var supplierArray = [];

//获取公共数据
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

                if (locationArray.length > 0) {
                    const buffer = locationArray[0].buffer;
                    FillData('item_detail', buffer);
                }
            } else {
                // alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

//获取主数据
ItemDetail.getMainSuppliersData = function () {
    $.ajax({
        url: '/data/input/item/mainsupplierdata/' + itemId + "/",
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // 填充数据
            if (data.result) {
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

//获取供应商数据
ItemDetail.getSuppliersData = function () {
    $.ajax({
        url: '/data/input/item/suppliers/' + itemId + "/",
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // 填充数据
            if (data.result) {

                FillData('item_detail_supplier', data.content[0]);

                supplierArray = data.content;
                var html = '';
                if (supplierArray.length > 0) {
                    for (var i = 0; i < supplierArray.length; i++) {
                        html += "<option value=" + supplierArray[i].nr + ">" + supplierArray[i].nr + "</option>"
                    }
                    $("#item_detail_supplier_nr").append(html);
                }
            } else {
                // alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

//获取计划数据
ItemDetail.getPlansData = function () {
    $.ajax({
        url: '/data/input/item/plansdata/' + itemId + "/",
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // 填充数据
            if (data.result) {

                FillData('item_detail_plan', data.content);

            } else {
                // alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

//获取预测界面grid数据
ItemDetail.getForecastGridData = function (date_type, report_type) {

    var locationId = $("#item_detail_location").val();
    var tableColModel = [
        {
            name: 'x',
            label: '',
        },
    ];

    $("#content-main").append('<table id="grid" class="table table-striped pivotgrid"></table>');

    jQuery("#grid").jqGrid({
        url: "/data/output/forecast/item/?id=" + itemId + "&location_id=" + locationId + "&date_type=" + (date_type ? date_type : '') + "&report_type=" + (report_type ? report_type : ''),
        datatype: "json",
        jsonReader: {
            repeatitems: false
        },
        colModel: tableColModel,
        pager: '#gridpager',
        emptyrecords: "无数据显示",
        loadtext: "卖力加载中...",
        // rownumbers: true,
        shrinkToFit: false,
        autoScroll: true,
        // rowNum: {{ request.pagesize }},
        viewrecords: true,
        // sortorder: "asc",
        iconSet: "fontAwesome",
        guiStyle: "bootstrapPrimary",
        hidegrid: false,
        resizeStop: grid.saveColumnConfiguration,
        scrollRows: true,
        autowidth: true,
        // multiSort: true,
        // maxSortColumns: 3,
        // viewSort: true,
        // onSortCol: grid.saveColumnConfiguration,
        // onPaging: grid.saveColumnConfiguration,
//                postData: {filters: JSON.stringify(filterParams)},
//                 postData: {filters: filterParams},
//                 search:true,
//                 searching: {
//                     multipleSearch: true,
//                     multipleGroup: false, // 不可以组搜索
//                     closeOnEscape: true,
//                     searchOnEnter: true,
//                     searchOperators: true,
//                     zIndex: 5000,
//                     width: 550
//                 },
        loadComplete: function () {
            $("#gird").closest(".ui-jqgrid-bdiv").css({'overflow-y': 'auto'});
        }
    })
};

//获取预测界面chart数据
ItemDetail.getForecastChartData = function (date_type, report_type) {

    var locationId = $("#item_detail_location").val();
    // var forecastChart = echarts.init($("#item_detail_forecast_chart"));

    $.ajax({
        url: "/data/output/forecast/item_report/?id=" + itemId + "&location_id=" + locationId + "&date_type=" + (date_type ? date_type : '') + "&report_type=" + (report_type ? report_type : ''),
        type: 'application/json',
        method: 'get',
        success: function (data) {
            if (data.result) {
                const series = data.content.serials
                console.log('data-----------------', data);

                var legendData = [];
                var xAxis = [];
                var yFAxis = [];
                var yDAxis = [];
                var currentValue = data.content.current_time_point.x_text;
                console.log('currentValue-----------------', currentValue);
                // var allSeries = [];

                for (var i = 0; i < series.length; i++) {
                    legendData.push(series[i].serial);
                    for (var j = 0; j < series[i].points.length; j++) {
                        xAxis.push(series[i].points[j].x_text)
                    }
                    if (series[i].serial_type === 'FORECAST BASIS') {
                        for (var k = 0; k < series[i].points.length; k++) {
                            yFAxis.push(series[i].points[k].y);
                            yDAxis.push(100);
                        }
                    } else if (series[i].serial_type === 'DEMAND FORECAST') {
                        for (var k = 0; k < series[i].points.length; k++) {
                            yDAxis.push(series[i].points[k].y)
                            yFAxis.push(100);
                        }
                    }
                }
                // console.log('---------legendData--------', legendData);
                // console.log('---------xAxis--------', xAxis);
                // console.log('---------yFAxis--------', yFAxis);
                // console.log('---------yDAxis--------', yDAxis);

                var forecastChart = echarts.init(document.getElementById('item_detail_forecast_chart'));
                // console.log(forecastChart)

                // for (var i = 0; i < legendData.length; i++) {
                //     switch (legendData[i]) {
                //         case 'Dispatches(Forecast basis)':
                //             var series = {
                //                 name: legendData[i],
                //                 type: 'bar',
                //                 data: yFAxis,
                //             };
                //             allSeries.push(series);
                //         case 'Demand forecast':
                //
                //     }
                // }

                var option = {
                    title: {
                        show: false
                    },
                    tooltip: {
                        position: [0, 0]
                    },
                    legend: {
                        data: legendData
                    },
                    xAxis: {
                        data: xAxis
                    },
                    yAxis: {
                        show: false,
                    },
                    dataZoom: [
                        {
                            show: true,
                            start: 94,
                            end: 100,
                            orient: "horizontal"
                        },
                        {
                            type: 'inside',
                            start: 94,
                            end: 100
                        },
                        {
                            show: true,
                            yAxisIndex: 0,
                            filterMode: 'empty',
                            width: 30,
                            height: '80%',
                            showDataShadow: false,
                            left: '93%'
                        }
                    ],
                    series: [{
                        name: 'Dispatches(Forecast basis)',
                        type: 'bar',
                        data: yFAxis,
                        markLine: {
                            symbol:"none",
                            lineStyle: {
                                type: 'solid',
                                color: 'black',
                                width: '2px',

                                // normal: {
                                //     type: 'solid',
                                // }
                            },
                            data: [
                                // {type: 'average', name: '当前值'},
                                {xAxis: currentValue}
                            ]
                        }
                    },
                        {
                            name: 'Demand forecast',
                            type: 'bar',
                            data: yDAxis,
                        },
                    ],
                };
                forecastChart.setOption(option);
            } else {
                // alert(data.message)
            }
        },
        error: function (err) {
            alert(err);
        }
    })
};

//切换仓库代码时相应数据一起变化
ItemDetail.locationChange = function () {
    var selectedValue = $("#item_detail_location").val();

    if (locationArray.length > 0) {
        for (var i = 0; i < locationArray.length; i++) {
            if (selectedValue == locationArray[i].id) {
                FillData('item_detail', locationArray[i].buffer);
                return;
            }
        }
    }
};

//切换供应商代码时相应数据一起变化
ItemDetail.supplierChange = function () {
    var selectedValue = $("#item_detail_supplier_nr").val();

    if (supplierArray.length > 0) {
        for (var i = 0; i < supplierArray.length; i++) {
            if (selectedValue == supplierArray[i].nr) {
                FillData('item_detail_supplier', supplierArray[i]);
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


