import pytest
import os
import shutil
import base64
from unittest.mock import patch, MagicMock, mock_open, call
from pathlib import Path

from ara_cli import prompt_handler
from ara_cli.ara_config import ARAconfig, LLMConfigItem

@pytest.fixture
def mock_config():
    """Mocks a standard ARAconfig object for testing."""
    config = ARAconfig(
        ext_code_dirs=[{"source_dir": "./src"}],
        glossary_dir="./glossary",
        doc_dir="./docs",
        local_prompt_templates_dir="./ara/.araconfig",
        custom_prompt_templates_subdir="custom-prompt-modules",
        ara_prompt_given_list_includes=["*.py"],
        llm_config={
            "gpt-4o": LLMConfigItem(provider="openai", model="openai/gpt-4o", temperature=0.8, max_tokens=1024, max_completion_tokens= None),
            "o3-mini": LLMConfigItem(provider="openai", model="openai/o3-mini", temperature=0.9, max_tokens=2048, max_completion_tokens= None),
        },
        default_llm="gpt-4o"
    )
    return config

@pytest.fixture
def mock_config_manager(mock_config):
    """Patches ConfigManager to ensure it always returns the mock_config."""
    with patch('ara_cli.ara_config.ConfigManager.get_config') as mock_get_config:
        mock_get_config.return_value = mock_config
        yield mock_get_config

@pytest.fixture(autouse=True)
def reset_singleton():
    """Resets the LLMSingleton before each test for isolation."""
    prompt_handler.LLMSingleton._instance = None
    prompt_handler.LLMSingleton._model = None
    yield

class TestLLMSingleton:
    """Tests the behavior of the LLMSingleton class."""

    def test_get_instance_creates_with_default_model(self, mock_config_manager):
        instance = prompt_handler.LLMSingleton.get_instance()
        assert instance is not None
        assert prompt_handler.LLMSingleton.get_model() == "gpt-4o"
        assert instance.config_parameters['temperature'] == 0.8

    def test_get_instance_creates_with_first_model_if_no_default(self, mock_config_manager, mock_config):
        mock_config.default_llm = None
        instance = prompt_handler.LLMSingleton.get_instance()
        assert instance is not None
        assert prompt_handler.LLMSingleton.get_model() == "gpt-4o"

    def test_get_instance_returns_same_instance(self, mock_config_manager):
        instance1 = prompt_handler.LLMSingleton.get_instance()
        instance2 = prompt_handler.LLMSingleton.get_instance()
        assert instance1 is instance2

    def test_set_model_switches_model(self, mock_config_manager):
        initial_instance = prompt_handler.LLMSingleton.get_instance()
        assert prompt_handler.LLMSingleton.get_model() == "gpt-4o"
        
        with patch('builtins.print') as mock_print:
            new_instance = prompt_handler.LLMSingleton.set_model("o3-mini")
            mock_print.assert_called_with("Language model switched to 'o3-mini'")

        assert prompt_handler.LLMSingleton.get_model() == "o3-mini"
        assert new_instance.config_parameters['temperature'] == 0.9
        assert initial_instance is not new_instance

    def test_set_model_to_invalid_raises_error(self, mock_config_manager):
        with pytest.raises(ValueError, match="No configuration found for the model: invalid-model"):
            prompt_handler.LLMSingleton.set_model("invalid-model")

    def test_get_model_initializes_if_needed(self, mock_config_manager):
        assert prompt_handler.LLMSingleton._instance is None
        model = prompt_handler.LLMSingleton.get_model()
        assert model == "gpt-4o"
        assert prompt_handler.LLMSingleton._instance is not None

class TestFileIO:
    """Tests file I/O helper functions."""

    def test_write_and_read_string_from_file(self, tmp_path):
        file_path = tmp_path / "test.txt"
        test_string = "Hello World"
        
        prompt_handler.write_string_to_file(file_path, test_string, 'w')
        
        content = prompt_handler.read_string_from_file(file_path)
        assert test_string in content
        
        content_get = prompt_handler.get_file_content(file_path)
        assert content == content_get


