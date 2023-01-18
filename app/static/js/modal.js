// request: modal content
var modal = document.getElementById("modal");
modal.addEventListener("show.bs.modal", async function (event) {
  var button = event.relatedTarget;
  // get params for form
  var modalType = button.dataset.modal;
  var formType = button.dataset.form;
  var modalContent = modal.querySelector(".modal-content");
  var id;
  if (button.closest("tr")) {
    var id = button.closest("tr").dataset.id;
  } else {
    id = null;
  }
  var field = document.getElementById("field");
  var params = [];
  if (formType == "cultivation") {
    params.push(field.dataset.fieldId);
  } else if (formType == "fertilization") {
    params.push(field.dataset.fieldId);
  } else if (formType == "soil") {
    params.push(field.dataset.baseId);
  }
  const modalURL =
    "/modal?" +
    new URLSearchParams({ modal: modalType, form: formType, params: params, id: id }).toString();
  console.log(modalURL);
  const modalData = await fetch(modalURL).then((response) => response.json());
  modalContent.innerHTML = modalData;
  if (modalType == "edit") {
    // add change event for crop and fert classes
    var crop_class = modalContent.querySelector("#crop_class");
    var fert_class = modalContent.querySelector("#fert_class");
    var selectElem;
    var selectURL;
    var nextSelect;
    if (crop_class != null) {
      selectElem = crop_class;
      selectURL = "/crop/";
      nextSelect = modalContent.querySelector("#crop");
    } else if (fert_class != null) {
      selectElem = fert_class;
      selectURL = "/fertilizer/";
      nextSelect = modalContent.querySelector("#fertilizer");
    }
    selectElem.addEventListener("change", () => {
      deleteInputs(modalContent, [selectElem, nextSelect]);
      changeSelect(selectURL, selectElem, nextSelect);
    });
  }
});

// when modal is closed, content is deleted
modal.addEventListener("hidden.bs.modal", function () {
  var modalContent = modal.querySelector(".modal-content");
  modalContent.innerHTML = "";
});

// delete all inputs, except specified
function deleteInputs(content, omitted) {
  content.querySelectorAll("input.form-control").forEach((element) => {
    if (!omitted.includes(element)) {
      element.parentNode.remove();
    }
  });
}

// fetches and changes select content, when select value changes
async function changeSelect(selectUrl, selectElem, nextSelect) {
  let value = selectElem.value;
  const data = await fetch(selectUrl + value).then((response) => response.json());
  let optionHTML = "";
  for (let elem of data) {
    optionHTML += `<option value=${elem.id}>${elem.name}</option>`;
  }
  nextSelect.innerHTML = optionHTML;
  console.log(optionHTML);
  console.log(value);
  console.log(data);
}
