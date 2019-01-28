var ItemDetail = {}
var itemId = parseInt(window.location.pathname.split('/item_detail/')[1]);

var locationArray = [];
var supplierArray = [];


//获取计划界面grid数据
ItemDetail.getPlanGridData = function () {
    var tableColModel = [
        {
            name: 'date_number',
            label: '日月/周数',
        },
        {

            name: 'qty',
            label: '数量',
        },
        {
            name: 'move_types',
            label: '移动类型',
        },
        {
            name: 'name',
            label: '供应商/客户',
        },
        {
            name: 'order_num',
            label: '单号',
        },
        {
            name: 'order_line_num',
            label: '订单行号',
        },
        {
            name: 'buffer',
            label: '库存',
        },
    ];

    $("#content-main-plan").append('<table id="planGrid" class="table table-striped pivotgrid"></table>');
    // $("#content-main-plan").append('<div id="plangridpager" class="col-md-12"></div>');
    // $("#planGrid").setGridWidth($('#content-main-plan').width());


    jQuery("#planGrid").jqGrid({
        url: '/data/output/item/buffer_operate_records/?id=' + itemId,
        datatype: "json",
        jsonReader: {
            repeatitems: false
        },
        colModel: tableColModel,
        pager: '#plangridpager',
        emptyrecords: "无数据显示",
        loadtext: "读取中...",
        rowNum: 20,//一页显示多少条
        prmNames: {
            "rows": "page_size",
            "page": "page",
        },
        // rownumbers: true,
        // rownumWidth: 20,
        shrinkToFit: false,
        autoScroll: true,
        viewrecords: true,
        iconSet: "fontAwesome",
        guiStyle: "bootstrapPrimary",
        hidegrid: false,
        resizeStop: planGrid.saveColumnConfiguration,
        scrollRows: true,
        onPaging: planGrid.saveColumnConfiguration,
        autowidth: true,

        loadComplete: function () {

            $("#planGrid").closest(".ui-jqgrid-bdiv").css({'overflow-y': 'scroll'});
            $("#planGrid").closest(".ui-jqgrid-bdiv").css({'overflow-x': 'scroll'});
            $("#planGrid").setGridWidth($('#content-main-plan').width()).setGridHeight('350');

            $(function () {
                $(window).resize(function () {
                    $("#planGrid").setGridWidth($('#content-main-plan').width());
                });
            });
        }
    });
}

//获取计划界面chart数据
ItemDetail.getPlanChartData = function (date_type, report_type) {
    var DateTypeValue = $("#plan_chart_chooseMonth").val();
    var locationId = $("#item_detail_location").val();

    $.ajax({
        url: "/data/output/plan/item_report/?id=" + itemId + "&location_id=" + locationId + "&date_type=" + (date_type ? date_type : DateTypeValue) + "&report_type=" + (report_type ? report_type : ''),
        type: 'application/json',
        method: 'get',
        success: function (data) {
            // console.log('-------------data', data);
            if (data.result) {
                const series = data.content.serials
                var legendData = ['current_time_point', 'lead_time_point'];
                var xAxis = [];
                var seriesPlan = [];
                var currentValue = data.content.current_time_point.x_text;
                var leadTimeValue = data.content.lead_time_point.x_text;


                for (var i = 0; i < series.length; i++) {
                    var yAxis = [];
                    legendData.push(series[i].serial);
                    for (var j = 0; j < series[i].points.length; j++) {
                        yAxis.push(series[i].points[j].y);
                    }
                    // var chartType = series[i].serial_type !== '';
                    var chartType = 'bar';
                    seriesPlan[i] = {name: series[i].serial, type: chartType, data: yAxis};
                }
                seriesPlan.push({
                    name: 'current_time_point', type: 'bar', data: [], markLine: {
                        symbol: "none",
                        lineStyle: {
                            normal: {
                                type: 'solid',
                            }
                        },
                        label: {
                            formatter: ''
                        },
                        data: [
                            {
                                name: '当前值',
                                xAxis: currentValue
                            },
                        ]
                    }
                });
                seriesPlan.push({
                    name: 'lead_time_point', type: 'bar', data: [], markLine: {
                        symbol: "none",
                        lineStyle: {
                            normal: {
                                type: 'solid',
                            }
                        },
                        label: {
                            formatter: ''
                        },
                        data: [
                            {
                                name: '提前期',
                                xAxis: leadTimeValue
                            },
                        ]
                    }
                });

                for (var i = 0; i < series[0].points.length; i++) {
                    xAxis.push(series[0].points[i].x_text)
                }

                // console.log('-------legendData------', legendData);
                // console.log('-------xAxis------', xAxis);
                // console.log('-------seriesPlan------', seriesPlan);
                var planChart = echarts.init(document.getElementById('item_detail_plan_chart'));
                var simulationChart = echarts.init(document.getElementById('item_detail_simulation_chart'));

                var option = {
                    title: {
                        show: false
                    },
                    tooltip: {},
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
                            start: 0,
                            end: 100,
                            orient: "horizontal"
                        },
                        {
                            type: 'inside',
                            start: 0,
                            end: 100
                        },
                    ],
                    series: seriesPlan
                };
                planChart.setOption(option);
                simulationChart.setOption(option);
            }
        },
        error: function (err) {
            alert(err);
        }
    })
}


