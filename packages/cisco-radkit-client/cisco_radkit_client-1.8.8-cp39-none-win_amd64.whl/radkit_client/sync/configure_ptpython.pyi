from collections.abc import Iterable
from dataclasses import dataclass
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from ptpython.repl import PythonRepl
from radkit_common.settings import Theme as Theme

__all__ = ['Theme', 'configure_ptpython']

def configure_ptpython(repl: PythonRepl, theme: Theme = ...) -> None: ...

@dataclass
class _CustomCompleter(Completer):
    ptpython_completer: Completer
    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]: ...
