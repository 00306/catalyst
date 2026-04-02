from dataclasses import dataclass, field
from typing import Dict
import numpy as np

@dataclass
class Signal:
    sample_name: str
    detector_name: str
    time: np.ndarray
    intensity: np.ndarray
    unit: str
    method: str = "UNKNOWN"
    date: str = "UNKNOWN"
    instrument: str = "UNKNOWN"

@dataclass
class AnalysisResult:
    mn: float = 0.0
    mw: float = 0.0
    pdi: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    log_mw_axis: np.ndarray = field(default_factory=lambda: np.array([]))
    mwd_signal: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class Metadata:
    sample_name: str = "UNKNOWN"
    description: str = "UNKNOWN"
    vial: str = "UNKNOWN"
    acquisition_date: str = "UNKNOWN"
    method_name: str = "UNKNOWN"
    flow_rate: str = "UNKNOWN"
    solvent: str = "UNKNOWN"
    temperature: str = "UNKNOWN"
    injection_volume: str = "UNKNOWN"
    instrument_name: str = "UNKNOWN"




@dataclass
class GPCDataset:
    folder_name: str
    metadata: Metadata = field(default_factory=Metadata)
    signals: Dict[str, Signal] = field(default_factory=dict)
    results: Dict[str, AnalysisResult] = field(default_factory=dict)

