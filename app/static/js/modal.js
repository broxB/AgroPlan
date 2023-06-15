import { fetchData, sendForm } from "./request.js";

export class Modal {
  static #instance;

  constructor() {
    let modal = document.querySelector("#modal");
    this.content = modal.querySelector(".modal-content");
    modal.addEventListener("hidden.bs.modal", () => {
      this.content.innerHTML = "";
    });
  }

  async fetchContent(event) {
    const e = event.relatedTarget;
    const modalType = e.dataset.modal;
    const formType = e.dataset.form;
    const id = e.dataset.id;
    const fieldId = document.getElementById("field").dataset.fieldId;
    const params = { modal: modalType, form: formType, id: id, fieldId: fieldId };
    const modalURL = "/modal?" + new URLSearchParams(params).toString();
    console.log(modalURL);
    const content = await fetchData(modalURL);
    this.addContent(content);
  }

  addEventListeners() {
    let selectElements = this.content.querySelectorAll("select");
    selectElements.forEach((select) => {
      select.addEventListener("change", async () => {
        const content = await sendForm(this.form, "POST", "/modal/specifics");
        this.addContent(content);
      });
    });
  }

  addContent(content) {
    this.content.innerHTML = content;
    this.form = modal.querySelector("#modalForm");
    this.addEventListeners();
  }
}

window.addEventListener("show.bs.modal", (event) => {
  let modal = new Modal();
  modal.fetchContent(event);
});
