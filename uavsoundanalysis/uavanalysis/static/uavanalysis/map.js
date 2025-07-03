ymaps.ready(init);
// Инициализация Яндекс.Карты
function init() {
    var myMap = new ymaps.Map('map', {
        center: [59.47, 31.62],
        zoom: 13
    });


     // Подключение к WebSocket
    var socket = new WebSocket('ws://localhost:8000/ws/');

    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        console.log(data);
<!--        myMap.geoObjects.removeAll();-->
        // Обновляем метки на карте
        if (data.action == "connected"){
            updateMarkers(data, myMap);
        } else{
            updateMarker(data, myMap);
        }
    };

    function updateMarker(data, map) {
        // Логика обновления метки
        const placemark = map.geoObjects.get(data.id)
        if (placemark){
            placemark.options.set('iconColor', data.color);
        }
<!--        var placemark = new ymaps.Placemark([-->
<!--            data.latitude,-->
<!--            data.longitude-->
<!--        ], {-->
<!--            id: data.id,-->
<!--            hintContent: data.label-->
<!--        });-->
<!--        map.geoObjects.add(placemark);-->

    }

    function updateMarkers(data, map) {
        // Логика обновления меток
        const coordinates = data.coordinates;
        coordinates.forEach(function(coordinate) {
            var placemark = new ymaps.Placemark([
                coordinate.latitude,
                coordinate.longitude
            ], {
                id: coordinate.id,
                hintContent: coordinate.label
            });
            map.geoObjects.add(placemark);
        });
    }

};