# calibre-recipe-runner

A lightweight Python sandbox for running Calibre news recipes.

The Calibre community has curated a treasure trove of over a thousand well-maintained [parsing recipes](https://github.com/kovidgoyal/calibre/tree/master/recipes) for news outlets around the world. These recipes are typically designed to run within Calibre itself — but what if you want to use them elsewhere?

`calibre-recipe-runner` is a lightweight sandbox that lets you execute Calibre news recipes outside of the Calibre environment. No installation of Calibre is required.

This tool:

- Dynamically loads `.recipe` files
- Emulates essential Calibre modules
- Extracts article feeds

## Example

Run the *Le Monde* recipe from the Calibre collection:
```
calibre-recipe-runner le_monde
```
Output:
```
https://www.lemonde.fr/article1.html
https://www.lemonde.fr/article2.html
```
Run any other recipe:
```
calibre-recipe-runner path/to/news.recipe
```

## Install

As a system-wide binary

```
uv tool install calibre-recipe-runner`
```

or

```
pipx install calibre-recipe-runner
```

As Python package

```
pip install calibre-recipe-runner
```

## Before first run & for occasional updates

Requires `curl` and `jq`.

```
calibre-recipe-runner --update
```
The recipe collection is stored in `~/.local/share/calibre-recipe-runner/recipes`.

## Limitations

- Most Calibre modules are stubbed or partially emulated.
- Recipes requiring authentication or complex browser automation may not work out of the box. PRs welcome.

## License

This project is licensed under the MIT License.
