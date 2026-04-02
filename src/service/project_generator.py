import os
import io
import json
import zipfile
import numpy as np
from src.model import ProjectConfig, ProjectMetadata
from src.manager import GPCDataManager
from src.core.parser import AgilentParser


class ProjectGenerator:

    def __init__(self, setup_data: ProjectConfig):
        self.setup_data = setup_data

    def run(self):
        if self.setup_data.mode == "Overlay":
            return self._process_overlay()
        elif self.setup_data.mode == "Multi-Detector":
            return self._process_multi_detector()
    
    def _process_overlay(self):
        total_manager = GPCDataManager()
        folders = self.setup_data.folder_paths
        
        for folder_path in folders:
            try:
                parser = AgilentParser(folder_path)
                dataset = parser.parse()
                total_manager.add_dataset(dataset)
            except Exception as e:
                print(f"❌ 파싱 실패: {os.path.basename(folder_path)} -> {e}")

        if not total_manager.datasets:
            raise ValueError("⚠️ 처리할 유효한 데이터가 없습니다. (파싱 모두 실패)")
        
        all_z_data = {}
        common_dets = self.setup_data.common_detectors

        X, Y = None, None
        

        for det in common_dets:
            cur_X, cur_Y, Z, valid_names = total_manager.get_mesh_data(detector_name=det)
            if Z is not None:
                all_z_data[det] = Z
                X, Y = cur_X, cur_Y

            if X is None or Y is None or not all_z_data:
                raise ValueError("⚠️ 매칭되는 디텍터 데이터가 없어 3D 데이터를 생성할 수 없습니다.")

        final_valid_names = [ds.metadata.sample_name for ds in total_manager.datasets]

        methods_dict = {}
        inst_dict = {}
        dates_dict = {}

        for ds in total_manager.datasets:
            s_name = ds.metadata.sample_name
            methods_dict[s_name] = getattr(ds.metadata, 'method_name', 'Unknown')
            inst_dict[s_name] = getattr(ds.metadata, 'instrument_name', 'Unknown')
            dates_dict[s_name] = getattr(ds.metadata, 'acquisition_date', 'Unknown')

        metadata = ProjectMetadata(
            project_name=self.setup_data.project_name,
            description=self.setup_data.description,
            mode="Overlay",
            sample_names=final_valid_names,
            detectors=list(all_z_data.keys()),
            default_detector=self.setup_data.target_detector,
            z_unit_dict={
                det: next((ds.signals[det].unit for ds in total_manager.datasets if det in ds.signals), "Unknown Unit")
                for det in all_z_data.keys()
            },   
            methods=methods_dict,
            instruments=inst_dict,
            analysis_dates=dates_dict
        )

        final_save_path = str(self.setup_data.save_path)

        if not final_save_path.lower().endswith('.pkz'):
            final_save_path = os.path.splitext(final_save_path)[0] + ".pkz"

        self._save_to_pkz(final_save_path, X, Y, all_z_data, metadata)
        return final_save_path

    def _process_multi_detector(self):
        pass
        # files = self.setup_data.file_paths
        # if len(files) < 2:
        #     raise ValueError("멀티 디텍터 모드에는 최소 2개의 파일이 필요합니다.")

        # ch_a = GPCParser().to_channel(files[0], vendor='AIA_STANDARD')
        # ch_b = GPCParser().to_channel(files[1], vendor='AIA_STANDARD')

        # name_a = ch_a.channel_name if ch_a.channel_name else "Detector A"
        # name_b = ch_b.channel_name if ch_b.channel_name else "Detector B"
        # sample_name = ch_a.sample_name if ch_a.sample_name else "Unknown Sample"

        # time_x = np.array(ch_a.times)
        
        # def normalize_1d(arr):
        #     min_v, max_v = np.min(arr), np.max(arr)
        #     return (arr - min_v) / (max_v - min_v) if max_v != min_v else arr

        # norm_a = normalize_1d(np.array(ch_a.intensities))
        # norm_b = normalize_1d(np.interp(time_x, ch_b.times, ch_b.intensities))

        # metadata = ProjectMetadata(
        #     project_name=self.setup_data.project_name,
        #     description=self.setup_data.description,
        #     mode="Multi-Detector",
        #     sample_names=[sample_name],
        #     channel_name=f"{name_a} vs {name_b}",
        #     z_unit="Normalized"
        # )

        # final_path = str(self.setup_data.save_path)
        
        # self._save_to_mdz(
        #     final_path, 
        #     time_x, 
        #     norm_a, 
        #     norm_b, 
        #     metadata, 
        #     name_a, 
        #     name_b
        # )
    
        # return final_path

    def _save_to_pkz(self, file_path, x_data, y_data, z_dict, metadata_obj: ProjectMetadata):
        npz_buffer = io.BytesIO()
        np.savez_compressed(npz_buffer, x=x_data, y=y_data, **z_dict)
        
        json_str = json.dumps(metadata_obj.to_dict(), indent=4, ensure_ascii=False)

        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.npz', npz_buffer.getvalue())
            zf.writestr('metadata.json', json_str)


    def _save_to_mdz(self, file_path, time, det_a, det_b, metadata_obj, det_a_name, det_b_name):

        npz_buffer = io.BytesIO()
        np.savez_compressed(npz_buffer, time=time, det_a=det_a, det_b=det_b)
    
        meta_dict = metadata_obj.to_dict()
        meta_dict["detector_A"] = det_a_name
        meta_dict["detector_B"] = det_b_name
        meta_dict["intensity_unit"] = "Normalized"

        json_str = json.dumps(meta_dict, indent=4, ensure_ascii=False)

        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.npz', npz_buffer.getvalue())
            zf.writestr('metadata.json', json_str)



