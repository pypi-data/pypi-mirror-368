import os.path
from typing import TYPE_CHECKING, Dict, Any, Optional, List

from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.common.command_request import CommandRequest
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
    from wexample_wex_core.common.execution_context import ExecutionContext


class AbstractEachPathMiddleware(AbstractMiddleware):
    recursive: bool = False
    should_exist: bool = False
    expand_glob: bool = False
    recursion_limit: int = 100

    def __init__(self, **kwargs):
        # Set default option if none provided
        if 'option' not in kwargs or not kwargs['option']:
            kwargs['option'] = self._get_default_option()

        kwargs['options'] = [
            kwargs['option']
        ]

        super().__init__(**kwargs)

    def _get_option_file_path(self, function_kwargs: "Kwargs") -> Optional[str]:
        option = self.get_first_option()
        return function_kwargs[option.name]

    def _get_default_option(self) -> Dict[str, Any]:
        from wexample_helpers.const.globals import PATH_NAME_PATH
        """Get the default path option definition."""
        return {
            "name": PATH_NAME_PATH,
            "type": str,
            "required": True,
            "description": "Path to local file or directory"
        }

    def validate_options(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> bool:
        if self.should_exist:
            import os.path
            from wexample_wex_core.exception.path_not_found_command_option_exception import \
                PathNotFoundCommandOptionException

            option = self.get_first_option()
            if option and option.name in function_kwargs:
                file_path = function_kwargs[option.name]
                if not os.path.exists(file_path):
                    raise PathNotFoundCommandOptionException(
                        option_name=option.name,
                        file_path=file_path
                    )

        return True

    def _should_process_item(self, request: "CommandRequest", item_path: str) -> bool:
        """
        Determine if an item should be processed based on its path.
        This method should be overridden by subclasses to implement specific filtering logic.
        
        Args:
            item_path: Path to the item to check
            
        Returns:
            True if the item should be processed, False otherwise
        """
        # Base implementation accepts all items
        return True

    def _should_explore_directory(self, request: "CommandRequest", directory_name: str) -> bool:
        """
        Determine if a directory should be explored during recursive traversal.
        This method can be overridden by subclasses to skip certain directories.
        
        Args:
            directory_name: Name of the directory to check (not the full path)
            
        Returns:
            True if the directory should be explored, False otherwise
        """
        # Base implementation explores all directories
        return True

    def _process_directory_recursively(
            self,
            request: "CommandRequest",
            directory_path: str,
            option_name: str,
            current_depth: int = 0) -> List[Dict]:
        """
        Process a directory recursively, collecting paths that match the criteria.
        
        Args:
            directory_path: Path to the directory to process
            option_name: Name of the option to set in function kwargs
            current_depth: Current recursion depth
            
        Returns:
            List of function kwargs dictionaries for each matching path
        """
        if current_depth > self.recursion_limit:
            return []  # Stop recursion if max depth is reached

        result = []

        try:
            # Iterate through all directory items
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)

                # Process items that match the subclass criteria
                if self._should_process_item(request=request, item_path=item_path):
                    # Create a copy of arguments for each matching item
                    result.append({option_name: item_path})

                # If recursive is enabled and item is a directory, check if we should explore it
                if self.recursive and os.path.isdir(item_path):
                    # Skip directories that shouldn't be explored
                    if not self._should_explore_directory(request=request, directory_name=item):
                        request.kernel.io.info(f'Skipping path that does not match middleware policy: {item_path}')
                        continue

                    subdirectory_results = self._process_directory_recursively(
                        request=request,
                        directory_path=item_path,
                        option_name=option_name,
                        current_depth=current_depth + 1
                    )
                    result.extend(subdirectory_results)
        except (PermissionError, FileNotFoundError) as e:
            # Skip directories we can't access
            pass

        return result

    def build_execution_contexts(
            self,
            command_wrapper: "CommandMethodWrapper",
            request: "CommandRequest",
            function_kwargs: "Kwargs"
    ) -> List["ExecutionContext"]:
        # If glob expansion is enabled and the path is a directory,
        # create an execution for each matching item in that directory
        if self.expand_glob:
            from wexample_wex_core.common.execution_context import ExecutionContext

            path = self._get_option_file_path(function_kwargs=function_kwargs)

            # If the path is a directory, process it
            if os.path.isdir(path):
                passes = []
                option = self.get_first_option()

                # Process the directory (recursively if enabled)
                path_kwargs_list = self._process_directory_recursively(
                    request=request,
                    directory_path=path,
                    option_name=option.name
                )

                # Create execution passes by combining the original kwargs with each path
                for path_kwargs in path_kwargs_list:
                    kwargs_copy = function_kwargs.copy()
                    kwargs_copy.update(path_kwargs)

                    passes.append(
                        ExecutionContext(
                            middleware=self,
                            command_wrapper=command_wrapper,
                            request=request,
                            function_kwargs=kwargs_copy
                        )
                    )

                return passes

            # If the path is not a directory, continue normally
            # (validation will happen in validate_options)

        # If expand_glob is not enabled, use default behavior
        return super().build_execution_contexts(
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        )