//获取模拟界面grid数据
ItemDetail.getSimulationGridData = function () {
    var tableColModel = [
        {
            name: 'date_number',
            label: '日月/周数',
        },
        {

            name: 'qty',
            label: '数量',
        },
        {
            name: 'move_types',
            label: '移动类型',
        },
        {
            name: 'name',
            label: '供应商/客户',
        },
        {
            name: 'order_num',
            label: '单号',
        },
        {
            name: 'order_line_num',
            label: '订单行号',
        },
        {
            name: 'buffer',
            label: '库存',
        },
    ];

    $("#content-main-simulation").append('<table id="simulationGrid" class="table table-striped pivotgrid"></table>');
    // $("#content-main-simulation").append('<div id="simulationgridpager" class="col-md-12"></div>');
    // $("#simulationGrid").setGridWidth($('#content-main-simulation').width());

    jQuery("#simulationGrid").jqGrid({
        url: '/data/output/item/buffer_operate_records/?id=' + itemId + '&page=1&page_size=100',
        datatype: "json",
        jsonReader: {
            repeatitems: false
        },
        colModel: tableColModel,
        pager: '#simulationgridpager',
        emptyrecords: "无数据显示",
        loadtext: "读取中...",
        rowNum: 20,//一页显示多少条
        prmNames: {
            "rows": "page_size",
            "page": "page",
        },
        shrinkToFit: false,
        autoScroll: true,
        viewrecords: true,
        iconSet: "fontAwesome",
        guiStyle: "bootstrapPrimary",
        hidegrid: false,
        // resizeStop: simulationGrid.saveColumnConfiguration,
        scrollRows: true,
        // onPaging: simulationGrid.saveColumnConfiguration,
        autowidth: true,

        loadComplete: function () {

            $("#simulationGrid").closest(".ui-jqgrid-bdiv").css({'overflow-y': 'scroll'});
            $("#simulationGrid").closest(".ui-jqgrid-bdiv").css({'overflow-x': 'scroll'});
            $("#simulationGrid").setGridWidth($('#content-main-simulation').width()).setGridHeight('300');
            $(function () {
                $(window).resize(function () {
                    $("#simulationGrid").setGridWidth($('#content-main-simulation').width());
                });
            });
        }
    });
}


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

//根据料号是否锁定控制“到期”是否为必填
ItemDetail.lockTypeChange = function () {
    var selectedValue = $("#item_detail_lock_types").val();

    if (selectedValue === 'locked') {
        $("#item_detail_lock_expire_at_required").css('display', 'inline-block');
        $("#item_detail_lock_expire_at").attr('required', 'true');
    } else {
        $("#item_detail_lock_expire_at_required").css('display', 'none');
        $("#item_detail_lock_expire_at").attr('required', 'false');
    }
};

//切换查询时间类型获取数据
ItemDetail.DateTypeChange = function (name, ifGrid) {
    var currentGridValueForecast = $("#forecast_grid_chooseMonth").val();
    var currentChartValueForecast = $("#forecast_chart_chooseMonth").val();
    var currentChartValuePlan = $("#plan_chart_chooseMonth").val();
    var currentChartValueSimulation = $("#simulation_chart_chooseMonth").val();

    if (name === 'forecast') {
        if (ifGrid) {
            $("#forecastGrid").GridDestroy();
            $("#content-main-forecast").append('<table id="forecastGrid" class="table table-striped pivotgrid"></table>');
            $("#content-main-forecast").append('<div id="forecastgridpager" class="col-md-12"></div>');
            ItemDetail.getForecastGridData(currentGridValueForecast);
        } else {
            $("#main-item_detail_forecast_chart").remove();
            $("#main-chart").append('<div id="item_detail_forecast_chart"></div>');
            ItemDetail.getForecastChartData(currentChartValueForecast);
        }
    } else if (name === 'plan') {
        if (!ifGrid) {
            $("#item_detail_plan_chart").remove();
            $("#plan-chart").append('<div id="item_detail_plan_chart" style="height: 300px; width: 100%;"></div>');
            ItemDetail.getPlanChartData(currentChartValuePlan);
        }
    } else if (name === 'simulation') {
        if (!ifGrid) {
            $("#item_detail_simulation_chart").remove();
            $("#simulation-chart").append('<div id="item_detail_simulation_chart" style="height: 300px; width: 100%;"></div>');
            ItemDetail.getPlanChartData(currentChartValueSimulation);
            e
        }
    }

}

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

                    if (currentValue === null) {
                        html += "<option value=" + currentValue + " style='display: none' >----</option>"
                    }

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

