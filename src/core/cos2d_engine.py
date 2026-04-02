import numpy as np
from scipy.signal import hilbert

class COS2DEngine:

    @classmethod
    def process(cls, matrix_Z, calc_sync=True, calc_async=False):
        ref_spec = cls.get_reference_spectrum(matrix_Z)
        dyn_spec = cls.get_dynamic_spectra(matrix_Z, ref_spec)
        
        results = {"avg_Z": ref_spec}
        
        if calc_sync:
            results["sync_Z"] = cls.calculate_sync(dyn_spec)
            
        if calc_async:
            results["async_Z"] = cls.calculate_async(dyn_spec)
            
        return results
    
    @staticmethod
    def get_reference_spectrum(matrix_Z):
        return np.mean(matrix_Z, axis=0)
    
    @staticmethod
    def get_dynamic_spectra(matrix_Z, ref_spectrum):
        return matrix_Z - ref_spectrum
    
    @staticmethod
    def calculate_sync(dynamic_spectra):
        N = dynamic_spectra.shape[0]
        return (dynamic_spectra.T @ dynamic_spectra) / (N-1)
    
    @staticmethod
    def calculate_async(dynamic_spectra):
        N = dynamic_spectra.shape[0]

        hilbert_transformed = np.imag(hilbert(dynamic_spectra, axis=1))
        return (dynamic_spectra.T @ hilbert_transformed) / (N-1)
    


