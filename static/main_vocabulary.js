    import { append_messages, config_mediarecorder, update_tokens } from './funcs.js';
    let audioIN = { audio: true };
    //  audio is true, for recording
    let is_recording = false;
    // Access the permission for use
    // the microphone

    let wait_div = document.getElementById('wait');
    wait_div.style.display = "block";

    // Start record
    let start = document.getElementById('btnStart');
    let btn_new = document.getElementById('btnNew');

    let audioSource = document.getElementById("audioPlay");
    audioSource.addEventListener("ended", function(){
     audioSource.currentTime = 0;
     start.style.display="block";
     console.log("ended audio");
    });

    fetch("/vocabulary_word", {
        method: "POST",
        cache: "no-cache"
      }).then(resp => resp.json()).then(data=>{ 

        console.log(data);
        audioSource.src = "/audio_vocabulary";
        audioSource.play();
        append_messages(data);

        wait_div.style.display = "none";
        start.style.display="block";
        
        });

    btn_new.onclick = function() {
      btn_new.style.display="none";
      wait_div.style.display = "block";
      fetch("/vocabulary_word", {
        method: "POST",
        cache: "no-cache"
      }).then(resp => resp.json()).then(data=>{ 

        console.log(data);
        audioSource.src = "/audio_vocabulary";
        audioSource.play();
        append_messages(data);

        wait_div.style.display = "none";
        start.style.display="block";
        
        });
    };

    navigator.mediaDevices.getUserMedia(audioIN)

      // 'then()' method returns a Promise
      .then(function (mediaStreamObj) {

        let mediaRecorder = new MediaRecorder(mediaStreamObj);
        config_mediarecorder(start, mediaRecorder, wait_div, is_recording);


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
          fetch("/vocabulary_feedback", {
            method: "POST",
            cache: "no-cache",
            body: formData
          }).then(resp => resp.json()).then(data=>{ 

            //conversation = document.getElementById("conversation");
            console.log(data)
            append_messages(data);
            //audioSource.src = "/audio_vocabulary";
            wait_div.style.display = "none";
            btn_new.style.display="block";
            
            });

        
        }
      })

      // If any error occurs then handles the error
      .catch(function (err) {
        console.log(err.name, err.message);
      });

