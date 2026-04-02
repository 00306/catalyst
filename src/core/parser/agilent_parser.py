import os
import xml.etree.ElementTree as ET
from src.model import GPCDataset, Signal
import rainbow as rb
import numpy as np
import glob
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AgilentParser:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.folder_name = os.path.basename(folder_path)

        self.dataset = GPCDataset(folder_name=self.folder_name)

    def parse(self) -> GPCDataset:
        self._parse_sample_xml()
        self._parse_ch_files()
        self._parse_run_log()
        self._parse_acq_method()

        return self.dataset

    def _parse_sample_xml(self):
        xml_path = Path(self.folder_path) / "SAMPLE.XML"
        if not os.path.exists(xml_path):
            return
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            def get_text(tag_name):
                element = root.find(f".//{tag_name}")
                return element.text if element is not None else "Unknown"

            self.dataset.metadata.sample_name = get_text("Name")
            self.dataset.metadata.description = get_text("Description")

        except Exception as e:
            logger.error(f"[{self.folder_name}] SAMPLE.XML 파싱 에러: {e}", exc_info=True)

    def _parse_ch_files(self):
        clean_path = os.path.abspath(str(self.folder_path))
        d_path = Path(clean_path)
        ch_file_paths = list(d_path.glob("*.ch"))
        
        if not ch_file_paths:
            logger.info(f"[.ch 파일이 존재하지 않습니다.]")
            return

        try:
            data_dir = rb.read(clean_path)
        except Exception as e:
            logger.error(f"❌ 폴더 구조 읽기 실패: {e}", exc_info=True)
            return

        base_sample_name = self.dataset.metadata.sample_name

        for ch_path in ch_file_paths:
            file_name = ch_path.name
            detector_name = ch_path.stem.upper()

            try:
                target = data_dir.get_file(file_name)
                
                if target is None:
                    continue

                time_arr = np.atleast_1d(target.xlabels).flatten()
                intensity_arr = np.atleast_1d(target.data).flatten()

                metadata = getattr(target, 'metadata', {})
                unit_str = metadata.get('unit', 'Unknown')
                date_str   = metadata.get('date', 'Unknown')
                method_str = metadata.get('method', 'Unknown')
                inst_str = metadata.get('instrument', 'Unknown Device')

                self.dataset.metadata.method_name = method_str
                self.dataset.metadata.acquisition_date = date_str
                self.dataset.metadata.instrument_name = inst_str

                if len(time_arr) == 0:
                    continue

                signal = Signal(
                    sample_name=base_sample_name,
                    detector_name=detector_name, 
                    time=time_arr, 
                    intensity=intensity_arr, 
                    unit=unit_str,
                    method=method_str,
                    date=date_str,
                    instrument=inst_str
                )
                
                self.dataset.signals[detector_name] = signal

            except Exception as e:
                logger.error(f" {file_name} 상세 파싱 중 에러 발생: {e}")

    def _parse_run_log(self):
        log_path = os.path.join(self.folder_path, "RUN.LOG")
        
        if not os.path.exists(log_path):
            return
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line in lines:
                time_match = re.search(r"(\d{2}:\d{2}:\d{2}\s+\d{2}/\d{2}/\d{2})", line)
                current_time = time_match.group(1) if time_match else None

                if "Method started:" in line:
                    if current_time:
                        self.dataset.metadata.acquisition_date = current_time
                    
                    vial_match = re.search(r"vial#\s*(\d+)", line, re.IGNORECASE)
                    if vial_match:
                        self.dataset.metadata.vial = vial_match.group(1)

                elif "Saving Method" in line:
                    method_match = re.search(r"Saving Method\s+(.+\.M)", line)
                    if method_match:
                        self.dataset.metadata.method_name = method_match.group(1)

        except Exception as e:
            logger.error(f"RUN.LOG 파싱 에러: {e}")

    def _parse_acq_method(self):
        acq_txt_path = os.path.join(self.folder_path, "ACQ.M", "ACQ.TXT")

        if not os.path.exists(acq_txt_path):
            acq_txt_path = os.path.join(self.folder_path, "ACQ.M", "acq.txt")
            if not os.path.exists(acq_txt_path):
                return
            
        try:
            with open(acq_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            flow_match = re.search(r"Column Flow\s*:\s*(.+m[l]/min)", content, re.IGNORECASE)
            if flow_match:
                self.dataset.metadata.flow_rate = flow_match.group(1).strip()

            solvent_match = re.search(r"Solvent A\s*:\s*(.+%\s*\([^)]+\))", content)
            if solvent_match:
                self.dataset.metadata.solvent = solvent_match.group(1).strip()

            temp_match = re.search(r"Optical Unit Temp\.\s*:\s*(.+°C)", content)
            if temp_match:
                self.dataset.metadata.temperature = temp_match.group(1).strip()

            inj_match = re.search(r"Injector volume\s*:\s*(.+µl)", content)
            if inj_match:
                self.dataset.metadata.injection_volume = inj_match.group(1).strip()

        except Exception as e:
            logger.error(f"ACQ.TXT 파싱 에러: {e}")

    @staticmethod
    def get_detector_names(folder_path: str) -> list[str]:
        ch_files = glob.glob(os.path.join(folder_path, "*.ch"))
        return [os.path.splitext(os.path.basename(f))[0].upper() for f in ch_files]