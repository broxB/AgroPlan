$(document).ready(function() {
    $('[data-toggle=offcanvas]').click(function() {
      $('.row-offcanvas').toggleClass('active');
    });
});

// $(function () {
//   'use strict'

//   $('[data-toggle="offcanvas"]').on('click', function () {
//     $('.row-offcanvas').toggleClass('open')
//   })

//   $('.navbar-nav>li>.nav-link').on('click', function(){
//      $('.offcanvas-collapse').toggleClass('open')
//   })
// })

// function offCanvasCollapse () {
//   document.getElementsByClassName('.row-offcanvas').toggleClass('open');
//   console.log('button clicked');
// }