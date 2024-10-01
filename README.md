# Llama Markdown Formatter

A simple tool to format text into well-structured Markdown using Llama 3.2.


Right now the outputs are completely insane, don't use it.

## Example
```
Input: hello world, testing 1, 2, 3. ummm ok.

Output         -       Hello,                                                          !       Hello,                                       !        Hello,                                                                                  !       Hello,                                       !        Hello,                                                                                  !       Hello,                                       !        Hello,                                                                                  !       Hello,                                       !        Hello,                                                                  !       Hello,                                                       !        Hello,                                                                                          !       Hello,          !       Hello,       !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello, -end
        -       Hello,                                                          !       Hello,                                                       !        Hello,                                                                                  !       Hello,                                       !        Hello,                                                                                  !       Hello,                                       !        Hello,                                                                                  !       Hello,                                       !        Hello,                                                                  !       Hello,                                                       !        Hello,                                                                                          !       Hello,          !       Hello,       !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello,                               !        Hello,                                                                                          !       Hello, 
```

What works is that it constrains the vocabulary, but the output is wrong.


## Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. To set up the project:

1. Install uv if you haven't already:
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a virtual environment and install dependencies:
   ```
   uv venv
   source .venv/bin/activate
   uv pip sync
   ```

3. Run the application:
   ```
   python src/main.py
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Build the project:
   ```
   uv build
   ```

## Development

- Use `uv add <package>` to add new dependencies
- Use `uv add --dev <package>` to add new development dependencies
- Run `black .` to format code
- Run `mypy .` for type checking

## License

This project is licensed under the MIT License.