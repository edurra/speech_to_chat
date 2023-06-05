    let audioIN = { audio: true };
    //  audio is true, for recording
    let is_recording = false;
    // Access the permission for use
    // the microphone
    navigator.mediaDevices.getUserMedia(audioIN)

      // 'then()' method returns a Promise
      .then(function (mediaStreamObj) {



        // Start record
        let start = document.getElementById('btnStart');


        let mediaRecorder = new MediaRecorder(mediaStreamObj);
        // Pass the audio stream

        // Start event
        start.addEventListener('click', function (ev) {
          if (is_recording == false) {
            mediaRecorder.start();
            console.log("start");
            is_recording = true;
            start.innerHTML = "stop recording";
          }
          else {
            mediaRecorder.stop();
            console.log("stop");
            is_recording = false;
            start.innerHTML = "start recording";
          }
          
          // console.log(mediaRecorder.state);
        })



        // If audio data available then push
        // it to the chunk array
                // Chunk array to store the audio data
        let dataArray = [];

        mediaRecorder.ondataavailable = function (ev) {
          dataArray.push(ev.data);
          console.log("dataArray push");
          //console.log(dataArray);
        }

        // Convert the audio data in to blob
        // after stopping the recording
        mediaRecorder.onstop = function (ev) {

          // blob of type mp3
          let audioData = new Blob(dataArray,
                    { 'type': 'audio/mp3;' });
          console.log(audioData);

          // After fill up the chunk
          // array make it empty
          dataArray = [];

          // Creating audio url with reference
          // of created blob named 'audioData'
          let audioSrc = window.URL
              .createObjectURL(audioData);

          // Pass the audio url to the 2nd video tag
          

          let formData = new FormData();
          formData.append("audio_file", audioData);

          // Send the form data to the server.
          fetch("/chat", {
            method: "POST",
            cache: "no-cache",
            body: formData
          }).then(resp => resp.json()).then(data=>{ 

            conversation = document.getElementById("conversation");
            console.log(data)
            for (let i = 0; i<data.length; i++) {
                
              var node = document.createElement('li');
              node.appendChild(document.createTextNode(data[i]["role"] + ": " + data[i]["content"]));
              document.querySelector('ul').appendChild(node);
              node.classList.add("convtext");
                
              };
            var audioSource = document.getElementById("audioPlay");
            audioSource.src = "/audio";
            })

          

        
        }
      })

      // If any error occurs then handles the error
      .catch(function (err) {
        console.log(err.name, err.message);
      });