export {append_messages, config_mediarecorder, update_tokens};

$(function () {
  $('[data-toggle="popover"]').popover()
})

function append_messages(data) {
  $('[data-toggle="popover"]').popover('hide');
  for (let i = 0; i<data["messages"].length; i++) {
    var container = document.createElement('div');
    container.classList.add("containerconv");
    document.getElementById('conversation').appendChild(container);

    var nodeimg = document.createElement('img');
    nodeimg.src = "/static/images/logo.jpeg";
    
    

    var node = document.createElement('span');
    node.appendChild(document.createTextNode(data["messages"][i]["content"]));
    
    node.classList.add("convtext");
    node.classList.add("alert");
    if (data["messages"][i]["role"]=="user"){
      node.classList.add("alert-success");
      nodeimg.src = "/static/images/user.png";
      nodeimg.classList.add("user");

      var sug_div = document.createElement("div");
      var sug = document.createElement('span');
      sug.setAttribute("data-toggle", "popover");
      sug.setAttribute("data-content", data["suggestion"]);
      sug.setAttribute("data-placement", "left");
      sug.classList.add("sug_span");
      sug.innerText = "suggestion";
      let sug_id = Math.floor(Math.random() * 10000000).toString();
      sug.id = sug_id;
      sug_div.appendChild(sug);
      container.appendChild(sug_div);
      $('#'+sug_id).popover("show");

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

function update_tokens() {
  fetch("/n_tokens", {
              method: "GET",
              cache: "no-cache"
            }).then(resp => resp.json()).then(data=>{ 

              // conversation = document.getElementById("conversation");
              console.log(data)
              let tokens_a = document.getElementById("ntokens");
              tokens_a.innerText = data["tokens"];
              
              })
}