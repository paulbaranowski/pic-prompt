# Building the Package Locally

Use uv to build the package:

`uv build`

# Building the package on Github

A GitHub Actions workflow automates building and publishing when a tagged release is pushed.

Workflow File: `.github/workflows/publish.yml`

## To publish a new version:
Update the version in pyproject.toml (e.g., 0.1.1).
Commit and push changes:

```
git add pyproject.toml
git commit -m "Bump to 0.1.1"
git push
```

Create and push a new tag:
```
git tag v0.1.1
git push origin v0.1.1
```
The workflow will automatically publish the new version.

# Installing the Package

To install the package from GitHub Packages:

Configure uv to use GitHub Packages: Edit uv.toml:

```
[index]
extra-index-url = ["https://__token__:ghp_YourTokenHere@ghcr.io/v2/your-username/my-python-package/pypi/simple"]
```

Replace ghp_YourTokenHere with your PAT.


## Install the package:

```
uv pip install my-python-package
```


Test it:
```
>>> import mypackage
>>> mypackage.say_hello()
'Hello from my package!'
```
