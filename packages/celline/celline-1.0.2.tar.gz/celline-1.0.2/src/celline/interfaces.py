from __future__ import annotations

import os
import subprocess
from collections.abc import Callable

# from celline.database import NCBI, GSE, GSM
from typing import Final

import toml

from celline.config import Config, Setting
from celline.functions._base import CellineFunction
from celline.middleware import ThreadObservable
from celline.server import ServerSystem
from celline.utils.path import Path


class Project:
    """Celline project"""

    EXEC_PATH: Final[str]
    PROJ_PATH: Final[str]

    def __init__(self, project_dir: str, proj_name: str = "", r_path: str = "") -> None:
        """#### Load or create new celline project"""

        def get_r_path() -> str:
            # Try common R installation paths first (faster)
            common_paths = ["/usr/bin/R", "/usr/local/bin/R", "/opt/homebrew/bin/R"]
            for path in common_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    return path
            
            # Fallback to system search only if needed
            try:
                with subprocess.Popen(
                    "which R",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,  # Suppress error output
                    shell=True,
                    timeout=2  # Add timeout to prevent hanging
                ) as proc:
                    result = proc.communicate()
                return result[0].decode("utf-8").strip()
            except (subprocess.TimeoutExpired, Exception):
                return "/usr/bin/R"  # Default fallback

        def get_default_proj_name() -> str:
            return os.path.basename(project_dir)

        self.EXEC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.PROJ_PATH = os.path.abspath(project_dir)
        Config.EXEC_ROOT = self.EXEC_PATH
        Config.PROJ_ROOT = self.PROJ_PATH
        
        # Only initialize settings if setting.toml doesn't exist
        setting_file = f"{self.PROJ_PATH}/setting.toml"
        if not os.path.isfile(setting_file):
            Setting.name = get_default_proj_name() if proj_name == "" else proj_name
            # Only get R path when actually needed (lazy initialization)
            Setting.r_path = r_path if r_path else ""
            Setting.version = "0.01"
            Setting.wait_time = 4
            # Initialize execution settings with defaults
            Setting.system = "multithreading"
            Setting.nthread = 1
            Setting.pbs_server = ""
            Setting.flush()
        with open(f"{self.PROJ_PATH}/setting.toml", encoding="utf-8") as f:
            setting = toml.load(f)
            Setting.name = setting["project"]["name"]
            Setting.r_path = setting["R"]["r_path"]
            Setting.version = setting["project"]["version"]
            Setting.wait_time = setting["fetch"]["wait_time"]
            # Load execution settings
            execution_settings = setting.get("execution", {})
            Setting.system = execution_settings.get("system", "multithreading")
            Setting.nthread = execution_settings.get("nthread", 1)
            Setting.pbs_server = execution_settings.get("pbs_server", "")
            
        # Apply configuration settings automatically
        self._apply_config_settings()

    def _apply_config_settings(self):
        """Apply configuration settings from setting.toml"""
        # Apply system configuration
        if Setting.system == "PBS":
            if Setting.pbs_server:
                self.usePBS(Setting.pbs_server)
            else:
                print("Warning: PBS system selected but no PBS server configured")
                self.useMultiThreading()
        else:  # Default to multithreading
            self.useMultiThreading()
        
        # Apply thread configuration
        if Setting.nthread > 1:
            self.parallelize(Setting.nthread)
        else:
            self.singularize()

    @property
    def nthread(self) -> int:
        return ThreadObservable.njobs

    def call(self, func: CellineFunction, wait_for_complete=True):
        """#### Call celline function"""
        func.call(self)
        ThreadObservable.wait_for_complete = wait_for_complete
        if wait_for_complete:
            ThreadObservable.watch()
        return self

    def call_if_else(
        self,
        condition: Callable[[Project], bool],
        true: CellineFunction,
        false: CellineFunction,
    ):
        """Call function if"""
        if condition(self):
            true.call(self)
        else:
            false.call(self)
        return self

    def parallelize(self, njobs: int):
        """#### Starts parallel computation\n
        @ njobs<int>: Number of jobs
        """
        ThreadObservable.set_jobs(njobs)
        return self

    def singularize(self):
        """#### End pararel computation"""
        ThreadObservable.set_jobs(1)
        return self

    def start_logging(self):
        return self

    def end_logging(self):
        return self

    def if_else(
        self,
        condition: Callable[[Project], bool],
        true: Callable[[Project], None],
        false: Callable[[Project], None],
    ):
        if condition(self):
            true(self)
        else:
            false(self)
        return self

    def usePBS(self, cluster_server_name: str):
        """#### Use PBS system."""
        print(f"--: Use PBS system: {cluster_server_name}")
        ServerSystem.usePBS(cluster_server_name)
        return self

    def useMultiThreading(self):
        """#### Use mutithreading system."""
        print("--: Use default multi threading")
        ServerSystem.useMultiThreading()
        return self

    def seurat(
        self,
        project_id: str,
        sample_id: str,
        identifier: str = "seurat.seurat",
        via_seurat_disk: bool = False,
    ):
        path = Path(project_id, sample_id)
        seurat_path = f"{path.data_sample}/{identifier}"
        bcmatrix_path = f"{path.resources_sample_counted}/outs/filtered_feature_bc_matrix.h5"
        if not os.path.isfile(seurat_path) and os.path.isfile(bcmatrix_path):
            return self.create_seurat(project_id, sample_id)
        return self.seurat_from_rawpath(seurat_path, via_seurat_disk)

    def seurat_from_rawpath(self, raw_path: str, via_seurat_disk: bool = True):
        return Seurat(raw_path, via_seurat_disk)

    def create_seurat(self, project_id: str, sample_id: str):
        identifier: str = "seurat.seurat"
        path = Path(project_id, sample_id)
        seurat_path = f"{path.data_sample}/{identifier}"
        
        # Lazy import pyper only when needed
        import pyper as pr
        r: pr.R = pr.R(RCMD=Setting.r_path, use_pandas=True)
        r.assign(
            "h5_path",
            f"{path.resources_sample_counted}/outs/filtered_feature_bc_matrix.h5",
        )
        r.assign("h5seurat_path", f"{seurat_path}")
        r.assign("proj", Setting.name)
        print("Loading raw matrix")
        result = r(
            """
pacman::p_load(Seurat, SeuratDisk, tidyverse)
raw <-
    Read10X_h5(h5_path) %>%
    CreateSeuratObject(proj) %>%
    NormalizeData() %>%
    FindVariableFeatures() %>%
    ScaleData()
raw %>%
    RunPCA(features = VariableFeatures(object = raw)) %>%
    FindNeighbors(dims = 1:20) %>%
    FindClusters(dims = 1:20) %>%
    RunUMAP(dims = 1:20) %>%
    saveRDS(h5seurat_path)
""",
        )
        print(
            f"""
Done.
---- Trace --------------
{result}
""",
        )
        return Seurat(seurat_path, False)
