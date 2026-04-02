window.initCrosshair = function (gd, options = {}) {
  if (!gd) return;

  const metaTheme = (gd.layout && gd.layout.meta) || {};
  const sliceLineColor =
    options.sliceLineColor || metaTheme.sliceLineColor || "rgba(0, 0, 0, 0.5)";

  if (gd._hasCrosshairOverlay) {
    if (window.startLine && window.endLine) {
      const newGradient = `linear-gradient(to bottom, ${sliceLineColor} 50%, transparent 50%)`;
      window.startLine.style.backgroundImage = newGradient;
      window.endLine.style.backgroundImage = newGradient;
    }

    return;
  }

  gd._hasCrosshairOverlay = true;

  var overlay = document.createElement("div");
  overlay.style.cssText =
    "position:absolute; left:0; top:0; width:100%; height:100%; z-index:9999; cursor:none; pointer-events:all;";

  function formatTime(decimalMinutes) {
    var mins = Math.floor(decimalMinutes);
    var secs = Math.round((decimalMinutes - mins) * 60);
    if (secs === 60) {
      mins++;
      secs = 0;
    }
    return (
      decimalMinutes.toFixed(2) +
      " (" +
      mins +
      "' " +
      (secs < 10 ? "0" : "") +
      secs +
      '")'
    );
  }

  function createLabel() {
    var lb = document.createElement("div");
    lb.style.cssText =
      "position:absolute; padding:2px 6px; background:rgba(255, 46, 88, 0.9); color:white; font-size:11px; font-weight:bold; pointer-events:none; display:none; white-space:nowrap; z-index:10001;";
    return lb;
  }

  function findNearestIndex(arr, target) {
    let low = 0;
    let high = arr.length - 1;

    while (low <= high) {
      let mid = Math.floor((low + high) / 2);
      if (arr[mid] == target) return mid;
      if (arr[mid] < target) low = mid + 1;
      else high = mid - 1;
    }

    return target - arr[high] < arr[low] - target ? high : low;
  }

  var xLabel = createLabel();
  var yLabel = createLabel();
  var infoRibbon = createLabel();
  infoRibbon.style.cssText =
    "position:absolute; color:rgba(255, 255, 255, 0.9); font-size:13px; font-weight:normal; pointer-events:none; display:none; z-index:10002;";

  // overlay.appendChild(infoRibbon);
  overlay.appendChild(xLabel);
  overlay.appendChild(yLabel);

  var vLine = document.createElement("div");
  var hLine = document.createElement("div");

  [vLine, hLine].forEach((line) => {
    line.style.cssText =
      "position:absolute; display:none; pointer-events:none;";
    overlay.appendChild(line);
  });

  // 선 스타일 설정
  vLine.style.width = "0px";
  vLine.style.borderLeft = "1.5px dashed #FF2E58";
  hLine.style.height = "0px";
  hLine.style.borderTop = "1.5px dashed #FF2E58";

  const timeData = gd.data[0].x;
  const minTime = timeData[0];
  const maxTime = timeData[timeData.length - 1];

  let sliceStartData = minTime;
  let sliceEndData = maxTime;
  let dragTarget = null;

  var startLine = document.createElement("div");
  var endLine = document.createElement("div");

  [startLine, endLine].forEach((line, index) => {
    line.style.cssText = `
        position: absolute; 
        width: 2px; /* 선의 굵기 */
        margin-left: -1px; 
        pointer-events: none; 
        display: none; 
        z-index: 10000; 
        height: 100%;
        /* 👇 여기서부터가 진짜 마법입니다 */
        background-image: linear-gradient(to bottom, ${sliceLineColor} 50%, transparent 50%);
        background-size: 2px 6px; /* 👈 요 숫자가 핵심! (가로 2px, 세로 6px 단위로 반복) */
        background-repeat: repeat-y;
    `;

    const input = document.createElement("input");
    input.type = "text";
    input.className = "range-label";
    input.style.cssText = `
        position: absolute;
        bottom: -30px; /* 차트 바닥 아래에 위치 */
        left: -25px;   /* 중앙 정렬을 위해 오프셋 */
        width: 50px;
        background: #3e3e42;
        color: #d4d4d4;
        border: 1px solid #555;
        border-radius: 4px;
        font-size: 11px;
        text-align: center;
        pointer-events: auto; /* 마우스 클릭/입력 가능하게 */
    `;

    input.onkeydown = (e) => {
      if (e.key === "Enter") {
        let newTime = parseFloat(e.target.value);

        if (isNaN(newTime)) {
          e.target.value = (
            index === 0 ? sliceStartData : sliceEndData
          ).toFixed(2);
          return;
        }

        if (index === 0) {
          if (newTime >= sliceEndData) {
            newTime = sliceEndData - 0.1;
          }
          sliceStartData = newTime;
        } else {
          if (newTime <= sliceStartData) {
            newTime = sliceStartData + 0.1;
          }
          sliceEndData = newTime;
        }

        updateSliceLines();

        if (window.plotBridge && window.plotBridge.receive_slice_range) {
          window.plotBridge.receive_slice_range(sliceStartData, sliceEndData);
        }

        input.blur();
      }
    };

    line.appendChild(input);

    overlay.appendChild(line);

    if (index === 0) {
      window.startLine = line;
      window.startInput = input;
      input.placeholder = "Start";
    } else {
      window.endLine = line;
      window.endInput = input;
      input.placeholder = "End";
    }
  });

  var leftMask = document.createElement("div");
  var rightMask = document.createElement("div");

  [leftMask, rightMask].forEach((mask) => {
    mask.style.cssText =
      "position:absolute; background: rgba(0, 0, 0, 0.3); pointer-events:none; display: none; z-index:9998;";
    overlay.appendChild(mask);
  });

  function updateSliceLines() {
    var fullLayout = gd._fullLayout;
    if (!fullLayout) return;

    var xAxis = fullLayout.xaxis;
    var yAxis = fullLayout.yaxis;

    var pLeft = xAxis._offset;
    var pTop = yAxis._offset;
    var pWidth = xAxis._length;
    var pHeight = yAxis._length;

    var startPx = xAxis.c2p(sliceStartData) + pLeft;
    var endPx = xAxis.c2p(sliceEndData) + pLeft;

    startLine.style.display = "block";
    startLine.style.left = startPx + "px";
    startLine.style.top = pTop + "px";
    startLine.style.height = pHeight + "px";

    endLine.style.display = "block";
    endLine.style.left = endPx + "px";
    endLine.style.top = pTop + "px";
    endLine.style.height = pHeight + "px";

    leftMask.style.display = "block";
    leftMask.style.left = pLeft + "px";
    leftMask.style.top = pTop + "px";
    leftMask.style.width = Math.max(0, startPx - pLeft) + "px";
    leftMask.style.height = pHeight + "px";

    rightMask.style.display = "block";
    rightMask.style.left = endPx + "px";
    rightMask.style.top = pTop + "px";
    rightMask.style.width = Math.max(0, pLeft + pWidth - endPx) + "px";
    rightMask.style.height = pHeight + "px";

    if (window.startInput) window.startInput.value = sliceStartData.toFixed(2);
    if (window.endInput) window.endInput.value = sliceEndData.toFixed(2);
  }

  overlay.addEventListener("mousedown", function (e) {
    if (window.isRangeLocked) return;

    var rect = this.getBoundingClientRect();
    var fullLayout = gd._fullLayout;
    if (!fullLayout) return;

    var xAxis = fullLayout.xaxis;
    var pLeft = xAxis._offset;
    var mouseX = e.clientX - rect.left;

    var startPx = xAxis.c2p(sliceStartData) + pLeft;
    var endPx = xAxis.c2p(sliceEndData) + pLeft;

    if (Math.abs(mouseX - startPx) < 6) {
      dragTarget = "start";
    } else if (Math.abs(mouseX - endPx) < 6) {
      dragTarget = "end";
    }
  });

  overlay.addEventListener("mouseup", function (e) {
    if (dragTarget) {
      console.log(
        "✂️ 잘린 구간:",
        sliceStartData.toFixed(2),
        "~",
        sliceEndData.toFixed(2)
      );

      if (window.plotBridge) {
        window.plotBridge.receive_slice_range(
          sliceStartData,
          sliceEndData,
          function () {}
        );
      }
    }
    dragTarget = null;
  });

  overlay.addEventListener("mousemove", function (e) {
    var rect = gd.getBoundingClientRect();
    var fullLayout = gd._fullLayout;
    if (!fullLayout) return;

    var xAxis = fullLayout.xaxis;
    var yAxis = fullLayout.yaxis;

    // 그래프 영역 마진 및 크기 정보
    var pLeft = xAxis._offset;
    var pTop = yAxis._offset;
    var pWidth = xAxis._length;
    var pHeight = yAxis._length;
    var pBottom = pTop + pHeight;

    var mouseX = e.clientX - rect.left;
    var mouseY = e.clientY - rect.top;

    var xData = xAxis.p2c(mouseX - pLeft);

    if (dragTarget === "start") {
      // Start가 End를 넘지 못하게 방어 (최소 간격 0.1분 유지)
      if (xData >= sliceEndData) xData = sliceEndData - 0.1;
      if (xData < minTime) xData = minTime;

      sliceStartData = xData;
      updateSliceLines();
      return; // 드래그 중에는 기존 십자선(크로스헤어) 코드는 실행 안 함
    } else if (dragTarget === "end") {
      // End가 Start보다 작아지지 않게 방어
      if (xData <= sliceStartData) xData = sliceStartData + 0.1;
      if (xData > maxTime) xData = maxTime;

      sliceEndData = xData;
      updateSliceLines();
      return;
    }

    var startPx = xAxis.c2p(sliceStartData) + pLeft;
    var endPx = xAxis.c2p(sliceEndData) + pLeft;
    if (Math.abs(mouseX - startPx) < 6 || Math.abs(mouseX - endPx) < 6) {
      overlay.style.cursor = "ew-resize";
    } else {
      overlay.style.cursor = "none";
    }

    if (
      mouseX >= pLeft &&
      mouseX <= pLeft + pWidth &&
      mouseY >= pTop &&
      mouseY <= pBottom
    ) {
      var xData = xAxis.p2c(mouseX - pLeft);
      var yData = yAxis.p2c(mouseY - pTop);

      var times = gd.data[0].x;
      var intensities = gd.data[0].y;
      var nearestIdx = findNearestIndex(times, xData);

      if (window.Plotly && Plotly.Fx) {
        try {
          Plotly.Fx.hover(gd, {
            xval: xAxis.p2c(mouseX - pLeft),
            yval: yAxis.p2c(mouseY - pTop),
            hovermode: "x",
          });
        } catch (e) {
          console.log("시발 에러 발생: }", e);
        }
      }

      var actualX = times[nearestIdx];
      var actualY = intensities[nearestIdx];

      var snapX = xAxis.c2p(actualX) + pLeft;

      [vLine, hLine, xLabel, yLabel, infoRibbon].forEach(
        (el) => (el.style.display = "block")
      );

      vLine.style.transform = "translateX(" + snapX + "px)";
      vLine.style.top = pTop + "px";
      vLine.style.height = pHeight + "px";

      hLine.style.transform = "translateY(" + mouseY + "px)";
      hLine.style.left = pLeft + "px";
      hLine.style.width = pWidth + "px";

      xLabel.innerHTML = formatTime(actualX);
      xLabel.style.left = mouseX - xLabel.offsetWidth / 2 + "px";
      xLabel.style.top = pBottom + 5 + "px";

      var currentMouseYData = yAxis.p2c(mouseY - pTop);
      yLabel.innerHTML = Number(currentMouseYData).toFixed(2);
      yLabel.style.left = pLeft + 5 + "px";
      yLabel.style.top = mouseY - yLabel.offsetHeight / 2 + "px";

      infoRibbon.style.left = pLeft + 10 + "px";
      infoRibbon.style.top = pTop + 10 + "px";

      infoRibbon.innerHTML = `Intensity: ${Number(actualY).toLocaleString(
        undefined,
        { minimumFractionDigits: 2 }
      )}`;
    } else {
      if (window.Plotly && Plotly.Fx) {
        Plotly.Fx.unhover(gd);
      }
      [vLine, hLine, xLabel, yLabel, infoRibbon].forEach(
        (el) => (el.style.display = "none")
      );
    }
  });

  overlay.addEventListener("mouseleave", function () {
    if (window.Plotly && Plotly.Fx) {
      Plotly.Fx.unhover(gd);
    }

    [vLine, hLine, xLabel, yLabel].forEach((el) => (el.style.display = "none"));
  });

  setTimeout(updateSliceLines, 100);
  gd.on("plotly_afterplot", updateSliceLines);

  gd.style.position = "relative";
  gd.appendChild(overlay);
};

window.setBarLockState = function (shouldLock) {
  const color = shouldLock
    ? "rgba(255, 0, 0, 0.8)"
    : "rgba(255, 255, 255, 0.5)";
  const pointerEvents = shouldLock ? "none" : "auto";
  const opacity = shouldLock ? "0.6" : "1";
  if (window.startLine) window.startLine.style.borderColor = color;
  if (window.endLine) window.endLine.style.borderColor = color;

  [window.startInput, window.endInput].forEach((input) => {
    if (input) {
      input.disabled = shouldLock;
      input.style.opacity = opacity;
      input.style.cursor = shouldLock ? "not-allowed" : "text";
      if (shouldLock) input.style.borderColor = "red";
      else input.style.borderColor = "#555";
    }
  });

  window.isRangeLocked = shouldLock;
};
