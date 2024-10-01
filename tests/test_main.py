import pytest
from lark import Lark
from unittest.mock import patch, AsyncMock, ANY
import asyncio
from src.main import (
    FormattingTask,
    FormattingQueue,
    get_selected_text,
    replace_selected_text,
    generate_diff,
    apply_diff,
    format_text,
    main,
    outlines_formatter,
    create_markdown_grammar,
    extract_unique_words,
)

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def formatting_queue():
    return FormattingQueue()

@pytest.fixture
def grammar():
    test_input = "hello world"
    return create_markdown_grammar(extract_unique_words(test_input))
@pytest.fixture
def sample_text():
    return "hello world"

@pytest.fixture
def sample_formatter():
    return lambda x: x.upper()

# def test_formatting_task():
#     task = FormattingTask("test", str.upper)
#     assert task.text == "test"
#     assert task.formatter("test") == "TEST"
#     assert task.result is None

# @pytest.mark.asyncio
# async def test_formatting_queue(formatting_queue, sample_text, sample_formatter):
#     task = FormattingTask(sample_text, sample_formatter)
#     formatting_queue.add_task(task)
#     await formatting_queue.process_queue()
#     assert task.result == "HELLO WORLD"

# @pytest.mark.asyncio
# async def test_get_selected_text():
#     with patch('asyncio.create_subprocess_exec') as mock_exec:
#         # Create a mock process
#         mock_process = AsyncMock()
        
#         # Set up the communicate method to return a coroutine that returns the desired tuple
#         async def mock_communicate():
#             return (b"Selected Text", b"")
        
#         mock_process.communicate = mock_communicate
        
#         mock_exec.return_value = mock_process
        
#         result = await get_selected_text()
#         assert result == "Selected Text"

#         # Verify that the correct command was called
#         mock_exec.assert_called_once_with(
#             'osascript', '-e', ANY,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )
# @pytest.mark.asyncio
# async def test_replace_selected_text():
#     with patch('asyncio.create_subprocess_exec') as mock_exec:
#         await replace_selected_text("New Text")
#         mock_exec.assert_called_once()

# def test_generate_diff():
#     original = "hello\nworld"
#     formatted = "HELLO\nWORLD"
#     diff = generate_diff(original, formatted)
#     assert "-hello" in diff
#     assert "+HELLO" in diff

# def test_grammar(grammar: str):
#     test_input = "hello world"
#     parser = Lark(grammar, parser='earley')
#     parse_tree = parser.parse(test_input)
#     print("Parsing succeeded.")
#     print(parse_tree.pretty())
        
# def test_apply_diff():
#     original = "hello\nworld"
#     formatted = "HELLO\nworld"
#     diff = generate_diff(original, formatted)
#     assert diff is not None
#     result = apply_diff(original, diff)
#     assert result == "HELLO\nworld"

@pytest.mark.asyncio
async def test_black_box_formatter():
    result = await outlines_formatter("hello world, testing 1, 2, 3. ummm ok.")
    assert result is not None
    print(result)
    assert result.startswith("hello world")

# @pytest.mark.asyncio
# async def test_format_text(sample_text, sample_formatter):
#     result = await format_text(sample_text, sample_formatter)
#     assert result == "HELLO WORLD"

# @pytest.mark.asyncio
# async def test_main():
#     with patch('src.main.get_selected_text', new_callable=AsyncMock) as mock_get_text, \
#          patch('src.main.replace_selected_text', new_callable=AsyncMock) as mock_replace_text, \
#          patch('src.main.outlines_formatter', new_callable=AsyncMock) as mock_formatter:
        
#         # Mock return values
#         mock_get_text.return_value = "test text, turn into bullet points: 1. a, 2. b 3. c."
#         mock_formatter.return_value = "- Test text\n- Turn into bullet points:\n  - a\n  - b\n  - c"

#         # Execute the main function
#         await main()

#         # Assertions to ensure functions were called correctly
#         mock_get_text.assert_awaited_once()
#         mock_formatter.assert_awaited_once_with("test text, turn into bullet points: 1. a, 2. b 3. c.")
#         mock_replace_text.assert_awaited_once_with("- Test text\n- Turn into bullet points:\n  - a\n  - b\n  - c")
