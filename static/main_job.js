    import { append_messages, config_mediarecorder, update_tokens}  from './funcs.js';
    let audioIN = { audio: true };
    //  audio is true, for recording
    let is_recording = false;
    // Access the permission for use
    // the microphone

    let wait_div = document.getElementById('wait');
    wait_div.style.display = "none";

    // Start record
    let start = document.getElementById('btnStart');

    let audioSource = document.getElementById("audioPlayRnd");
    audioSource.addEventListener("ended", function(){
     audioSource.currentTime = 0;
     start.style.display="block";
     console.log("ended audio");
    });


    let job_div = document.getElementById("jobdiv");
    let job_button = document.getElementById("jobbnt");
    let job_text = document.getElementById("inputJob");

    job_button.addEventListener('click', function (ev) {
        job_div.style.display="none";
        wait_div.style.display = "block";

        let data = {
            "job_position": job_text.value     
        };
        fetch("/job_interview_init", {
        method: "POST",
        cache: "no-cache",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data),
      }).then(resp => resp.json()).then(data=>{ 

        console.log(data)
        
        audioSource.src = "/audio_job";
        audioSource.play();
        append_messages(data);

        wait_div.style.display = "none";
        
        
        });
    });
    

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
          fetch("/job_interview", {
            method: "POST",
            cache: "no-cache",
            body: formData
          }).then(resp => resp.json()).then(data=>{ 

            //conversation = document.getElementById("conversation");
            console.log(data)
            append_messages(data);
            
            audioSource.src = "/audio_random";
            audioSource.play();
            wait_div.style.display = "none";
            
            })

        }
      })

      // If any error occurs then handles the error
      .catch(function (err) {
        console.log(err.name, err.message);
      });

