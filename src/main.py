import asyncio
from typing import Callable, List
import re

# https://github.com/diff-match-patch-python/diff-match-patch
from diff_match_patch import diff_match_patch
import outlines
import os
import torch

# os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# https://tomassetti.me/ebnf/ Documentation for EBNF

# models live at ~/.cache/huggingface/hub

# base_model = "unsloth/Llama-3.2-1B"
base_model = "unsloth/Llama-3.2-3B"
# base_model = "meta-llama/Llama-3.2-1B"
# base_model = "Llama-3.2-1B-Instruct"
# base_model = "unsloth/Llama-3.2-3B"
model = outlines.models.transformers(base_model, device="mps", model_kwargs={"torch_dtype": torch.float16})


def extract_unique_words(text: str) -> List[str]:
    """
    Extract a sorted list of unique words from the input text,
    excluding filler words like 'um' and 'uh'.
    """
    # Remove punctuation and tokenize words
    words = re.findall(r"\b\w+\b", text)

    # Define filler words to exclude (in lowercase)
    filler_words = {"um", "uh", "umm", "ummm", "uhh", "uhhh"}

    # Exclude filler words and get unique words
    unique_words = sorted({word for word in words if word.lower() not in filler_words})

    return unique_words


def create_markdown_regex(words: List[str]) -> str:
    """
    Create a regex pattern for Markdown, limiting the vocabulary
    to the provided list of words.
    """
    # Escape and sort words to prioritize longer matches and avoid partial matches
    sorted_words = sorted(set(words), key=lambda x: -len(x))
    word_pattern = "|".join(re.escape(word) for word in sorted_words)

    # Define the content pattern: words separated by spaces
    content_pattern = rf"(?:{word_pattern})(?:\s+(?:{word_pattern}))*"

    # Construct the regex patterns for different Markdown elements as a single-line string
    markdown_regex = (
        rf"(?P<h1>#\s+(?P<h1_content>{content_pattern}))|"
        rf"(?P<h2>##\s+(?P<h2_content>{content_pattern}))|"
        rf"(?P<h3>###\s+(?P<h3_content>{content_pattern}))|"
        rf"(?P<bullet>-\s+(?P<bullet_content>{content_pattern}))|"
        rf"(?P<paragraph>(?P<paragraph_content>{content_pattern}))"
    )

    try:
        compiled_regex = re.compile(
            markdown_regex, re.MULTILINE | re.IGNORECASE
        )
        print("Compiled Regex Pattern:\n", compiled_regex.pattern)
        return compiled_regex.pattern
    except re.error as e:
        print(f"Regex compilation error: {e}")
        raise


def create_markdown_regex_smol(words: List[str]) -> str:
    """
    Create a simplified regex pattern that matches strings composed exclusively
    of the provided words, allowing for spaces and newlines between them.
    """
    # Sort words by length in descending order to prioritize longer matches
    sorted_words = sorted(set(words), key=lambda x: -len(x))
    
    # Escape special regex characters in words
    escaped_words = [re.escape(word) for word in sorted_words]
    
    # Join words into an alternation group
    word_pattern = "|".join(escaped_words)
    
    
    # Define the regex pattern:
    # ^(?:wordword2|word3)(?:\s+(?:word1|word2|word3))*$
    # This matches a string that starts and ends with the allowed words,
    # separated by one or more whitespace characters (spaces, tabs, newlines)
    regex_pattern = rf"(?:\s*({word_pattern})\s*)*"
    
    try:
        # Compile the regex pattern
        compiled_regex = re.compile(regex_pattern, re.IGNORECASE)
        print("Compiled Regex Pattern:\n", compiled_regex.pattern)
        return regex_pattern
    except re.error as e:
        print(f"Regex compilation error: {e}")
        raise

def create_markdown_grammar(words: List[str]) -> str:
    """
    Create a CFG in EBNF syntax for Markdown, limiting the vocabulary
    to the provided list of words.
    """
    # Create a regex pattern that matches any of the words
    word_pattern = "|".join(re.escape(word) for word in sorted(set(words)) if word.isalpha())
    regex_pattern = rf"(?:\s*({word_pattern})\s*)*"
    regex_pattern_simple = f"/{word_pattern}/i"

    # Define the WORD token using the regex pattern
    markdown_grammar = f"""
    %import common.NEWLINE
    %import common.WS_INLINE
    %ignore WS_INLINE

    ?start: block+

    ?block: heading
        | bullet_list
        | paragraph

    heading: h1_heading | h2_heading | h3_heading

    h1_heading: "#" line NEWLINE
    h2_heading: "##" line NEWLINE
    h3_heading: "###" line NEWLINE

    bullet_list: bullet_item+

    bullet_item: "- " line NEWLINE

    paragraph: line (NEWLINE line)*

    line: inline_element+

    ?inline_element: WORD
                    | PUNCTUATION
                    | emphasis
                    | strong
                    | code

    emphasis: "*" inline_element+ "*"
    strong: "**" inline_element+ "**"
    code: "`" inline_element+ "`"

    WORD: {regex_pattern_simple}
    PUNCTUATION: ":" | "," | "." | "!" | "?"
    """
    print(markdown_grammar)
    return markdown_grammar


