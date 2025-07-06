ymaps.ready(init);
// Инициализация Яндекс.Карты
function init() {
    var myMap = new ymaps.Map('map', {
        center: [59.47, 31.62],
        zoom: 13
    });
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Define the colors to blink between
    var colors = ['red', 'black'];

    // Define the blink interval (in milliseconds)
    var blinkInterval = 500;

    var blinkIntervalIdList = [];
    var alarmElementList = [];

    // Подключение к WebSocket
    var socket = new WebSocket('ws://localhost:8000/ws/');


    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        console.log(data);
        // Обновляем метки на карте
        if (data.action == "connected"){
            updateMarkers(data, myMap);
            updatePlacemarksList(data.coordinates);
        } else{
            updateMarkerbyAlarm(data, myMap);
        }
    };

    function updatePlacemarksList(placemarks) {
        const placemarksListContainer = document.getElementById('placemarks-list');
        placemarksListContainer.innerHTML = '';
        placemarks.forEach((placemark) => {
            const placemarkHTML =
                `<div id = placemark-${placemark.id}> <span>${placemark.label}</span> <span>(${placemark.latitude}, ${placemark.longitude})</span> </div>`;
            placemarksListContainer.innerHTML += placemarkHTML;
        });
    }


    // Function to blink a placemark
    function blinkPlacemark(placemark) {
      var currentColor = placemark.options.get('iconColor');
      var nextColor = colors[(colors.indexOf(currentColor) + 1) % colors.length];
      placemark.options.set('iconColor', nextColor);
    }


    function updateMarkerbyAlarm(data, map) {
        // Логика обновления метки

        blinkIntervalIdList.length = 0;
        alarmElementList.length = 0;

        const coordinates = data.coordinates;
        console.log('updateMarkerbyAlarm');
        coordinates.forEach(function(coordinate) {
            console.log(coordinate.id);
            const placemark = map.geoObjects.get(coordinate.id - 1)
            if (placemark){
//                placemark.options.set('iconColor', data.color);
               blinkIntervalId = setInterval(function() {
                  blinkPlacemark(placemark);
                }, blinkInterval);
               blinkIntervalIdList.push(blinkIntervalId);
            } else{
                console.log(`placemark-${coordinate.id} not found`);
            }

            var element = document.getElementById(`placemark-${coordinate.id}`)
            element.style.backgroundColor = data.color;
            alarmElementList.push(element);
            console.log(element);
        })

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
            placemark.options.set('iconColor', 'black');
            map.geoObjects.add(placemark);
        });
    }



    // Add event listeners to the buttons to send notifications to the WebSocket
    document.getElementById('clear-alarm-button').addEventListener('click', function() {
        // Send notification to WebSocket
        console.log('Clear alarm button clicked');

        // Clear the interval
        blinkIntervalIdList.forEach(function(blinkId) {
            clearInterval(blinkId);
        });

         // Disable blinking for all placemarks
        myMap.geoObjects.each(function(placemark) {
          id = placemark.properties.get('id');
          placemark.options.set('iconColor', 'black'); // reset icon color to default
        });

        alarmElementList.forEach(function(element) {
            element.style.backgroundColor = '';
        })

    });

    document.getElementById('test-alarm-button').addEventListener('click', function() {
        // Send notification to WebSocket
        console.log('Test alarm button clicked');

        var placemarkJson = [];

        myMap.geoObjects.each(function(placemark) {
            placemarkJson.push({
                id: placemark.properties.get('id'),
                latitude: placemark.geometry.getCoordinates()[0],
                longitude: placemark.geometry.getCoordinates()[1]
            });
        });

        console.log(placemarkJson);

        fetch('/test_alarm',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            mode: 'same-origin',
            body: JSON.stringify({'placemarks': placemarkJson})
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    });

};