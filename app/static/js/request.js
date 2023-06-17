export async function fetchData(endpoint) {
  return fetch(endpoint)
    .then((response) => response.json())
    .catch((err) => {
      console.log(err);
      return err;
    });
}

export async function sendForm(form, action, endpoint) {
  const formData = new FormData(form);
  const dataJSON = JSON.stringify(Object.fromEntries(formData));
  const headers = new Headers([["Content-Type", "application/json"]]);
  return fetch(endpoint, { method: action, body: dataJSON, headers: headers })
    .then((response) => response.json())
    .catch((err) => {
      console.log(err);
      return err;
    });
}
