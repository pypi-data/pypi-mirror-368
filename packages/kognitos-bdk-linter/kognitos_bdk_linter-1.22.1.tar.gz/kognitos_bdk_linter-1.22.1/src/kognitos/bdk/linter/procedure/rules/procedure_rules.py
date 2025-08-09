from abc import ABC, abstractmethod

from astroid import FunctionDef
from pylint.lint import PyLinter

from kognitos.bdk.reflection import BookProcedureDescriptor


class ProcedureRule(ABC):
    @abstractmethod
    def check_rule(self, linter: PyLinter, book_procedure: BookProcedureDescriptor, node: FunctionDef) -> None:
        pass


class ProcedureExamplesRule(ProcedureRule):
    def check_rule(self, linter: PyLinter, book_procedure: BookProcedureDescriptor, node: FunctionDef):
        if not book_procedure.examples or len(book_procedure.examples) < 1:
            linter.add_message("procedure-missing-examples", args=node.repr_name(), node=node)
