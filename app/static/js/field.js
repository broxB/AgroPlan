// restore selected tab on reload
window.addEventListener("load", () => {
  var id = localStorage.getItem("activeTab");
  if (id) {
    var elem = document.querySelector(`${id}-tab`);
  } else {
    var elem = document.querySelector("#field-nav > button");
  }
  var tab = new bootstrap.Tab(elem);
  tab.show();
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

//
function edit(element) {
  var tr = element.parentElement.parentElement;
  if (!tr.classList.contains("editing")) {
    fallback = [];
    tr.classList.toggle("editing");
    var td = tr.getElementsByTagName("td");
    for (let elem of td) {
      if (!elem.classList.contains("action")) {
        const value = elem.textContent.trim();
        fallback.push(value);
        elem.textContent = "";
        const input = createInput(elem, value);
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
      elem.textContent = getNewValue(elem);
    } else {
      toggleButtons(elem);
    }
  }
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
}

function createInput(elem, value) {
  var type = getElementType(elem);
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
  input.style.minWidth = value.length + 6 + "ch"; // adjust size to value length
  return input;
}

function getNewValue(elem) {
  var type = elem.firstChild.tagName;
  if (type == "INPUT") {
    var value = elem.querySelector(type).value;
  } else if (type == "SELECT") {
    const select = elem.querySelector(type);
    var value = select.options[select.selectedIndex].text;
  }
  return value;
}

function getElementType(td) {
  // https://stackoverflow.com/a/37312707/16256581
  const index = Array.prototype.indexOf.call(td.parentNode.children, td);
  const corresponding_th = td.closest("table").querySelector("th:nth-child(" + (index + 1) + ")");
  return corresponding_th.classList[0];

  // https://stackoverflow.com/a/46139306/16256581 for col-span support
  /*
  var idx = [...td.parentNode.children].indexOf(td), // get td index
      thCells = td.closest('table').tHead.rows[0].cells, // get all th cells
      th_colSpan_acc = 0 // accumulator
  // iterate all th cells and add-up their colSpan value
  for( var i=0; i < thCells.length; i++ ){
     th_colSpan_acc += thCells[i].colSpan
     if( th_colSpan_acc >= (idx + td.colSpan) ) {
      break
    }
  }
  return thCells[i].classList[0]
  */
}

function toggleButtons(elem) {
  elem.querySelectorAll("BUTTON").forEach((btn) => {
    btn.classList.toggle("visually-hidden");
  });
}

// request: field footer saldo
window.addEventListener("load", fetchSaldo());
async function fetchSaldo() {
  const field = document.getElementById("field").dataset.baseId;
  // const room_url = "{{ url_for('main.field_data', id=base_field.id) }}";
  const room_url = "/field/" + field + "/data";
  const data = await fetch(room_url).then((response) => response.json());
  for (let elem in data) {
    var element = document.getElementById(elem);
    if (element) {
      var value = Number(data[elem]).toFixed(0);
      element.textContent = value;
      if (value > 0) {
        element.classList.add("text-danger");
      } else if (value < 0) {
        element.classList.add("text-primary");
      } else {
        element.classList.add("text-success");
      }
    }
  }
}
