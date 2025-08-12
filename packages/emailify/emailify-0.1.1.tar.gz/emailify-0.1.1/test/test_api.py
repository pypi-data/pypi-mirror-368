import io

import matplotlib.pyplot as plt
import pandas as pd
import pytest

import emailify as ef


def test_api():
    buf = io.BytesIO()
    plt.plot([1, 2, 3], [2, 4, 1])
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)

    df = pd.DataFrame(
        {
            "hello2": [1, 2, 3],
            "hello": ["My", "Name", "Is"],
            "hello3": [1, 2, 3],
        }
    )
    df.rename(columns={"hello2": "hello"}, inplace=True)
    rendered = ef.render(
        ef.Text(
            text="Hello, this is a table with merged headers",
            style=ef.Style(background_color="#cbf4c9", padding_left="5"),
        ),
        ef.Table(
            data=df,
            merge_equal_headers=True,
            header_style={
                "hello": ef.Style(background_color="#000000", font_color="#ffffff"),
            },
            column_style={
                "hello3": ef.Style(background_color="#0d0d0", bold=True),
            },
            row_style={
                1: ef.Style(background_color="#cbf4c9", bold=True),
            },
        ),
        ef.Fill(style=ef.Style(background_color="#cbf4c9")),
        ef.Image(data=buf, format="png", width="600px"),
    )
    assert rendered is not None


if __name__ == "__main__":
    pytest.main([__file__])
