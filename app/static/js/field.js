import { fetchData } from "./request.js";
import { sidebar } from "./sidebar.js";

// restore field nav tab on reload
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

// remove stored selected tab on page change
export function removeStoredTab() {
  if (sidebar) {
    const links = sidebar.querySelectorAll("a");
    links.forEach((link) => {
      link.addEventListener("click", () => {
        localStorage.removeItem("activeTab");
      });
    });
  }
}

// save field nav tab on click
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
  const room_url = "/field/" + fieldId + "/data";
  const data = await fetchData(room_url);
  for (let elem in data) {
    var element = document.getElementById(elem);
    if (element) {
      var value = Number(data[elem]).toFixed(0).replace("-0", "0");
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
