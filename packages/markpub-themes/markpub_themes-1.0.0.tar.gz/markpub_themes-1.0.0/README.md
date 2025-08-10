# markpub_themes

A collection of themes for
[markpub](https://pypi.org/project/markpub), a markdown web publishing package.

## Installation

```shell
pip install -i https://test.pypi.org/simple/ markpub-themes
```

## Available Themes

- **dolce** - A sweet and elegant theme

To see the available themes:  

``` shell
python -c "import markpub_themes; print(markpub_themes.list_themes())"
```

## Usage

```python
import markpub_themes

markpub_themes.list_themes()

markpub_themes.get_theme_path('dolce')
```

## License

MIT License - see LICENSE file for details.
