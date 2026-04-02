const WebLoading = {
  _hideTimer: null,

  init: function (theme) {
    if (this._hideTimer) {
      clearTimeout(this._hideTimer);
      this._hideTimer = null;
    }

    if (typeof applyTheme === "function") {
      applyTheme(theme);
    }

    const oldOverlay = document.getElementById("web-overlay");
    if (oldOverlay) {
      oldOverlay.remove();
    }

    const bgColor = theme.bg_base;
    const textColor = theme.text_primary;
    const accentColor = theme.bg_spinner;
    const borderColor = theme.border_base;

    const overlayHtml = `
      <div id="web-overlay" style="
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: ${bgColor}; z-index: 99999;
        display: flex; justify-content: center; align-items: center;
        opacity: 1; transition: none;
      ">
        <div style="text-align: center; font-family: 'Arial', sans-serif;">
          <div class="spinner" style="
            border: 3px solid ${borderColor};
            border-left-color: ${accentColor};
            border-radius: 50%; width: 30px; height: 30px;
            animation: spin 1s linear infinite; margin: 0 auto 15px;
          "></div>
          <div class="loading-text" style="color: ${textColor}; font-size: 12px; font-weight: bold; opacity: 0.8; letter-spacing: 1px;">
            RENDERING...
          </div>
        </div>
        <style>
          @keyframes spin { to { transform: rotate(360deg); } }
        </style>
      </div>
    `;

    document.body.insertAdjacentHTML("afterbegin", overlayHtml);

    let newOverlay = document.getElementById("web-overlay");
    void newOverlay.offsetWidth;
    newOverlay.style.transition = "opacity 0.2s ease-out";
  },

  hide: function () {
    const overlay = document.getElementById("web-overlay");
    if (overlay) {
      overlay.style.transition = "opacity 0.2s ease-out";
      overlay.style.opacity = "0";

      this._hideTimer = setTimeout(() => {
        overlay.style.display = "none";
        if (window.pyBridge && window.pyBridge.on_render_finished) {
          window.pyBridge.on_render_finished();
        }
        this._hideTimer = null;
      }, 200);
    }
  },
};
