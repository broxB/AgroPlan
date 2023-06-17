export function manageFields() {
  document.querySelectorAll(".header").forEach((header) => {
    header.addEventListener("click", (event) => {
      event.preventDefault();
      let span = header.querySelector("tr>th>span");
      span.textContent = span.textContent == "+" ? "-" : "+";
      let elems = nextUntil(header, ".header");
      for (let elem of elems) {
        elem.classList.toggle("show");
      }
    });
  });
}

function nextUntil(elem, selector, filter) {
  var siblings = [];
  elem = elem.nextElementSibling;
  while (elem) {
    if (elem.matches(selector)) break;
    // If filtering by a selector, check if the sibling matches
    if (filter && !elem.matches(filter)) {
      elem = elem.nextElementSibling;
      continue;
    }
    siblings.push(elem);
    elem = elem.nextElementSibling;
  }
  return siblings;
}
