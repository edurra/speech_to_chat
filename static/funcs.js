export {append_messages, config_mediarecorder};

function append_messages(data) {
  for (let i = 0; i<data.length; i++) {
    var container = document.createElement('div');
    container.classList.add("containerconv");
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

function config_mediarecorder(start, mediaRecorder, wait_div, is_recording) {
  
  // Pass the audio stream

  // Start event
  start.addEventListener('click', function (ev) {
    if (is_recording == false) {
      mediaRecorder.start();
      console.log("start");
      is_recording = true;
      start.innerHTML = "stop recording";
      start.classList.remove("btn-success");
      start.classList.add("btn-warning");
    }
    else {
      mediaRecorder.stop();
      console.log("stop");
      is_recording = false;
      start.innerHTML = "start recording";
      wait_div.style.display = "block";
      start.style.display="none";
      start.classList.remove("btn-warning");
      start.classList.add("btn-success");
    }
    
    // console.log(mediaRecorder.state);
  });
}