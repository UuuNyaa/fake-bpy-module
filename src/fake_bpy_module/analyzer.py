import re
from typing import List
from docutils import nodes
from docutils.core import publish_doctree

from .docutils_based.transformer import transformer

from .common import (
    SectionInfo,
)
from .docutils_based import analyzer, compat, configuration


REGEX_SUB_LINE_SPACES = re.compile(r"\s+")


# pylint: disable=R0903
class AnalysisResult:
    def __init__(self):
        self.section_info: List['SectionInfo'] = []


class BaseAnalyzer:
    def __init__(self, mod_files: List[str]):
        analyzer.directives.register_directives()
        analyzer.roles.register_roles()

        self.target: str = None         # "blender" or "upbge"
        self.target_version: str = None    # Ex: "2.80"
        self.mod_files: List[str] = mod_files
        self.mod_documents: List[nodes.document] = []

    def set_target_version(self, version: str):
        self.target_version = version

    def set_target(self, target: str):
        self.target = target

    def _target(self) -> str:
        return self.target

    def _modify(self, doc_list: List[nodes.document]) -> AnalysisResult:
        result = AnalysisResult()

        for doc in doc_list:
            section_info: SectionInfo = SectionInfo()
            writer = compat.FakeBpyModuleImmWriter(
                doc, section_info)
            writer.translate()

            result.section_info.append(section_info)

        return result

    def apply_transform(self, doc_list: List[nodes.document]) -> List[nodes.document]:
        t = transformer.Transformer([
            "rst_specific_node_cleaner",
            "base_class_fixture",
            "module_level_attribute_fixture",
            "bpy_app_handlers_data_type_adder",
            "bpy_ops_override_parameters_adder",
            "bpy_types_class_baseclass_rebaser",
            "bpy_context_variable_converter",
            "mod_applier",
            "format_validator"
        ], {
            "mod_applier": {
                "mod_files": self.mod_files
            }
        })
        t.transform(doc_list)

        return doc_list

    def _analyze_by_file(self, filename: str) -> nodes.document:
        with open(filename, "r", encoding="utf-8") as f:
            contents = f.read()

        configuration.set_target(self.target)
        configuration.set_target_version(self.target_version)

        settings_overrides = {
            "exit_status_level": 2,
            "halt_level": 2,
            "line_length_limit": 20000,
        }
        document: nodes.document = publish_doctree(
            contents, settings_overrides=settings_overrides,
            reader=analyzer.readers.BpyRstDocsReader())

        return document

    def analyze_internal(self, filenames: list) -> List[nodes.document]:
        files_to_exclude = []

        documents: List[nodes.document] = []
        for f in filenames:
            exclude = False
            for ex in files_to_exclude:
                if f.endswith(ex):
                    exclude = True
                    break
            if exclude:
                continue

            document = self._analyze_by_file(f)
            documents.append(document)

        return documents

    def analyze(self, filenames: list) -> AnalysisResult:
        documents = self.analyze_internal(filenames)
        documents = self.apply_transform(documents)
        result = self._modify(documents)

        return result
