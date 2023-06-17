import { fetchData, sendForm } from "./request.js";

class Modal {
  static #instance;

  constructor() {
    let modal = document.querySelector("#modal");
    this.content = modal.querySelector(".modal-content");
    modal.addEventListener("hidden.bs.modal", () => {
      this.content.innerHTML = "";
    });
  }

  async initialContent(event) {
    const e = event.relatedTarget;
    const fieldId = document.getElementById("field").dataset.fieldId;
    const params = {
      modalType: e.dataset.modal,
      formType: e.dataset.form,
      id: e.dataset.id,
      fieldId: fieldId,
    };
    const modalURL = "/modal?" + new URLSearchParams(params).toString();
    console.log(modalURL);
    const content = await fetchData(modalURL);
    this.addContent(content);
  }

  addEventListeners() {
    let selectElements = this.content.querySelectorAll("select");
    selectElements.forEach((select) => {
      if (select.classList.contains("reload")) {
        select.addEventListener("change", async () => {
          const content = await sendForm(this.form, "POST", "/modal/specifics");
          this.addContent(content);
        });
      }
    });
  }

  addContent(content) {
    this.content.innerHTML = content;
    this.form = modal.querySelector("#modalForm");
    this.addEventListeners();
  }
}

export function createModal(event) {
  let modal = new Modal();
  modal.initialContent(event);
}
