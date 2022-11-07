$(document).ready(function() {
  $('[data-bs-toggle=sidebarCollapse]').click(function() {
    $('#sidebarNav').toggleClass('show');
    $(this).attr('aria-expanded', function(i, attr) {return attr == 'true' ? 'false': 'true'});
    activateSidebarItem();
  });
});

// call function when page content is loaded
document.addEventListener("DOMContentLoaded", function() {
  activateSidebarItem();
});

// scroll to selected field and add active tag
function activateSidebarItem () {
  const value = JSON.parse(document.getElementById('data').textContent);
  var element = document.getElementById(value);
  element.scrollIntoView();
  element.classList.toggle('active');
};
