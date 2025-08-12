# Emailify

[![codecov](https://codecov.io/gh/choinhet/emailify/graph/badge.svg?token=${CODECOV_TOKEN})](https://codecov.io/gh/choinhet/emailify)

Create beautiful HTML emails with tables, text, charts and more. Built on MJML for consistent rendering across all email clients.

## Installation

```bash
pip install emailify
```

## Usage

### Basic Table
```python
import pandas as pd
import emailify as ef

df = pd.DataFrame({"Name": ["Alice", "Bob"], "Score": [95, 87]})
table = ef.Table(data=df)
html = ef.render(table)
```

### Text and Styling
```python
text = ef.Text(
    text="Hello, this is a styled header",
    style=ef.Style(background_color="#cbf4c9", padding_left="5px")
)
html = ef.render(text)
```

### Tables with Custom Styles
```python
table = ef.Table(
    data=df,
    header_style={"Name": ef.Style(background_color="#000", font_color="#fff")},
    column_style={"Score": ef.Style(background_color="#f0f0f0", bold=True)},
    row_style={0: ef.Style(background_color="#e6ffe6")}
)
```

### Charts with Matplotlib
```python
import io
import matplotlib.pyplot as plt

buf = io.BytesIO()
plt.plot([1, 2, 3], [2, 4, 1])
plt.savefig(buf, format="png", dpi=150)
plt.close()
buf.seek(0)

chart = ef.Graph(data=buf, format="png", width="600px")
html = ef.render(chart)
```

## Why MJML?

MJML compiles to responsive HTML that works across Gmail, Outlook, Apple Mail, and other clients. You write simple components like `ef.Table()` and `ef.Text()`, and emailify handles the complex email-compatible markup automatically.