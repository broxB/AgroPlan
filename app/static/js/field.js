// restore selected tab on reload
window.addEventListener("load", () => {
  var id = localStorage.getItem("activeTab");
  if (id) {
    var elem = document.querySelector(`${id}-tab`);
    var tab = new bootstrap.Tab(elem);
    tab.show();
  } else {
    var elem = document.querySelector("#field-nav > button");
    var tab = new bootstrap.Tab(elem);
    tab.show();
  }
});

// save tab selection on click
document.querySelectorAll("#field-nav > button").forEach((btn) => {
  btn.addEventListener("shown.bs.tab", () => {
    var id = btn.dataset["bsTarget"];
    localStorage.setItem("activeTab", id);
  });
});

// global for original values
var fallback = [];

function edit(element) {
  var tr = element.parentElement.parentElement;
  if (!tr.classList.contains("editing")) {
    tr.classList.toggle("editing");
    var td = tr.getElementsByTagName("td");
    for (let elem of td) {
      if (!elem.classList.contains("action")) {
        const value = elem.textContent.trim();
        elem.textContent = "";
        const elemType = elem.classList[0];
        const input = createElement(elemType, value);
        elem.appendChild(input);
      } else {
        toggleButtons(elem);
      }
    }
  }
}

function save(element) {
  var tr = element.parentElement.parentElement;
  tr.classList.toggle("editing");
  var td = tr.getElementsByTagName("td");
  for (let elem of td) {
    if (!elem.classList.contains("action")) {
      elem.textContent = newValue(elem);
    } else {
      toggleButtons(elem);
    }
  }
  fallback = [];
}

function cancel(element) {
  var tr = element.parentElement.parentElement;
  tr.classList.toggle("editing");
  var td = tr.getElementsByTagName("td");
  for (let elem of td) {
    if (!elem.classList.contains("action")) {
      elem.textContent = fallback.shift();
    } else {
      toggleButtons(elem);
    }
  }
  fallback = [];
}

function createElement(type, value) {
  var input = document.createElement(type);
  if (type == "input") {
    input.type = "text";
    input.classList.add("form-control");
    input.setAttribute("value", value);
  } else if (type == "select") {
    const option = document.createElement("option");
    option.value = input.length + 1; // sets invisible id
    option.text = value; // sets displayed text
    input.add(option, input.length + 1);
    input.classList.add("form-select");
  }
  fallback.push(value);
  return input;
}

function newValue(elem) {
  var inputClass = elem.classList[0];
  if (inputClass == "input") {
    return elem.querySelector("INPUT").value;
  } else if (inputClass == "select") {
    const select = elem.querySelector("SELECT");
    const text = select.options[select.selectedIndex].text;
    return text;
  }
}

function toggleButtons(elem) {
  elem.querySelectorAll("BUTTON").forEach((btn) => {
    btn.classList.toggle("visually-hidden");
  });
}
