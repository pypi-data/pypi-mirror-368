# Orgo SDK

Desktop infrastructure for AI agents.

## Install

```bash
pip install orgo
```

## Usage

```python
from orgo import Computer

# Create computer
computer = Computer()

# Control
computer.left_click(100, 200)
computer.type("Hello world")
computer.key("Enter")
computer.screenshot()  # Returns PIL Image

# Execute Python code
computer.exec("import pyautogui; pyautogui.click(512, 384)")

# Cleanup
computer.shutdown()
```

Full documentation: [docs.orgo.ai](https://docs.orgo.ai)