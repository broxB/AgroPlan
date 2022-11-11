// toggle sidebar
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
  localStorage.setItem("scrollPositon", document.querySelector("#sidebar").scrollTop);
});

// scroll to selected field and add active tag
function activateSidebarItem() {
  try {
    const value = JSON.parse(document.getElementById("data").textContent);
    var element = document.getElementById(value);
    element.classList.add("active");
    document.querySelector("#sidebar").scrollTop = localStorage.getItem("scrollPositon") || 0;
  } catch (err) {
    document.querySelector("#sidebar").scrollTop = 0;
  }
}
// toggle sidebar in mobile mode
function toggleSidebar(toggler) {
  var element = document.getElementById("sidebarNav");
  element.classList.toggle("show");
  toggler.ariaExpanded = toggler.ariaExpanded == "true" ? "false" : "true";
}
