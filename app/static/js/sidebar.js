const sidebar = document.querySelector("#sidebarNav");
const offcanvas = new bootstrap.Offcanvas(sidebar);

export function manageSidebar() {
  window.addEventListener("show.bs.offcanvas", () => {
    // scroll to item pos on canvas open
    scrollToItem();
    // close offcanvas on window breakpoint and scroll to item pos
    window.addEventListener("resize", hideOnResize);
  });
  window.addEventListener("load", () => {
    scrollToItem();
  });
}

function hideOnResize() {
  const WINDOW_BREAKPOINT_LG = 992;
  const WINDOW_BREAKPOINT_MD = 768;
  if (window.innerWidth >= WINDOW_BREAKPOINT_MD) {
    offcanvas.hide();
    scrollToItem();
    window.removeEventListener("resize", hideOnResize);
  }
}

function scrollToItem() {
  try {
    const fieldId = document.getElementById("field").dataset.baseId;
    var element = document.getElementById(fieldId);
    element.classList.add("active");
    element.scrollIntoView();
  } catch (err) {
    document.getElementById("sidebar").scrollTop = 0;
  }
}

function toggleSidebar(event) {
  let toggle = event.currentTarget;
  var sidebar = document.getElementById("sidebarNav");
  sidebar.classList.toggle("show");
  toggle.ariaExpanded = toggle.ariaExpanded == "true" ? "false" : "true";
}
