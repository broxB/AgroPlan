export async function fetchData(endpoint, full_response = false) {
  return fetch(endpoint)
    .then((response) => {
      if (!full_response) {
        return response.json();
      } else {
        return response;
      }
    })
    .catch((err) => {
      console.log(err);
      return err;
    });
}

export async function sendForm(form, action, endpoint, full_response = false) {
  const formData = new FormData(form);
  return fetch(endpoint, { method: action, body: formData })
    .then((response) => {
      if (!full_response) {
        return response.json();
      } else {
        return response;
      }
    })
    .catch((err) => {
      console.log(err);
      return err;
    });
}
