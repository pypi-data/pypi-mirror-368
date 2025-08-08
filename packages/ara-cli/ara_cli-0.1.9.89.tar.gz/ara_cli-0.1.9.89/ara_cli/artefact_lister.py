from ara_cli.file_classifier import FileClassifier
from ara_cli.artefact_reader import ArtefactReader
from ara_cli.file_lister import list_files_in_directory
from ara_cli.artefact_models.artefact_model import Artefact
from ara_cli.list_filter import ListFilter, filter_list
from ara_cli.artefact_fuzzy_search import suggest_close_name_matches
import os


class ArtefactLister:
    def __init__(self, file_system=None):
        self.file_system = file_system or os

    @staticmethod
    def artefact_content_retrieval(artefact: Artefact):
        content = artefact.serialize()
        return content

    @staticmethod
    def artefact_path_retrieval(artefact: Artefact):
        return artefact.file_path

    @staticmethod
    def artefact_tags_retrieval(artefact: Artefact):
        final_tags = []

        if not artefact:
            return []

        final_tags.extend([f"user_{user}" for user in artefact.users])
        final_tags.append(artefact.status)
        final_tags.extend(artefact.tags)

        return final_tags

    def filter_artefacts(self, classified_files: list, list_filter: ListFilter):
        filtered_list = filter_list(
            list_to_filter=classified_files,
            list_filter=list_filter,
            content_retrieval_strategy=ArtefactLister.artefact_content_retrieval,
            file_path_retrieval=ArtefactLister.artefact_path_retrieval,
            tag_retrieval=ArtefactLister.artefact_tags_retrieval
        )
        return filtered_list

    def list_files(
        self,
        tags=None,
        navigate_to_target=False,
        list_filter: ListFilter | None = None
    ):
        artefact_list = ArtefactReader.read_artefacts(tags=tags)
        artefact_list = self.filter_artefacts(artefact_list, list_filter)

        filtered_artefact_list = {
            key: [artefact for artefact in value if artefact is not None]
            for key, value in artefact_list.items()
        }
        file_classifier = FileClassifier(self.file_system)
        file_classifier.print_classified_files(filtered_artefact_list)

    def list_branch(
        self,
        classifier,
        artefact_name,
        list_filter: ListFilter | None = None
    ):
        file_classifier = FileClassifier(os)
        classified_artefacts = file_classifier.classify_files()
        artefact_info = classified_artefacts.get(classifier, [])
        matching_artefact_info = [p for p in artefact_info if p["title"] == artefact_name]

        if not matching_artefact_info:
            suggest_close_name_matches(
                artefact_name,
                [info["title"] for info in artefact_info]
            )

        artefacts_by_classifier = {classifier: []}
        ArtefactReader.step_through_value_chain(
            artefact_name=artefact_name,
            classifier=classifier,
            artefacts_by_classifier=artefacts_by_classifier,
        )
        artefacts_by_classifier = self.filter_artefacts(artefacts_by_classifier, list_filter)
        file_classifier.print_classified_files(artefacts_by_classifier)

    def list_children(
        self,
        classifier,
        artefact_name,
        list_filter: ListFilter | None = None
    ):
        file_classifier = FileClassifier(os)
        classified_artefacts = file_classifier.classify_files()
        artefact_info = classified_artefacts.get(classifier, [])
        matching_artefact_info = [p for p in artefact_info if p["title"] == artefact_name]

        if not matching_artefact_info:
            suggest_close_name_matches(
                artefact_name,
                [info["title"] for info in artefact_info]
            )

        child_artefacts = ArtefactReader.find_children(
            artefact_name=artefact_name,
            classifier=classifier
        )

        child_artefacts = self.filter_artefacts(child_artefacts, list_filter)

        file_classifier.print_classified_files(child_artefacts)

    def list_data(
        self,
        classifier,
        artefact_name,
        list_filter: ListFilter | None = None
    ):
        file_classifier = FileClassifier(os)
        classified_artefact_info = file_classifier.classify_files()
        artefact_info_dict = classified_artefact_info.get(classifier, [])

        matching_info = [info for info in artefact_info_dict if info["title"] == artefact_name]

        if not matching_info:
            suggest_close_name_matches(
                artefact_name,
                [info["title"] for info in artefact_info_dict]
            )
            return

        artefact_info = matching_info[0]
        data_dir = os.path.splitext(artefact_info["file_path"])[0] + '.data'
        if os.path.exists(data_dir):
            list_files_in_directory(data_dir, list_filter)