class TestCoreLogic:
    """Tests functions related to the main business logic."""

    @patch('ara_cli.prompt_handler.litellm.completion')
    @patch('ara_cli.prompt_handler.LLMSingleton.get_instance')
    def test_send_prompt(self, mock_get_instance, mock_completion, mock_config):
        mock_llm_instance = MagicMock()
        mock_llm_instance.config_parameters = mock_config.llm_config['gpt-4o'].model_dump()
        mock_get_instance.return_value = mock_llm_instance
        
        mock_chunk = MagicMock()
        mock_chunk.choices[0].delta.content = "test chunk"
        mock_completion.return_value = [mock_chunk]

        prompt = [{"role": "user", "content": "A test"}]
        
        result = list(prompt_handler.send_prompt(prompt))

        # Create expected parameters to match the actual implementation
        # The actual send_prompt function copies config_parameters and only removes 'provider'
        expected_params = mock_config.llm_config['gpt-4o'].model_dump()
        if 'provider' in expected_params:
            del expected_params['provider']

        mock_completion.assert_called_once_with(
            messages=prompt,
            stream=True,
            **expected_params
        )
        assert len(result) == 1
        assert result[0].choices[0].delta.content == "test chunk"

    @patch('ara_cli.prompt_handler.send_prompt')
    def test_describe_image(self, mock_send_prompt, tmp_path):
        fake_image_path = tmp_path / "test.png"
        fake_image_content = b"fakeimagedata"
        fake_image_path.write_bytes(fake_image_content)
        
        mock_send_prompt.return_value = iter([])
        
        prompt_handler.describe_image(fake_image_path)
        
        mock_send_prompt.assert_called_once()
        called_args = mock_send_prompt.call_args[0][0]
        
        assert len(called_args) == 1
        message_content = called_args[0]['content']
        assert isinstance(message_content, list)
        assert message_content[0]['type'] == 'text'
        assert message_content[1]['type'] == 'image_url'
        
        encoded_image = base64.b64encode(fake_image_content).decode('utf-8')
        expected_url = f"data:image/png;base64,{encoded_image}"
        assert message_content[1]['image_url']['url'] == expected_url

    @patch('ara_cli.prompt_handler.Classifier.get_sub_directory', return_value="test_classifier")
    def test_append_headings(self, mock_get_sub, tmp_path):
        os.chdir(tmp_path)
        os.makedirs("ara/test_classifier/my_param.data", exist_ok=True)
        
        log_file = tmp_path / "ara/test_classifier/my_param.data/test_classifier.prompt_log.md"
        
        prompt_handler.append_headings("test_classifier", "my_param", "PROMPT")
        assert "## PROMPT_1" in log_file.read_text()
        
        prompt_handler.append_headings("test_classifier", "my_param", "PROMPT")
        assert "## PROMPT_2" in log_file.read_text()
        
        prompt_handler.append_headings("test_classifier", "my_param", "RESULT")
        assert "## RESULT_1" in log_file.read_text()

