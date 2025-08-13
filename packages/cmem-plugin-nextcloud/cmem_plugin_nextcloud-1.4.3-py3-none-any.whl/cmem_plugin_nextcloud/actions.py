"""Plugin actions"""

from nc_py_api import Nextcloud

from cmem_plugin_nextcloud.retrieval import NextcloudRetrieval


class ResultPreview:
    """Class for preview action in Nextcloud plugins"""

    def __init__(  # noqa: PLR0913
        self,
        nc: Nextcloud,
        path: str,
        file_expression: str,
        no_subfolder: bool,
        error_on_empty_result: bool,
        only_files: bool,
    ):
        self.nc = nc
        self.path = path
        self.file_expression = file_expression
        self.no_subfolder = no_subfolder
        self.error_on_empty_result = error_on_empty_result
        self.only_files = only_files

    def result_preview(self) -> str:
        """Plugin Action to preview the results"""
        files = []
        ncr = NextcloudRetrieval(
            nc=self.nc,
            error_on_empty_result=self.error_on_empty_result,
            file_expression=self.file_expression,
        )
        if self.file_expression == "":
            if self.no_subfolder:
                files = ncr.listdir_parallel(
                    files=[], directory=self.path, context=None, depth=1, no_of_max_hits=10
                )
            else:
                files = ncr.listdir_parallel(
                    files=[], directory=self.path, context=None, no_of_max_hits=10
                )
        elif self.no_subfolder:
            files = ncr.listdir_parallel(
                files=[], directory=self.path, context=None, depth=1, no_of_max_hits=10
            )
        else:
            files = ncr.listdir_parallel(
                files=[], directory=self.path, context=None, depth=-1, no_of_max_hits=10
            )
        if len(files) == 0:
            raise ValueError("No results found with the given instructions.")
        output = [f"The Following {len(files)} entities were found:", ""]
        output.extend(f"- {file.user_path}" for file in files)
        output.append(
            "\nNote: The preview results may appear out of order due to the parallel traversal of "
            "the file system."
        )
        return "\n".join(output)
