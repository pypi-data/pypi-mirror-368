"""Autocomplete for paths"""

from typing import Any, ClassVar

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from nc_py_api import Nextcloud


class DirectoryParameterType(StringParameterType):
    """Nextcloud Search Type"""

    def __init__(
        self,
        url_expand: str,
        display_name: str,
    ) -> None:
        self.url_expand = url_expand
        self.display_name = display_name
        self.suggestions: list[Autocompletion] = []

    autocompletion_depends_on_parameters: ClassVar[list[str]] = [
        "base_url",
        "user",
        "token",
        "path",
    ]

    allow_only_autocompleted_values: bool = False
    autocomplete_value_with_labels: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocomplete"""
        _ = context

        selected_path = depend_on_parameter_values[3]
        entered_directory = "".join(query_terms)

        if selected_path == "":
            self.suggestions = self.suggest_base_directories(depend_on_parameter_values)
            return self.suggestions

        if selected_path != "" and entered_directory == "":
            return self.suggestions

        if entered_directory[-1] == "/":
            dataset = self.get_nextcloud_client(depend_on_parameter_values)
            folders = [
                i
                for i in dataset.files.listdir(path=selected_path, depth=1, exclude_self=False)
                if i.is_dir
            ]
            result = [
                Autocompletion(
                    value=folder.user_path,
                    label=folder.user_path,
                )
                for folder in folders
            ]

            child_folder = "/".join(selected_path.rstrip("/").split("/")[:-1])
            child_folder = f"{child_folder}/"
            result.append(Autocompletion(value=child_folder, label=child_folder))

            self.suggestions = result
            self.remove_non_matching_results(query_terms)

            for suggestion in self.suggestions:
                if suggestion.label == "/":
                    return self.suggestions
            self.suggestions.append(Autocompletion(value="", label="/"))

            return self.suggestions

        self.remove_non_matching_results(query_terms)
        self.sort_suggestions(query_terms)
        return self.suggestions

    def suggest_base_directories(
        self, depend_on_parameter_values: list[Any]
    ) -> list[Autocompletion]:
        """Initialise the root directory for browsing"""
        dataset = self.get_nextcloud_client(depend_on_parameter_values)
        folders = [i for i in dataset.files.listdir(depth=1, exclude_self=False) if i.is_dir]
        return [
            Autocompletion(
                value=folder.user_path,
                label=folder.user_path if folder.user_path != "" else "/",
            )
            for folder in folders
        ]

    def sort_suggestions(self, query_terms: list[str]) -> None:
        """Sort autocompleted suggestions"""
        self.suggestions.sort(
            key=lambda x: (
                not all(term.lower() in x.label.lower() for term in query_terms),
                x.label.lower(),
            )
        )

    def remove_non_matching_results(self, query_terms: list[str]) -> None:
        """Remove non-matching query terms from autocompletion"""
        self.suggestions = [
            x
            for x in self.suggestions
            if all(term.lower() in x.label.lower() for term in query_terms) or x.label.lower != "/"
        ]

    @staticmethod
    def get_nextcloud_client(depend_on_parameter_values: list[Any]) -> Nextcloud:
        """Initialise the Nextcloud dataset"""
        return Nextcloud(
            nextcloud_url=depend_on_parameter_values[0],
            nc_auth_user=depend_on_parameter_values[1],
            nc_auth_pass=depend_on_parameter_values[2]
            if isinstance(depend_on_parameter_values[2], str)
            else depend_on_parameter_values[2].decrypt(),
        )
