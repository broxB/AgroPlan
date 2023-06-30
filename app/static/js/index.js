import { createModal } from "./modal.js";
import { manageToast } from "./toast.js";
import { fieldSaldo, restoreTab, storeTab } from "./field.js";
import { manageSidebar } from "./sidebar.js";
import { manageFields } from "./fields.js";

// Control modal
window.addEventListener("show.bs.modal", (event) => createModal(event));

// Control toasts
window.addEventListener("load", manageToast());

// Control /field/ scripts
if (window.location.pathname.includes("/field/")) {
  window.addEventListener("load", () => {
    fieldSaldo();
    restoreTab();
    storeTab();
  });
}

// Control /fields/ scripts
if (window.location.pathname.includes("/fields/")) {
  // manageFields();
}

// Control sidebar
if (document.querySelector("#sidebarNav")) {
  manageSidebar();
}
