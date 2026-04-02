import numpy as np

class GPCEngine:
    def __init__(self, coeffs):
        self.coeffs = coeffs
    
    def process_and_calculate(self, time_array, intensity_array):
        if len(time_array) < 2:
            return None
        
        slope = (intensity_array[-1] - intensity_array[0]) / (time_array[-1] - time_array[0])
        baseline = intensity_array[0] + slope * (time_array - time_array[0])
        
        corrected_h = intensity_array - baseline
        
        corrected_h = np.where(corrected_h < 0, 0, corrected_h)

        if np.sum(corrected_h) == 0:
            return None

        log_mw = np.polyval(self.coeffs, time_array)
        mw_i = 10 ** log_mw
        
        mn = np.sum(corrected_h) / np.sum(corrected_h / mw_i) 
        mw = np.sum(corrected_h * mw_i) / np.sum(corrected_h)
        pdi = mw / mn
        
        mp = mw_i[np.argmax(corrected_h)]

        max_h = np.max(corrected_h)
        mwd_signal = corrected_h / max_h if max_h != 0 else corrected_h

        return {
            "Mn": round(mn, 2),
            "Mw": round(mw, 2),
            "PDI": round(pdi, 3),
            "Mp": round(mp, 2),
            "log_mw_axis": log_mw,
            "mwd_signal": mwd_signal
        }