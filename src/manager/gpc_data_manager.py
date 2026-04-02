import numpy as np
from src.model import GPCDataset
from typing import List
from src.core import GPCEngine
from src.model import AnalysisResult

class GPCDataManager:
    def __init__(self):
        self.datasets: List[GPCDataset] = []

    def add_dataset(self, dataset: GPCDataset):
        self.datasets.append(dataset)

    def get_mesh_data(self, detector_name: str, z_gap: float = 10.0, num_points: int = 1000):
        if not self.datasets:
            return None, None, None, None
        
        valid_signals = []
        actual_names = []

        if self.datasets:
            available_channels = list(self.datasets[0].signals.keys())

        for ds in self.datasets:
            if detector_name in ds.signals:
                valid_signals.append(ds.signals[detector_name])
                actual_names.append(ds.folder_name)

        if not valid_signals:
            return None, None, None, None
        
        c_min = max(np.min(sig.time) for sig in valid_signals)
        c_max = min(np.max(sig.time) for sig in valid_signals)

        if c_min >= c_max:
            return None, None, None, None

        common_x = np.linspace(c_min, c_max, num_points)

        z_list = []
        for sig in valid_signals:
            sort_idx = np.argsort(sig.time)
            z_vals = np.interp(common_x, sig.time[sort_idx], sig.intensity[sort_idx])
            z_list.append(z_vals)
        
        Z = np.array(z_list)

        y_coords = np.arange(len(valid_signals)) * z_gap
        
        X, Y = np.meshgrid(common_x, y_coords)
        
        return X, Y, Z, actual_names
        
    def apply_calibration(self, coeffs: List[float], detector_name: str):
        engine = GPCEngine(coeffs)

        for ds in self.datasets:
            if detector_name in ds.signals:
                sig = ds.signals[detector_name]
                res_dict = engine.process_and_calculate(sig.time, sig.intensity)

                if res_dict:
                        ds.results[detector_name] = AnalysisResult(
                            mn=res_dict['Mn'],
                            mw=res_dict['Mw'],  
                            pdi=res_dict['PDI']
                    )

    def get_trend_data(self, detector_name: str, metric: str):
        trend_values = []

        for ds in self.datasets:
            res = ds.results.get(detector_name)

            if res:
                trend_values.append(getattr(res, metric.lower()))
            else:
                trend_values.append(0.0)

        return trend_values
