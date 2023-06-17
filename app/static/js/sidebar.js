import { removeStoredTab } from "./field.js";

export function manageSidebar() {
  // remove stored nav tab selection
  document.querySelectorAll("#sidebarNav > .list-group > a").forEach((link) => {
    link.addEventListener("click", removeStoredTab());
  });

  // toggle sidebar and load scroll pos
  document.getElementById("sidebarToggle").addEventListener("click", (event) => {
    toggleSidebar(event);
    activateSidebarItem();
  });
  // get sidebar scroll pos on page load
  window.addEventListener("load", () => {
    activateSidebarItem();
  });
  // save scroll pos on going to new page
  window.addEventListener("beforeunload", () => {
    localStorage.setItem("scrollPositon", document.getElementById("sidebar").scrollTop);
  });
}

// load scroll pos and add active tag to field entry
function activateSidebarItem() {
  try {
    const fieldId = document.getElementById("field").dataset.baseId;
    var element = document.getElementById(fieldId);
    element.classList.add("active");
    document.getElementById("sidebar").scrollTop = localStorage.getItem("scrollPositon") || 0;
  } catch (err) {
    document.getElementById("sidebar").scrollTop = 0;
  }
}
// toggle sidebar in mobile mode
function toggleSidebar(event) {
  let toggle = event.currentTarget;
  var sidebar = document.getElementById("sidebarNav");
  sidebar.classList.toggle("show");
  toggle.ariaExpanded = toggle.ariaExpanded == "true" ? "false" : "true";
}
