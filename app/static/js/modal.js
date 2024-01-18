import { fetchData, sendForm } from "./request.js";

export function createModal(event) {
  new Modal(event);
}

class Modal {
  constructor(event) {
    const modal = document.querySelector("#modal");
    this.content = modal.querySelector(".modal-content");
    modal.addEventListener("hidden.bs.modal", () => {
      this.content.innerHTML = "";
    });
    this.initialContent(event);
  }

  async initialContent(event) {
    const e = event.relatedTarget;
    this.modal_type = e.dataset.modal;
    const params = {
      modal: this.modal_type,
      form: e.dataset.form,
      id: e.dataset.id,
    };
    const modalURL = "/modal?" + new URLSearchParams(params).toString();
    console.log(modalURL);
    const content = await fetchData(modalURL);
    this.addContent(content);
  }

  addContent(content, defaults = true) {
    this.content.innerHTML = content;
    this.form = this.content.querySelector("#modalForm");
    if (this.modal_type === "new" && defaults) {
      this.setDefaults();
    } else {
      // neccessary to delete entries when form validation fails, e.g. missing data.
      this.form.setAttribute("novalidate", "");
    }
    this.addEventListeners();
  }

  setDefaults() {
    const selectElements = this.content.querySelectorAll("select");
    selectElements.forEach((select) => {
      if (select.attributes.getNamedItem("selected")) {
        return;
      }
      let selectDefault = new Option("");
      selectDefault.setAttribute("hidden", "");
      selectDefault.setAttribute("selected", "");
      selectDefault.setAttribute("disabled", "");
      select.add(selectDefault, select.options[0]);
    });
  }

  addEventListeners() {
    const formControls = this.content.querySelectorAll("select, input");
    formControls.forEach((control) => {
      if (control.classList.contains("reload")) {
        control.addEventListener("change", async () => {
          const content = await sendForm(this.form, "POST", "/modal/refresh");
          this.addContent(content);
        });
      } else {
        if (control.tagName === "SELECT") {
          control.addEventListener("change", () => {
            this.content.querySelector(".btn-success").removeAttribute("hidden");
          });
        } else {
          control.addEventListener("keydown", () => {
            this.content.querySelector(".btn-success").removeAttribute("hidden");
          });
        }
      }
    });
    try {
      this.form.addEventListener("submit", (event) => {
        event.preventDefault();
        const btn = event.submitter.textContent;
        if (btn != "Delete" && !this.form.checkValidity()) {
          this.form.reportValidity();
        } else {
          if (btn === "Save") {
            this.editData();
          } else if (btn === "Create") {
            this.newData();
          } else if (btn === "Delete") {
            this.deleteData();
          }
        }
        console.log(event);
      });
      this.form.addEventListener("keydown", (event) => {
        if (event.keyCode != 13) {
          return;
        }
        event.preventDefault();
        if (this.modal_type === "new") {
          this.newData();
        } else if (this.modal_type === "edit") {
          this.editData();
        }
      });
    } catch (error) {
      console.log(error);
    }
  }

  async newData() {
    console.log("new");
    let response = await sendForm(this.form, "POST", "/modal/submit", true);
    this.handleResponse(response);
  }

  async editData() {
    console.log("update");
    let response = await sendForm(this.form, "PUT", "/modal/submit", true);
    this.handleResponse(response);
  }

  async deleteData() {
    console.log("delete");
    let response = await sendForm(this.form, "DELETE", "/modal/submit", true);
    this.handleResponse(response);
  }

  async handleResponse(response) {
    if (response.status == 201) {
      // success
      response.json().then((data) => {
        this.clearErrors();
        this.content.querySelector(".modal-footer").innerHTML = `
        <ul class="ps-0 me-auto">
        <h6 class="">${data}</h6></ul>
        <ul><button type="button" class="btn btn-secondary ms-1" data-bs-dismiss="modal">Close</button></ul>`;
        for (let control of this.form) {
          control.setAttribute("disabled", "");
        }
        document.addEventListener("hidden.bs.modal", () => {
          window.location.reload();
        });
      });
    } else if (response.status == 206) {
      // changed content
      response.json().then((data) => {
        this.addContent(data, false);
      });
    } else if (response.status == 400) {
      // failed
      response.json().then((data) => {
        this.content.innerHTML = data;
      });
    }
  }

  clearErrors() {
    this.form.querySelectorAll(".invalid-feedback").forEach((elem) => {
      elem.remove();
    });
    this.form.querySelectorAll(".is-invalid").forEach((elem) => {
      elem.classList.remove("is-invalid");
    });
    // this.form.querySelectorAll("input, select").forEach((elem) => {elem.classList.add("is-valid")})
  }
}
