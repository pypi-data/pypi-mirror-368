# utstd

# Github Actions
https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/

https://docs.astral.sh/uv/guides/integration/github/

# Publish Package
https://docs.astral.sh/uv/guides/package/#publishing-your-package
```sh

uv lock
uv sync

uv version --bump patch

uv build
uv run --with utstd --no-project -- python -c "import utstd; print(utstd.__version__)"

git add .
git commit -m ""
git push
```
