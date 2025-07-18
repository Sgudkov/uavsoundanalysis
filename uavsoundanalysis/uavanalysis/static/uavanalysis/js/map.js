import  { startAudioStreaming, stopAudioStreaming }  from './audio.js';

ymaps.ready(init);
// Initialize the map
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

    var placemarkJson = [];

    // Connect to the WebSocket
    var socket = new WebSocket('ws://'+ window.location.host + '/ws/');
    var socket_audio = null;

    // Event listener for messages received from the WebSocket
    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);

        // Initialize the markers or update the markers
        if (data.action == "connected"){
            initMarkers(data, myMap);
        } else{
            updateMarkerbyAlarm(data, myMap);
        }
    };

    // Function to blink a placemark
    function blinkPlacemark(placemark) {
      var currentColor = placemark.options.get('iconColor');
      var nextColor = colors[(colors.indexOf(currentColor) + 1) % colors.length];
      placemark.options.set('iconColor', nextColor);
    }

    // Update the markers based on the alarm data
    function updateMarkerbyAlarm(data, map) {

        blinkIntervalIdList.length = 0;
        alarmElementList.length = 0;

        const coordinates = data.coordinates;
        console.log('updateMarkerbyAlarm');
        coordinates.forEach(function(coordinate) {

            const placemark = map.geoObjects.get(coordinate.id - 1)
            if (placemark){
              // Blink the placemark
              var blinkIntervalId = setInterval(function() {
                  blinkPlacemark(placemark);
                }, blinkInterval);
               blinkIntervalIdList.push(blinkIntervalId);
            } else{
                console.log(`placemark-${coordinate.id} not found`);
            }

            var element = document.getElementById(`placemark-${coordinate.id}`)
            element.style.backgroundColor = data.color;
            alarmElementList.push(element);
        })

    }

    // Initialize the markers
    function initMarkers(data, map) {

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

            placemark.events.add('click', function(e) {
                var placemarkId = e.get('target').properties.get('id');
                console.log(`Placemark ${placemarkId} clicked!`);
            });

            // Collect initialized placemark data
            placemarkJson.push({
                id: coordinate.id,
                latitude: coordinate.latitude,
                longitude: coordinate.longitude
            });

        });
    }

    let startWorkButtonPressed = false;

    // Event listener for the toogle start work button
    document.getElementById('start-work-button').addEventListener('click', function() {

        this.classList.toggle('clicked');

        // Start or stop audio streaming
        if (!startWorkButtonPressed) {
            startAudioStreaming(placemarkJson);
            startWorkButtonPressed = true;
        } else {
            stopAudioStreaming();
            startWorkButtonPressed = false;
        }

        console.log('Start work button clicked');

    });

    // Stop alarm and blink the placemarks without sending data to the server
    document.getElementById('clear-alarm-button').addEventListener('click', function() {

        console.log('Clear alarm button clicked');

        // Clear the interval
        blinkIntervalIdList.forEach(function(blinkId) {
            clearInterval(blinkId);
        });

         // Disable blinking for all placemarks
        myMap.geoObjects.each(function(placemark) {
          placemark.options.set('iconColor', 'black'); // reset icon color to default
        });

        alarmElementList.forEach(function(element) {
            element.style.backgroundColor = '';
        })

    });

    // Send alarm to WebSocket
    document.getElementById('test-alarm-button').addEventListener('click', function() {
        // Send notification to WebSocket
        console.log('Test alarm button clicked');


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