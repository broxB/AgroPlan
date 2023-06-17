// remove stored selected tab on page change
export function removeStoredTab() {
  localStorage.removeItem("activeTab");
}

// restore selected tab on reload
export function restoreTab() {
  var id = localStorage.getItem("activeTab");
  if (id) {
    var elem = document.querySelector(`${id}-tab`);
  } else {
    var elem = document.querySelector("#field-nav > button");
  }
  var tab = new bootstrap.Tab(elem);
  tab.show();
}

// save selected tab on click
export function storeTab() {
  document.querySelectorAll("#field-nav > button").forEach((btn) => {
    btn.addEventListener("shown.bs.tab", () => {
      var id = btn.dataset["bsTarget"];
      localStorage.setItem("activeTab", id);
    });
  });
}

/**
 * request: field footer saldo
 */
export async function fieldSaldo() {
  const fieldId = document.getElementById("field").dataset.baseId;
  // const room_url = "{{ url_for('main.field_data', id=base_field.id) }}";
  const room_url = "/field/" + fieldId + "/data";
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
