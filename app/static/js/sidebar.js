export const sidebar = document.querySelector("#sidebarNav");
const WINDOW_BREAKPOINT_LG = 992;
const WINDOW_BREAKPOINT_MD = 768;

var offcanvas;
if (sidebar) {
  offcanvas = new bootstrap.Offcanvas(sidebar);
}

export function manageSidebar() {
  window.addEventListener("beforeunload", () => {
    saveScrollPosition();
  });
  window.addEventListener("resize", () => {
    scrollToItem();
  });
  window.addEventListener("load", () => {
    scrollToItem();
  });
}

function saveScrollPosition() {
  let scrollPosition = document.getElementById("sidebar").scrollTop;
  if (scrollPosition == 0) {
    scrollPosition = document.querySelector("#sidebarNav .offcanvas-body").scrollTop;
  }
  localStorage.setItem("scrollPosition", scrollPosition);
}

function scrollToItem() {
  try {
    const fieldId = document.getElementById("field").dataset.baseId;
    var element = document.getElementById(fieldId);
    element.classList.add("active");
    const scrollPosition = localStorage.getItem("scrollPosition");
    document.getElementById("sidebar").scrollTop = scrollPosition;
    document.querySelector("#sidebarNav .offcanvas-body").scrollTop = scrollPosition;
  } catch (err) {
    document.getElementById("sidebar").scrollTop = 0;
  }
}
