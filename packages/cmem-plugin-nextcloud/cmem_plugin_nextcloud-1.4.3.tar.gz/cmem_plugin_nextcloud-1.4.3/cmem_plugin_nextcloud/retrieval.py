"""Retrieval for nodes in Nextcloud instance"""

import fnmatch
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from nc_py_api import FsNode, Nextcloud


def context_report(context: ExecutionContext, files: list[FsNode]) -> None:
    """Report for user context"""
    if context is not None:
        context.report.update(
            ExecutionReport(
                entity_count=len(files), operation="wait", operation_desc="files listed"
            )
        )


class NextcloudRetrieval:
    """Retrieval class for Nextcloud folders and files"""

    def __init__(self, nc: Nextcloud, file_expression: str, error_on_empty_result: bool):
        self.nc = nc
        self.file_expression = file_expression
        self.error_on_empty_result = error_on_empty_result
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def listdir_parallel(  # noqa: PLR0913
        self,
        files: list[FsNode],
        context: ExecutionContext | None,
        directory: str = "",
        depth: int = -1,
        curr_depth: int = 0,
        no_of_max_hits: int = -1,
    ) -> list[FsNode]:
        """List directories/files from Nextcloud, recursing in parallel."""
        if curr_depth == 0:
            self.stop_event.clear()
        self.cancel_listdir(context)
        if self.stop_event.is_set() or (depth != -1 and curr_depth >= depth):
            return files

        nodes = self.nc.files.listdir(directory, depth=1)
        subdirectories: list[str] = []

        for node in nodes:
            self.cancel_listdir(context)
            if self.stop_event.is_set():
                return files

            added = self.add_node(files, node, no_of_max_hits)
            context_report(context, files)

            if added and self.check_stop(files, no_of_max_hits):
                return files

            if node.is_dir:
                subdirectories.append(node.user_path)

        if not self.stop_event.is_set() and subdirectories:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self.listdir_parallel,
                        files,
                        None,
                        sd,
                        depth,
                        curr_depth + 1,
                        no_of_max_hits,
                    )
                    for sd in subdirectories
                    if not self.stop_event.is_set()
                ]
                for fut in as_completed(futures):
                    self.cancel_listdir(context)
                    if self.stop_event.is_set():
                        break
                    fut.result()
                    context_report(context, files)

        context_report(context, files)

        self.raise_empty_error(files)

        return files

    def cancel_listdir(self, context: ExecutionContext) -> None:
        """Cancel listdir if workflow is cancelled"""
        try:
            if context.workflow.status() == "Canceling":
                self.stop_event.set()
        except AttributeError:
            pass

    def raise_empty_error(self, files: list[FsNode]) -> None:
        """Raise error if flag is set and no files were found"""
        if self.error_on_empty_result and not files:
            raise ValueError("Results are empty!")

    def add_node(self, files: list[FsNode], node: FsNode, no_of_max_hits: int) -> bool:
        """Add file or folder node to result"""
        with self.lock:
            if no_of_max_hits != -1 and len(files) >= no_of_max_hits:
                self.stop_event.set()
                return False

            if (
                self.file_expression != "" and fnmatch.fnmatch(node.name, self.file_expression)
            ) and not node.is_dir:
                files.append(node)
                if no_of_max_hits != -1 and len(files) >= no_of_max_hits:
                    self.stop_event.set()
                return True

            if self.file_expression == "":
                files.append(node)
                if no_of_max_hits != -1 and len(files) >= no_of_max_hits:
                    self.stop_event.set()
                return True

        return False

    def check_stop(self, files: list[FsNode], max_results: int) -> bool:
        """Check whether max_results reached and stop if so"""
        with self.lock:
            if max_results != -1 and len(files) >= max_results:
                self.stop_event.set()
                return True
        return False
