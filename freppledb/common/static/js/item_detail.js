var ItemDetail = {}
var itemId = 0
var




ItemDetail.getMainData = function () {
    $.ajax({
        url: '/data/input/item/maindata/'
    })
};
