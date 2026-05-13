(function () {
  'use strict';

  /* ====== 1. BLOQUEO DE CLIC DERECHO ====== */
  document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    return false;
  });

  /* ====== 2. BLOQUEO DE TECLAS Y COMBINACIONES ====== */
  document.addEventListener('keydown', function (e) {
    var blocked = false;

    var ctrl = e.ctrlKey || e.metaKey;
    var shift = e.shiftKey;
    var alt = e.altKey;
    var key = e.keyCode || e.which;
    var keyName = e.key || '';

    var c = '';
    try { c = String.fromCharCode(key).toLowerCase(); } catch (ex) {}

    var ctrlShift = ctrl && shift;
    var anyModifier = ctrl || shift || alt;

    if (ctrl) {
      if (
        c === 'c' || c === 'v' || c === 'x' || c === 's' ||
        c === 'u' || c === 'p' || c === 'a'
      ) {
        blocked = true;
      }
    }

    if (keyName === 'F12' || key === 123) {
      blocked = true;
    }

    if (keyName === 'F1' || key === 112) {
      if (anyModifier || true) {
        blocked = true;
      }
    }

    if (ctrlShift) {
      if (
        key === 73 || key === 74 || key === 67 ||
        c === 'i' || c === 'j' || c === 'c'
      ) {
        blocked = true;
      }
      if (key === 70 || c === 'f') {
        blocked = true;
      }
      if (key === 77 || c === 'm') {
        blocked = true;
      }
      if (key === 69 || c === 'e') {
        blocked = true;
      }
    }

    if (alt) {
      if (key === 68 || keyName.toLowerCase() === 'd') {
        blocked = true;
      }
    }

    if (blocked) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    return true;
  });

  /* ====== 3. DETECCIÓN DE DEVTOOLS (OVERLAY NO DESTRUCTIVO) ====== */
  var devtoolsOpen = false;
  var threshold = 160;
  var secOverlay = null;

  function showSecOverlay(msg) {
    if (document.getElementById('sec-overlay')) return;
    var ov = document.createElement('div');
    ov.id = 'sec-overlay';
    ov.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:#0f172a;color:#ef4444;display:flex;align-items:center;justify-content:center;z-index:99999;font-family:sans-serif;text-align:center;padding:2rem;';
    ov.innerHTML = '<div><h1 style="font-size:2rem;margin-bottom:1rem;">⚠️ ACCESO DENEGADO</h1><p style="font-size:1.1rem;color:#94a3b8;">' + msg + '</p><p style="font-size:0.9rem;color:#64748b;margin-top:1rem;">Por favor, cierra las herramientas de desarrollo y recarga la página.</p></div>';
    document.body.appendChild(ov);
  }

  function hideSecOverlay() {
    var ov = document.getElementById('sec-overlay');
    if (ov) ov.remove();
  }

  setInterval(function () {
    var widthThreshold = window.outerWidth - window.innerWidth > threshold;
    var heightThreshold = window.outerHeight - window.innerHeight > threshold;
    if (widthThreshold || heightThreshold) {
      if (!devtoolsOpen) {
        devtoolsOpen = true;
        document.title = '🔒 DevTools Detectado';
        showSecOverlay('Las herramientas de desarrollador están deshabilitadas en este sistema.');
      }
    } else {
      if (devtoolsOpen) {
        devtoolsOpen = false;
        hideSecOverlay();
        document.title = '';
      }
    }
  }, 1000);

  /* ====== 4. BLOQUEO DE ARRASTRE ====== */
  document.addEventListener('dragstart', function (e) {
    e.preventDefault();
    return false;
  });

  /* ====== 5. BLOQUEO DE SELECCIÓN VÍA JS ====== */
  document.addEventListener('selectstart', function (e) {
    e.preventDefault();
    return false;
  });

  /* ====== 6. BLOQUEO DE COPIADO ====== */
  document.addEventListener('copy', function (e) {
    e.preventDefault();
    return false;
  });
  document.addEventListener('cut', function (e) {
    e.preventDefault();
    return false;
  });
  document.addEventListener('paste', function (e) {
    e.preventDefault();
    return false;
  });

  /* ====== 7. DETECCIÓN DE CONSOLA (SOBREESCRITURA NO DESTRUCTIVA) ====== */
  (function() {
    var consolaDetectada = false;
    var element = new Image();
    Object.defineProperty(element, 'id', {
      get: function () {
        if (!consolaDetectada) {
          consolaDetectada = true;
          document.title = '🔒 Consola Detectada';
          showSecOverlay('La consola de desarrollador está bloqueada en este sistema.');
        }
      }
    });
    try { console.log('%c', element); } catch(e) {}
  })();

  /* ====== 8. DEBUGGER INFINITO (REDUCIDO) ====== */
  setInterval(function () {
    debugger;
  }, 10000);

})();
