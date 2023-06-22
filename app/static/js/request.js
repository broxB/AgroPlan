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
  return fetch(endpoint, { method: action, body: formData })
    .then((response) => response.json())
    .catch((err) => {
      console.log(err);
      return err;
    });
}
