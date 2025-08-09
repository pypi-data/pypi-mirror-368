# EOCube.RO Tools
![Grant Funded](https://img.shields.io/badge/funded_by-UEFISCDI-blueviolet)
[![pipeline status](https://gitlab.dev.info.uvt.ro/rocs/tools/eocube-tools/badges/main/pipeline.svg)](https://gitlab.dev.info.uvt.ro/rocs/tools/eocube-tools/-/pipelines)

This repository holds the `eocube` python library currently providing a set of minimal 
tools aimed to be used on the STAC Catalogs and data hosted by the ROCS Project

## Installing

### Option 1: From PyPi
```bash
pip install "eocube[cli]"
```

Visit https://pypi.org/project/eocube/ for more oficial packages.

### Option 2: From GitLab Package Registry
```bash
pip install eocube[cli] --index-url https://gitlab.dev.info.uvt.ro/api/v4/projects/3491/packages/pypi/simple
```
Visit the [GitLab Package Registry](https://gitlab.dev.info.uvt.ro/rocs/tools/eocube-tools/-/packages) for available development packages

### Option 3: From Git (development branch)
```bash
pip install "eocube[cli] @ git+https://gitlab.dev.info.uvt.ro/rocs/tools/eocube-tools.git@main"
```

## Command Line Tools
You can use the command line tool by calling the `eocube` library.

```bash
Usage: eocube [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  services
```

### 🔐 Authentication
#### Login
In order to authenticate against our service provider you need to call:

```bash
eocube auth login
```

This will open a browser window and perform the standard authentication.

#### Logout

In order to invalidate the session and delete local token issue you need to call:
```bash
eocube auth login
```

#### User Info
For obtaining user information you can call:

```bash
eocube auth login
```

### 🧰 Internal Services
### 🌍 External Services
#### Geo-Spatial.Org Services

Some basic services from the Geo-Spatial.Org are provided. All the tools provide the 
option to save the result in a `GeoJSON` file. 

```
Usage: eocube services geospatialorg [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  get-administrative-unit-by-code
                                  Uses the SIRUTA Code to retrieve the...
  get-administrative-unit-by-name
                                  Retrieves the administrative unit by name
  get-county-by-mnemonic          Retrieves the county by mnemonic
  get-county-by-name              Retrieves the county by name
```

## Library Tools
### Raster
  - `eocube.raster.utils.get_raster_patches()`: Function generating patches over an rasterio `DatasetReaser`

We welcome contributions! If you'd like to improve `eocube`, fix bugs, or propose new features, follow the steps below to set up your development environment.

## 🛠️ Development Setup (with Poetry)

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

### 1. Install Poetry

Follow the official instructions:  
👉 https://python-poetry.org/docs/#installation

Or, if you're on a Unix-like system:

```bash
pip install poetry
```

Or

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure it’s available:

```bash
poetry --version
```

### 2. Clone the repository
```bash
git clone https://gitlab.dev.info.uvt.ro/rocs/tools/eocube-tools.git
cd eocube-tools
```

### 3. Create a feature branch

**Never commit directly to main!**

Create a new branch for your work:

```bash
git checkout -b my-feature-branch # Replace with something meaningful
```

### 4. Install development dependencies
```bash
poetry install --with dev
```

This will install both the main library and the development tools (`black`, `pip-audit`, `twine`, etc).

### 5. Activate the shell (optional)

```bash
poetry shell
```

You can now run commands like `eocube`, `pytest`, or `black` directly.

## ✅ Submitting Changes
1. Push your branch to GitLab:
   ```bash
   git push --set-upstream origin my-feature-branch
   ```
2. Open a Merge Request (MR) via the GitLab UI.
3. Your MR will be reviewed and must be approved by a project maintainer before it can be merged.


## 🧹 Code Style
Make sure your code is properly formated. Non-compliant code will be rejected.
We use [Black](https://black.readthedocs.io/en/stable/) for consistent formatting. Before committing:

```bash
poetry run black .
```

## 🙏 Acknowledgements

This work was supported by a grant of the Ministry of Research, Innovation and Digitization, 
CCCDI - UEFISCDI, project number **PN-IV-P6-6.3-SOL-2024-2-0248**, within PNCDI IV.

## 📜 Licensing
After updating do not forget to update the NOTICE file with:

```bash
pip-licenses --from=mixed --format=plain --with-urls -i eocube > NOTICE
```

## Publish to PyPi
Publication to PyPi is intentionally manual.

In order to publish to PyPi please make sure to be on the correct branch/tag and issue:

```bash
rm -fr build/ dist/*
poetry build
poetry run twine upload --verbose -s -i 5C5D049F dist/*
```
In the above example adapt the GPG key id with your key id.