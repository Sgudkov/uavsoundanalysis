//// Add event listeners to the buttons to send notifications to the WebSocket
//document.getElementById('clear-alarm-button').addEventListener('click', function() {
//    // Send notification to WebSocket
//    // Replace with your WebSocket code
//    console.log('Clear alarm button clicked');
//});
//
//document.getElementById('test-alarm-button').addEventListener('click', function() {
//    // Send notification to WebSocket
//    // Replace with your WebSocket code
//    console.log('Test alarm button clicked');
//    var placemarks = myMap.geoObjects.get();
//    console.log(placemarks);
//    console.log(placemarksListContainer);
//    fetch('/test_alarm',{
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/json'
//        },
//        body: JSON.stringify({})
//    })
//    .then(response => response.json())
//    .then(data => console.log(data))
//    .catch(error => console.error(error));
//});
