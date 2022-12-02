// toggle sidebar
document.querySelectorAll("#sidebarNav > .list-group > a").forEach((link) => {
  link.addEventListener("click", () => {
    localStorage.removeItem("activeTab");
  });
});

document.getElementById("sidebarToggle").addEventListener("click", () => {
  toggleSidebar(this);
  activateSidebarItem();
});
// load scroll position of sidebar
window.addEventListener("load", () => {
  activateSidebarItem();
});
// save scroll position of sidebar
window.addEventListener("beforeunload", () => {
  localStorage.setItem("scrollPositon", document.getElementById("sidebar").scrollTop);
});

// scroll to selected field and add active tag
function activateSidebarItem() {
  try {
    const fieldId = document.getElementById("field").dataset.fieldId;
    var element = document.getElementById(fieldId);
    element.classList.add("active");
    document.getElementById("sidebar").scrollTop = localStorage.getItem("scrollPositon") || 0;
  } catch (err) {
    document.getElementById("sidebar").scrollTop = 0;
  }
}
// toggle sidebar in mobile mode
function toggleSidebar(toggler) {
  var sidebar = document.getElementById("sidebarNav");
  sidebar.classList.toggle("show");
  toggler.ariaExpanded = toggler.ariaExpanded == "true" ? "false" : "true";
}
