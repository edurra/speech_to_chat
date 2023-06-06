    let audioIN = { audio: true };
    //  audio is true, for recording
    let is_recording = false;
    // Access the permission for use
    // the microphone

    let wait_div = document.getElementById('wait');
    wait_div.style.display = "none";

    // Start record
    let start = document.getElementById('btnStart');

    let audioSource = document.getElementById("audioPlay");
    audioSource.addEventListener("ended", function(){
     audioSource.currentTime = 0;
     start.style.display="block";
     console.log("ended audio");
    });

    navigator.mediaDevices.getUserMedia(audioIN)

      // 'then()' method returns a Promise
      .then(function (mediaStreamObj) {

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
            wait_div.style.display = "block";
            start.style.display="none";
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
            append_messages(data);
            
            
            audioSource.src = "/audio";
            wait_div.style.display = "none";
            
            })

          

        
        }
      })

      // If any error occurs then handles the error
      .catch(function (err) {
        console.log(err.name, err.message);
      });

  function append_messages(data) {
  for (let i = 0; i<data.length; i++) {
    var container = document.createElement('div');
    container.classList.add("container");
    document.getElementById('conversation').appendChild(container);

    var nodeimg = document.createElement('img');
    nodeimg.src = "/static/images/logo.jpeg";
    
    

    var node = document.createElement('span');
    node.appendChild(document.createTextNode(data[i]["content"]));
    
    node.classList.add("convtext");
    node.classList.add("alert");
    if (data[i]["role"]=="user"){
      node.classList.add("alert-success");
      nodeimg.src = "/static/images/user.png";
      nodeimg.classList.add("user");
      }
    else {
        node.classList.add("alert-info");
        nodeimg.src = "/static/images/logo.jpeg";
        nodeimg.classList.add("logo");
      };
    container.appendChild(nodeimg);
    container.appendChild(node);
  };
}