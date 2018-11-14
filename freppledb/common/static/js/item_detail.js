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

    $.ajax({
        url: '/data/output/forecast/item/?id=' + itemId + '&location_id=' + locationId + '&date_type=' + (date_type ? date_type : '') + '&report_type=' + (report_type ? report_type : ''),
        type: 'application/json',
        method: 'get',
        success: function (data) {
            if (data.result) {
                var tableColModel = [{
                    name: 'location', index: 'location', cellattr: function (rowId, tv, rawObject, cm, rdata) {
                        //合并单元格
                        return 'id=\'location' + rowId + "\'";
                    }
                }, {name: 'type', index: 'type'}];
                var tableColName = ['', ''];
                var rowData = []
                var forecastGridData = data.content.data;
                // console.log('---------data', data);
                if (forecastGridData.length > 0) {

                    // 七个属性
                    // total, last_sale_qty, actual_sale_qty，new_product_plan_qty, normal_qty, promotion_qty, ratio, system_forecast_qty,

                    var totalRowData = {
                        location: "仓名",
                        type: "合计",
                    };
                    var lastRowData = {
                        location: "仓名",
                        type: "去年销量",
                    };
                    var actualRowData = {
                        location: "仓名",
                        type: "实际销量",
                    };
                    var systemRowData = {
                        location: "仓名",
                        type: "系统统计预测",
                    };
                    var ratioRowData = {
                        location: "仓名",
                        type: "配额系数",
                    };
                    var normalRowData = {
                        location: "仓名",
                        type: "手工预测",
                    };
                    var newRowData = {
                        location: "仓名",
                        type: "新产品上市计划量",
                    };
                    var promotionRowData = {
                        location: "仓名",
                        type: "促销量",
                    };


                    for (var i = 0; i < forecastGridData.length; i++) {
                        var everyCol = {name: forecastGridData[i].x, index: forecastGridData[i].x};
                        tableColName.push(forecastGridData[i].x);
                        tableColModel.push(everyCol);
                        // eachRowData[forecastGridData[i].x] = forecastGridData[i].y.total;
                        totalRowData[forecastGridData[i].x] = forecastGridData[i].y.total;
                        lastRowData[forecastGridData[i].x] = forecastGridData[i].y.last_sale_qty;
                        actualRowData[forecastGridData[i].x] = forecastGridData[i].y.actual_sale_qty;
                        systemRowData[forecastGridData[i].x] = forecastGridData[i].y.system_forecast_qty;
                        ratioRowData[forecastGridData[i].x] = forecastGridData[i].y.ratio;
                        normalRowData[forecastGridData[i].x] = forecastGridData[i].y.normal_qty;
                        newRowData[forecastGridData[i].x] = forecastGridData[i].y.new_product_plan_qty;
                        promotionRowData[forecastGridData[i].x] = forecastGridData[i].y.promotion_qty;
                    }

                    rowData.push(totalRowData);
                    rowData.push(lastRowData);
                    rowData.push(actualRowData);
                    rowData.push(systemRowData);
                    rowData.push(ratioRowData);
                    rowData.push(normalRowData);
                    rowData.push(newRowData);
                    rowData.push(promotionRowData);

                    // console.log('-----------------------rowData', rowData);
                    $("#content-main").append('<table id="grid" class="table table-striped pivotgrid"></table>');

                    jQuery("#grid").jqGrid({
                        datatype: "local",
                        data: rowData,
                        localReader: {
                            repeatitems: false
                        },
                        colNames: tableColName,
                        colModel: tableColModel,
                        pager: '#gridpager',
                        emptyrecords: "无数据显示",
                        loadtext: "卖力加载中...",
                        shrinkToFit: false,
                        autoScroll: true,
                        viewrecords: true,
                        iconSet: "fontAwesome",
                        guiStyle: "bootstrapPrimary",
                        hidegrid: false,
                        resizeStop: grid.saveColumnConfiguration,
                        scrollRows: true,
                        autowidth: true,
                        loadComplete: function () {
                            $("#gird").closest(".ui-jqgrid-bdiv").css({'overflow-y': 'auto'});
                        },
                        gridComplete: function () {
                            //在gridComplete调用合并方法
                            ItemDetail.Merger('grid', 'location');
                        }

                    })
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

//公共调用方法
ItemDetail.Merger = function (gridName, CellName) {
    //得到显示到界面的id集合
    var mya = $("#" + gridName + "").getDataIDs();
    //当前显示多少条
    var length = mya.length;
    for (var i = 0; i < length; i++) {
        //从上到下获取一条信息
        var before = $("#" + gridName + "").jqGrid('getRowData', mya[i]);
        //定义合并行数
        var rowSpanTaxCount = 1;
        for (j = i + 1; j <= length; j++) {
            //和上边的信息对比 如果值一样就合并行数+1 然后设置rowspan 让当前单元格隐藏
            var end = $("#" + gridName + "").jqGrid('getRowData', mya[j]);
            if (before[CellName] == end[CellName]) {
                rowSpanTaxCount++;
                $("#" + gridName + "").setCell(mya[j], CellName, '', {display: 'none'});
            } else {
                rowSpanTaxCount = 1;
                break;
            }
            $("#" + CellName + "" + mya[i] + "").attr("rowspan", rowSpanTaxCount);
        }
    }
}

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
                // console.log('data-----------------', data);

                var legendData = [];
                var xAxis = [];
                var yFAxis = [];
                var yDAxis = [];
                var currentValue = data.content.current_time_point.x_text;
                // console.log('currentValue-----------------', currentValue);
                // var allSeries = [];

                for (var i = 0; i < series.length; i++) {
                    legendData.push(series[i].serial);
                    if (series[i].serial_type === 'FORECAST BASIS') {
                        for (var k = 0; k < series[i].points.length; k++) {
                            yFAxis.push(series[i].points[k].y);
                            // yDAxis.push(100);
                        }
                    } else if (series[i].serial_type === 'DEMAND FORECAST') {
                        for (var k = 0; k < series[i].points.length; k++) {
                            yDAxis.push(series[i].points[k].y)
                            // yFAxis.push(100);
                        }
                    }
                }

                for (var i = 0; i < series[0].points.length; i++) {
                    xAxis.push(series[0].points[i].x_text)
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
                            symbol: "none",
                            lineStyle: {
                                color: 'black',
                                width: '2px',

                                normal: {
                                    type: 'solid',
                                }
                            },
                            data: [
                                {
                                    name: '当前值',
                                    xAxis: currentValue
                                },
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


