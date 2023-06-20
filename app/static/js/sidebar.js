export function manageSidebar() {
  // toggle sidebar and load scroll pos
  document.getElementById("sidebarToggle").addEventListener("click", (event) => {
    // toggleSidebar(event);
    activateSidebarItem();
  });
  // get sidebar scroll pos on page load
  window.addEventListener("load", () => {
    activateSidebarItem();
  });
}

// scroll element pos and add active tag
function activateSidebarItem() {
  try {
    const fieldId = document.getElementById("field").dataset.baseId;
    var element = document.getElementById(fieldId);
    element.classList.add("active");
    element.scrollIntoView();
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
