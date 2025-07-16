var mediaRecorder, socket_audio;
export async function startAudioStreaming(placemarkJson) {
    try {

         // Request access to microphone
         const stream = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: 48000, channelCount: 2, sampleSize: 16, frameRate: 30 } });

         // Check if browser supports MediaRecorder
         if (!MediaRecorder.isTypeSupported('audio/webm')) {
             alert('Browser not supported for MediaRecorder');
             return;
         }

         // Create a MediaRecorder instance
          mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm',
            audioBitsPerSecond: 320000,
            bitrate: 320000
          });

         // Connect to WebSocket server
         socket_audio = new WebSocket('ws://' + window.location.host + '/ws/audio'); // Replace with your WebSocket server URL

         socket_audio.onopen = () => {
             console.log('WebSocket connection established.');

             // Send audio data in chunks
             mediaRecorder.addEventListener('dataavailable', async (event) => {
                 if (event.data.size > 0 && socket_audio.readyState === WebSocket.OPEN) {

                    const audioData = event.data;
                    const arrayBuffer = await audioData.arrayBuffer();
                    const uint8Array = new Uint8Array(arrayBuffer);

                    // Encode the Uint8Array as a Base64 encoded string
                    const base64EncodedData = btoa(String.fromCharCode(...uint8Array));

                    // Create the JavaScript object with the binary string
                    const dataToSend = {
                        messageType: 'binary_payload',
                        data: base64EncodedData,
                        placemarks: placemarkJson,
                        timestamp: Date.now()
                    };
                     // Convert the object to a JSON string
                     const jsonString = JSON.stringify(dataToSend);

                     console.log(jsonString);
                     socket_audio.send(jsonString); // Send the audio chunk
                 }
             });

             // Start recording and sending data every second
             mediaRecorder.start(2000); // Send data every 2000ms (2 seconds)
         };


        socket_audio.onmessage = (event) => {
            console.log('Received message from server:', event.data);
            // Handle incoming messages from the server, e.g., for two-way communication
        };

        socket_audio.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        socket_audio.onclose = () => {
            console.log('WebSocket connection closed.');
            mediaRecorder.stop();
        };


    } catch (err) {
        console.error('Error accessing microphone:', err);
    }
}

export async function stopAudioStreaming() {
    if (socket_audio) {
        socket_audio.close();
    }
 }
