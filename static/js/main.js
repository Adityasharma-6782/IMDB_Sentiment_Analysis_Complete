document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('siteNav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  document.querySelectorAll('.flash-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var flash = btn.closest('.flash');
      if (flash) flash.remove();
    });
  });

  // Auto-dismiss success/info flashes after a few seconds
  document.querySelectorAll('.flash-success, .flash-info').forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = 'opacity 0.4s ease';
      flash.style.opacity = '0';
      setTimeout(function () { flash.remove(); }, 400);
    }, 5000);
  });
});
