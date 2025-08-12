from typing import TYPE_CHECKING, Optional, Any, Dict

from wexample_prompt.common.error_context import ErrorContext

if TYPE_CHECKING:
    from wexample_prompt.responses.messages import ErrorPromptResponse


class ErrorPromptResponseManagerMixin:
    def error(
        self,
        message: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        exception: Optional[Any] = None,
        fatal: bool = False,
        format: bool = False,
        format_paths_map: Optional[dict] = None,
        **kwargs
    ) -> "ErrorPromptResponse":
        from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse

        context = ErrorContext(
            fatal=fatal,
            params=params,
            indentation=self.log_indent
        )
        response = ErrorPromptResponse.create_error(
            message=message,
            context=context,
            exception=exception,
            format=format,
            format_paths_map=format_paths_map,
            **kwargs
        )

        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.error(message, extra={"params": params} if params else None)

        self.print_response(response)

        # Only call _on_fatal() if fatal is True
        # if fatal:
        response._on_fatal()

        return response
