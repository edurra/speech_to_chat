export {append_messages};

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