<div align="center">
  <h1>Catalyst</h1>
  <p><strong>GPC Data Analysis &amp; Visualization</strong></p>
  <p>A desktop app for analyzing GPC (Gel Permeation Chromatography) data with 3D chromatograms and 2D-COS</p>
  <img width="800" alt="Catalyst dashboard" src="https://github.com/user-attachments/assets/f8277e2b-a509-49c5-a4be-51f3c24cc0b2" />
  <p>
    <code>Python</code> · <code>PyQt5</code> · <code>QtWebEngine</code> · <code>Plotly</code> · <code>NumPy</code> · <code>SciPy</code>
  </p>
</div>

<br>

## Getting Started

Download the latest build from [Releases (v1.0.1)](https://github.com/00306/catalyst/releases/tag/v1.0.1).

| Platform | Steps |
|:---|:---|
| macOS (Apple Silicon) | Download `Catalyst_v1.01_macOS.zip`, unzip it, move `Catalyst.app` to Applications, and double-click to launch. |
| Windows 10/11 (x64) | Download `Catalyst_v1.01_Windows.zip`, unzip it, and run `Catalyst.exe` inside the folder. If a SmartScreen warning appears, click **More info** → **Run anyway**. |

<br>

## Features

### 3D Chromatogram & Heatmap

Drop Agilent `.D` folders into the app to load their detector data (`.ch`). Multiple samples are shown together as a 3D chromatogram and a heatmap, and the 3D plot can be rotated to compare samples.

### 2D-COS

Computes synchronous and asynchronous 2D correlation spectra to show how samples change relative to each other.

<img width="600" alt="2D-COS" src="https://github.com/user-attachments/assets/1217cbaf-527e-41f4-b770-53fd872a8c54" />

### Chromatogram

Overlay chromatograms of all samples and read retention time and signal values with a crosshair. The analysis range can be adjusted and applied to every sample at once.

<img width="600" alt="Chromatogram" src="https://github.com/user-attachments/assets/0638ff0f-5ce4-42ef-ab91-a4d2822d6214" />

### Molecular Weight Distribution

Applies a calibration curve (3rd-order polynomial) to plot the molecular weight distribution (MWD) and lists Mn, Mw, and PDI for each sample. Calibration curves can be saved by name and reused.

<img width="600" alt="Molecular weight distribution" src="https://github.com/user-attachments/assets/f8d7d8a1-eddb-46d6-abee-77123ed985c6" />

### Dark · Paper Theme

One button switches the whole app between a dark theme for long analysis sessions and a white-background theme for papers. Plots can be saved as images at 4x resolution, exactly as they appear on screen.

<table>
  <tr>
    <td><img width="360" alt="Dark theme" src="https://github.com/user-attachments/assets/d532e30e-b970-4f3b-8dd8-edf1c2e8fc1c" /></td>
    <td><img width="360" alt="Paper theme" src="https://github.com/user-attachments/assets/2bf70175-d032-434a-93b6-8bd9a0c5cea0" /></td>
  </tr>
  <tr>
    <td align="center">Dark</td>
    <td align="center">Paper</td>
  </tr>
</table>

<br>

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
