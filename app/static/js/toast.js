export function manageToast(){
  const toastTrigger = document.getElementById("resetToast");
  const toastList = document.getElementsByClassName("toast");
  toastTrigger.addEventListener("click", () => {
    showToast(toastList);
    return true;
  });
}

export function showToast(toastList) {
  for (let toast of toastList) {
    toast.classList.remove("hide");
    toast.classList.add("show");
  }
}

// function showToast(toastList, timeout) {
//   for (let toastItem of toastList) {
//     var options = timeout ? { delay: timeout } : {};
//     var toast = new bootstrap.Toast(toastItem, options);
//     var bar = toastItem.querySelector(".progress-bar");
//     // bootstrap.Toast.Default.delay = timeout;
//     toast.show();
//     if (timeout) {
//       startProgress(bar, timeout);
//     }
//   }
// }

// function startProgress(bar, timeout) {
//   var width = 100;
//   var interval = timeout / 100;
//   var id = setInterval(() => {
//     if (width > 0) {
//       width--;
//       bar.style.width = `${width}%`;
//     } else {
//       clearInterval(id);
//     }
//   }, interval);
// }