async def outlines_formatter(text: str) -> str:
    """
    Format the input text into well-structured Markdown,
    using only words from the original text.
    """
    unique_words = extract_unique_words(text)
    markdown_grammar = create_markdown_grammar(unique_words)
    generator = outlines.generate.cfg(model, markdown_grammar)
    # regex attempt
    # markdown_regex = create_markdown_regex_smol(unique_words)
    # generator = outlines.generate.regex(model, markdown_regex)

    prompt = f"""
     Take the input text and format it into well-structured Markdown.
     - This means adding headings, paragraphs, bullet points, etc., and removing small inconsistencies like "um" and "uh".
     - Only minor cleanups and structuring, including capitalization.
     - Do not alter the words used; only use the words present in the original text.
     - Ensure that you make use of all the words available to create a coherent structure.

     Input text:
     {text}

     Generate text output only.
     """
    # Estimate the number of tokens in the text
    print(text)
    token_count = len(text)
    formatted_text = generator(prompt, max_tokens=token_count * 5)
    print(f"formatted_text: {formatted_text}-end")
    return formatted_text


differ = diff_match_patch()


class FormattingTask:
    def __init__(self, text, formatter):
        self.text = text
        self.formatter = formatter
        self.result = None

    async def execute(self):
        result = self.formatter(self.text)
        if asyncio.iscoroutine(result):
            self.result = await result
        else:
            self.result = result


class FormattingQueue:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    async def process_queue(self):
        for task in self.tasks:
            await task.execute()


async def get_selected_text() -> str:
    """
    Use AppleScript to get the selected text from the active application.
    Returns:
        str: The selected text
    """
    apple_script = """
    tell application "System Events"
        keystroke "c" using command down
    end tell
    delay 0.1
    return the clipboard
    """
    proc = await asyncio.create_subprocess_exec(
        "osascript",
        "-e",
        apple_script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode().strip()


async def replace_selected_text(new_text: str) -> None:
    """
    Use AppleScript to replace the selected text in the active application.
    Args:
        new_text (str): The text to replace the selection with
    """
    apple_script = f"""
    set the clipboard to "{new_text}"
    tell application "System Events"
        keystroke "v" using command down
    end tell
    """
    await asyncio.create_subprocess_exec("osascript", "-e", apple_script)


def generate_diff(original: str, formatted: str) -> str:
    """
    Generate a unified diff between the original and formatted text.
    Args:
        original (str): The original text
        formatted (str): The formatted text
    Returns:
        str: A unified diff representation
    """
    patches = differ.patch_make(original, formatted)
    diff = differ.patch_toText(patches)
    print("diff", diff)
    return diff


def apply_diff(original: str, diff: str) -> str:
    """
    Apply a unified diff to the original text to produce the formatted text.
    Args:
        original (str): The original text
        diff (str): The unified diff to apply
    Returns:
        str: The formatted text
    """
    # Create a PatchSet object from the diff string
    patches = differ.patch_fromText(diff)
    new_text, _ = differ.patch_apply(patches, original)

    # Join the lines back into a single string
    return new_text


async def format_text(text: str, formatter: Callable[[str], str]) -> str:
    """
    Apply the formatting function to the input text.
    Args:
        text (str): The input text to format
        formatter (Callable[[str], str]): The formatting function
    Returns:
        str: The formatted text
    """
    return await asyncio.to_thread(formatter, text)


async def main():
    formatting_queue = FormattingQueue()
    selected_text = await get_selected_text()
    task = FormattingTask(selected_text, outlines_formatter)
    formatting_queue.add_task(task)
    await formatting_queue.process_queue()
    formatted_text = task.result
    diff = generate_diff(selected_text, formatted_text)
    final_text = apply_diff(selected_text, diff)
    await replace_selected_text(final_text)


if __name__ == "__main__":
    asyncio.run(main())