class TestArtefactAndTemplateHandling:
    """Tests functions that manage artefact and template files."""

    @pytest.fixture(autouse=True)
    def setup_fs(self, tmp_path):
        self.root = tmp_path
        os.chdir(self.root)
        self.mock_classifier = "my_artefact"
        self.mock_param = "my_param"
        
        self.classifier_patch = patch('ara_cli.prompt_handler.Classifier.get_sub_directory', return_value=self.mock_classifier)
        self.mock_get_sub_dir = self.classifier_patch.start()
        
        yield
        
        self.classifier_patch.stop()

    def test_prompt_data_directory_creation(self):
        path = prompt_handler.prompt_data_directory_creation(self.mock_classifier, self.mock_param)
        expected_path = self.root / "ara" / self.mock_classifier / f"{self.mock_param}.data" / "prompt.data"
        assert os.path.exists(expected_path)
        assert Path(path).resolve() == expected_path.resolve()

    @patch('ara_cli.prompt_handler.generate_markdown_listing')
    def test_generate_config_prompt_givens_file(self, mock_generate_listing, mock_config_manager):
        prompt_data_path = prompt_handler.prompt_data_directory_creation(self.mock_classifier, self.mock_param)
        
        prompt_handler.generate_config_prompt_givens_file(prompt_data_path, "config.givens.md")
        
        mock_generate_listing.assert_called_once()
        args, _ = mock_generate_listing.call_args
        assert "ara" in args[0]
        assert "./src" in args[0]
        assert "./docs" in args[0]
        assert "./glossary" in args[0]
        assert args[1] == ["*.py"]
        assert args[2] == os.path.join(prompt_data_path, "config.givens.md")

    @patch('ara_cli.prompt_handler.generate_markdown_listing')
    def test_generate_config_prompt_givens_file_marks_artefact(self, mock_generate_listing, mock_config_manager):
        prompt_data_path = Path(prompt_handler.prompt_data_directory_creation(self.mock_classifier, self.mock_param))
        config_path = prompt_data_path / "config.givens.md"
        artefact_to_mark = "file.py"

        def create_fake_file(*args, **kwargs):
            content = f"- [] some_other_file.txt\n- [] {artefact_to_mark}\n"
            with open(args[2], 'w') as f:
                f.write(content)

        mock_generate_listing.side_effect = create_fake_file

        prompt_handler.generate_config_prompt_givens_file(
            str(prompt_data_path), "config.givens.md", artefact_to_mark=artefact_to_mark
        )
        
        content = config_path.read_text()
        assert f"- [x] {artefact_to_mark}" in content
        assert f"- [] some_other_file.txt" in content

    @patch('ara_cli.prompt_handler.extract_and_load_markdown_files')
    @patch('ara_cli.prompt_handler.move_and_copy_files')
    @patch('ara_cli.prompt_handler.TemplatePathManager.get_template_base_path', return_value="/global/templates")
    def test_load_selected_prompt_templates(self, mock_base_path, mock_move, mock_extract, mock_config_manager):
        prompt_data_path = prompt_handler.prompt_data_directory_creation(self.mock_classifier, self.mock_param)
        config_file = Path(prompt_data_path) / "config.prompt_templates.md"
        config_file.touch()

        mock_extract.return_value = [
            "custom-prompt-modules/my_custom.rules.md",
            "prompt-modules/global.intention.md",
            "unrecognized/file.md"
        ]
        
        prompt_handler.load_selected_prompt_templates(self.mock_classifier, self.mock_param)

        archive_path = os.path.join(prompt_data_path, "prompt.archive")

        assert mock_move.call_count == 2
        expected_calls = [
            call(
                os.path.join(mock_config_manager.return_value.local_prompt_templates_dir, "custom-prompt-modules/my_custom.rules.md"),
                prompt_data_path,
                archive_path
            ),
            call(
                os.path.join("/global/templates", "prompt-modules/global.intention.md"),
                prompt_data_path,
                archive_path
            )
        ]
        mock_move.assert_has_calls(expected_calls, any_order=True)

    def test_extract_and_load_markdown_files(self):
        md_content = """
# prompt-modules
## a-category
- [x] first.rules.md
- [] second.rules.md
# custom-prompt-modules
- [x] custom.intention.md
"""
        m = mock_open(read_data=md_content)
        with patch('builtins.open', m):
            paths = prompt_handler.extract_and_load_markdown_files("dummy_path")
        
        assert len(paths) == 2
        assert 'prompt-modules/a-category/first.rules.md' in paths
        assert 'custom-prompt-modules/custom.intention.md' in paths
    
    @patch('ara_cli.prompt_handler.send_prompt')
    @patch('ara_cli.prompt_handler.collect_file_content_by_extension')
    @patch('ara_cli.prompt_handler.append_images_to_message')
    def test_create_and_send_custom_prompt(self, mock_append_images, mock_collect, mock_send):
        prompt_data_path = Path(prompt_handler.prompt_data_directory_creation(self.mock_classifier, self.mock_param))

        mock_collect.return_value = ("### GIVENS\ncontent", [{"type": "image_url", "image_url": {}}])
        
        final_message_list = [{"role": "user", "content": [{"type": "text", "text": "### GIVENS\ncontent"}, {"type": "image_url", "image_url": {}}]}]
        mock_append_images.return_value = final_message_list

        mock_send.return_value = iter([MagicMock(choices=[MagicMock(delta=MagicMock(content="llm response"))])])

        prompt_handler.create_and_send_custom_prompt(self.mock_classifier, self.mock_param)
        
        mock_collect.assert_called_once()
        mock_append_images.assert_called_once()
        mock_send.assert_called_once_with(final_message_list)

        artefact_root = self.root / "ara" / self.mock_classifier
        log_file = artefact_root / f"{self.mock_param}.data" / f"{self.mock_classifier}.prompt_log.md"

        assert log_file.exists()
        log_content = log_file.read_text()
        assert "### GIVENS\ncontent" in log_content
        assert "llm response" in log_content