ItemDetail.FillOption = function (id) {
    var html = '';
    html += "<option value= W> 周 </option>";
    html += "<option value= M> 月 </option>";
    $("#" + id).append(html);
}


window.onload = function () {
    const mainTab = {
        name: 'main-tab',
        data() {
            return {
                mainData: {},
            }
        },
        mounted() {
            $(".vDateField").datetimepicker({
                timepicker: false,
                format: 'Y-m-d',
                formatDate: 'Y-m-d',
                defaultDate: new Date().format("YYYY-MM-DD"),
            });
        },
        created() {
        },
        methods: {}

    };

    const supplierTab = {
        name: 'supplier-tab',
        data() {
            return {
                supplierData: [
                    {
                        address: null,
                        city: null,
                        contact: null,
                        cost: null,
                        cost_unit: null,
                        country: null,
                        email: null,
                        id: null,
                        name: null,
                        nr: null,
                        phone: null,
                        supplier_item_nr: null,
                        telephone: null
                    }
                ],
                supplierSelected: 0, // 选中的选项在数组中的数组下标
            }
        }
    };

    const planTab = {
        name: 'plan-tab'
    };

    const simulationTab = {
        name: 'simulation-tab'
    }

    const forecastTab = {
        name: 'forecast-tab',
        data() {
            return {
                forecastTableDateType: 'W',
                forecastChartDateType: 'W'
            }
        },
        methods: {
            changeDateType(type) {
                let name = 'handle-' + type + '-date-change';
                this.$emit(name);
            }
        }
    };

    new Vue({
        delimiters: ['{[', ']}'],
        name: '单个物料',
        el: '#item-detail',
        components: {
            'main-tab': mainTab,
            'supplier-tab': supplierTab,
            'plan-tab': planTab,
            'simulation-tab': simulationTab,
            'forecast-tab': forecastTab
        },
        data() {
            return {
                tab: 'main',
                publicData: {
                    available_inventory: null,
                    description: null,
                    id: null,
                    inventory_cost: null,
                    inventory_qty: null,
                    location: {current: null, values: []},
                    lock_expire_at: null,
                    lock_types: {current: null, values: []},
                    nr: null,
                    plan_strategies: {current: null, values: []},
                    price_abc: null,
                    project_nr: null,
                    qty_abc: null,
                    statuses: {current: null, values: []},
                    successor_nr: null,
                }
            }
        },
        created() {
            this.getMainData();
            this.getMainSuppliersData();
        },
        mounted() {
            $(".vDateField").datetimepicker({
                timepicker: false,
                format: 'Y-m-d',
                formatDate: 'Y-m-d',
                defaultDate: new Date().format("YYYY-MM-DD"),
            });
        },
        methods: {
            //  TAB页切换
            changeTab(tabType) {
                this.tab = tabType;
                switch (tabType) {
                    case 'main':
                        this.getMainSuppliersData();
                        break;
                    case 'supplier':
                        this.getSuppliersData();
                        break;
                    case 'plan':
                        break;
                    case 'simulation':
                        this.getSimulationData();
                        break;
                    case 'forecast':
                        this.getForecastGridData();
                        this.getForecastChartData();
                        break;
                    default:
                        this.getMainSuppliersData();
                        break;
                }
            },
            // 获取公共数据
            getMainData() {
                const _this = this;
                if (this.publicData.location.current) {
                    url = '/data/input/item/maindata/' + itemId + "/?location_id=" + this.publicData.location.current;
                } else {
                    url = '/data/input/item/maindata/' + itemId + "/";
                }
                $.ajax({
                    url: url,
                    type: 'application/json',
                    method: 'get',
                    success: function (data) {
                        // 填充数据
                        if (data.result) {
                            _this.publicData = data.content;
                            _this.location_id = _this.location_id ? _this.location_id : 0;
                        } else {
                            // alert(data.message)
                        }
                    },
                    error: function (err) {
                        alert(err);
                    }
                })
            },
            // 获取主数据TAB
            getMainSuppliersData() {
                const _this = this;
                let url;
                if (this.publicData.location.current) {
                    url = '/data/input/item/mainsupplierdata/' + itemId + "/?location_id=" + this.publicData.location.current;
                } else {
                    url = '/data/input/item/mainsupplierdata/' + itemId + "/";
                }
                $.ajax({
                    url: url,
                    type: 'application/json',
                    method: 'get',
                    success: function (data) {
                        // 填充数据
                        if (data.result) {
                            _this.$refs.main.mainData = data.content;
                        } else {
                            // alert(data.message)
                        }
                    },
                    error: function (err) {
                        alert(err);
                    }
                })
            },
            //获取供应商数据
            getSuppliersData() {
                const _this = this;
                $.ajax({
                    url: '/data/input/item/suppliers/' + itemId + "/?location_id=" + this.publicData.location.current,
                    type: 'application/json',
                    method: 'get',
                    success: function (data) {
                        // 填充数据
                        if (data.result) {
                            // 保存的是数组下标
                            _this.$refs.supplier.supplierSelected = 0;
                            _this.$refs.supplier.supplierData = data.content.length ? data.content : [
                                {
                                    address: null,
                                    city: null,
                                    contact: null,
                                    cost: null,
                                    cost_unit: null,
                                    country: null,
                                    email: null,
                                    id: null,
                                    name: null,
                                    nr: null,
                                    phone: null,
                                    supplier_item_nr: null,
                                    telephone: null
                                }
                            ];
                        } else {
                            // alert(data.message)
                        }
                    },
                    error: function (err) {
                        alert(err);
                    }
                })
            },
            //获取计划数据
            getPlanData() {
                $.ajax({
                    url: '/data/input/item/plandata/' + itemId + "/",
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

                ItemDetail.getPlanGridData();
                ItemDetail.getPlanChartData();
            },
            //获取模拟数据
            getSimulationData() {
                $.ajax({
                    url: '/data/input/item/simulationdata/' + itemId + "/",
                    type: 'application/json',
                    method: 'get',
                    success: function (data) {
                        // 填充数据
                        if (data.result) {

                            FillData('item_detail_simulation', data.content);

                        } else {
                            // alert(data.message)
                        }
                    },
                    error: function (err) {
                        alert(err);
                    }
                });

                ItemDetail.getSimulationGridData();
                ItemDetail.getPlanChartData($("#simulation_chart_chooseMonth").val());
            },
            //获取预测界面grid数据
            getForecastGridData(date_type, report_type) {

                // var DateTypeValue = $("#forecast_grid_chooseMonth").val();
                $("#forecastGrid").GridDestroy();
                $("#content-main-forecast").append('<table id="forecastGrid" class="table table-striped pivotgrid"></table>');
                $("#content-main-forecast").append('<div id="forecastgridpager" class="col-md-12"></div>');
                let datetype = this.$refs.forecast ? this.$refs.forecast.forecastTableDateType : 'W';
                $.ajax({
                    url: '/data/output/forecast/item/?id=' + itemId + '&location_id=' + this.publicData.location.current + '&date_type=' + datetype + '&report_type=' + (report_type ? report_type : ''),
                    type: 'application/json',
                    method: 'get',
                    success: function (data) {
                        if (data.result) {
                            var tableColModel = [{
                                name: 'location', index: 'location', align: 'center',
                                cellattr: function (rowId, tv, rawObject, cm, rdata) {
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
                                    var everyCol = {
                                        name: forecastGridData[i].x_text,
                                        index: forecastGridData[i].x_text
                                    };
                                    tableColName.push(forecastGridData[i].x_text);
                                    tableColModel.push(everyCol);
                                    // eachRowData[forecastGridData[i].x] = forecastGridData[i].y.total;
                                    totalRowData[forecastGridData[i].x_text] = forecastGridData[i].y.total;
                                    lastRowData[forecastGridData[i].x_text] = forecastGridData[i].y.last_sale_qty;
                                    actualRowData[forecastGridData[i].x_text] = forecastGridData[i].y.actual_sale_qty;
                                    systemRowData[forecastGridData[i].x_text] = forecastGridData[i].y.system_forecast_qty;
                                    ratioRowData[forecastGridData[i].x_text] = forecastGridData[i].y.ratio;
                                    normalRowData[forecastGridData[i].x_text] = forecastGridData[i].y.normal_qty;
                                    newRowData[forecastGridData[i].x_text] = forecastGridData[i].y.new_product_plan_qty;
                                    promotionRowData[forecastGridData[i].x_text] = forecastGridData[i].y.promotion_qty;
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
                                $("#content-main-forecast").append('<table id="forecastGrid" class="table table-striped pivotgrid"></table>');

                                jQuery("#forecastGrid").jqGrid({
                                    datatype: "local",
                                    data: rowData,
                                    localReader: {
                                        repeatitems: false
                                    },
                                    colNames: tableColName,
                                    colModel: tableColModel,
                                    pager: '#forecastgridpager',
                                    emptyrecords: "无数据显示",
                                    loadtext: "卖力加载中...",
                                    shrinkToFit: false,
                                    autoScroll: true,
                                    viewrecords: true,
                                    iconSet: "fontAwesome",
                                    guiStyle: "bootstrapPrimary",
                                    hidegrid: false,
                                    resizeStop: forecastGrid.saveColumnConfiguration,
                                    scrollRows: true,
                                    autowidth: true,
                                    loadComplete: function () {
                                        $("#forecastGrid").closest(".ui-jqgrid-bdiv").css({'overflow-y': 'auto'});
                                        $(function () {
                                            $(window).resize(function () {
                                                $("#forecastGrid").setGridWidth($('#content-main-forecast').width());
                                            });
                                        });
                                    },
                                    gridComplete: function () {
                                        //在gridComplete调用合并方法
                                        ItemDetail.Merger('forecastGrid', 'location');
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
            },
            //获取预测界面chart数据
            getForecastChartData(date_type, report_type) {

                let datetype = this.$refs.forecast ? this.$refs.forecast.forecastChartDateType : 'W';

                $("#main-item_detail_forecast_chart").remove();
                $("#main-chart").append('<div id="item_detail_forecast_chart"></div>');

                $.ajax({
                    url: "/data/output/forecast/item_report/?id=" + itemId + "&location_id=" + this.publicData.location.current + "&date_type=" + datetype + "&report_type=" + (report_type ? report_type : ''),
                    type: 'application/json',
                    method: 'get',
                    success: function (data) {
                        if (data.result) {
                            const series = data.content.serials
                            // console.log('data-----------------', data);

                            var legendData = ['current_time_point'];
                            var xAxis = [];
                            var yFAxis = [];
                            var yDAxis = [];
                            var currentValue = data.content.current_time_point.x_value;
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
                                if (datetype == 'W') {
                                    xAxis.push(series[0].points[i].x_text);
                                } else {
                                    xAxis.push(series[0].points[i].x_value)
                                }
                            }
                            // console.log('---------legendData--------', legendData);
                            console.log('---------xAxis--------', xAxis);
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
                                tooltip: {},
                                legend: {
                                    data: legendData
                                },
                                xAxis: {
                                    data: xAxis,
                                    axisLabel: {
                                        formatter: function (value) {
                                            if (datetype == 'M') {
                                                let date = new Date(value);
                                                if (date.getMonth() == 0) {
                                                    return date.getFullYear() + '年' + (date.getMonth() + 1) + '月';
                                                } else {
                                                    return (date.getMonth() + 1) + '月';
                                                }
                                            } else {
                                                return value;
                                            }
                                        }
                                    }
                                },
                                yAxis: {
                                    show: false,
                                },
                                dataZoom: [
                                    {
                                        show: true,
                                        start: 0,
                                        end: 100,
                                        orient: "horizontal"
                                    },
                                    {
                                        type: 'inside',
                                        start: 0,
                                        end: 100
                                    },
                                ],
                                series: [{
                                    name: 'current_time_point',
                                    type: 'bar',
                                    data: [],
                                    markLine: {
                                        symbol: "none",
                                        lineStyle: {
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
                                }, {
                                    name: 'Dispatches(Forecast basis)',
                                    type: 'bar',
                                    data: yFAxis,
                                    // markLine: {
                                    //     symbol: "none",
                                    //     lineStyle: {
                                    //         // type: 'solid',
                                    //         // color: 'black',
                                    //         // width: '5px',
                                    //         normal: {
                                    //             type: 'solid',
                                    //             color: '#333',
                                    //             width: '10',
                                    //         }
                                    //     },
                                    //     data: [
                                    //         {
                                    //             name: '当前值',
                                    //             xAxis: currentValue
                                    //         },
                                    //     ]
                                    // }
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
            },
            //切换仓库代码时相应数据一起变化
            locationChange() {
                this.getMainData();
                this.changeTab(this.tab);
            }
        }
    });
}

