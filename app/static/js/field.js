function edit(element) {
  var tr = element.parentElement.parentElement;
  if (!tr.classList.contains("editing")) {
    tr.classList.toggle("editing");
    var td = tr.getElementsByClassName("form-td");
    for (let elem of td) {
      if (!elem.classList.contains("action")) {
        var value = elem.textContent;
        elem.textContent = "";
        var input = createElement("input", value);
        elem.appendChild(input);
      } else {
        // elem.querySelector("I").classList = "fa-solid fa-square-check";
        // elem.querySelector("I").classList = "fa-solid fa-pen-to-square";
        toggleButtons(elem);
      }
    }
  }
}

function save(element) {
  var tr = element.parentElement.parentElement;
  tr.classList.toggle("editing");
  var td = tr.getElementsByClassName("form-td");
  for (let elem of td) {
    if (!elem.classList.contains("action")) {
      var input = elem.querySelector("INPUT");
      elem.textContent = input.value;
    } else {
      toggleButtons(elem);
    }
  }
}

function cancel(element) {
  var tr = element.parentElement.parentElement;
  tr.classList.toggle("editing");
  var td = tr.getElementsByClassName("form-td");
  for (let elem of td) {
    if (!elem.classList.contains("action")) {
      var input = elem.querySelector("INPUT");
      elem.textContent = input.getAttribute("fallback");
    } else {
      toggleButtons(elem);
    }
  }
}

function createElement(type, value) {
  var input = document.createElement(type);
  input.type = "text";
  input.setAttribute("value", value);
  input.setAttribute("fallback", value);
  return input;
}

function toggleButtons(elem) {
  elem.querySelectorAll("BUTTON").forEach((btn) => {
    btn.classList.toggle("visually-hidden");
  });
}
