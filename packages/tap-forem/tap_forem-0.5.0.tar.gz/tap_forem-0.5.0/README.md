# `tap-forem`

Singer tap for the [Forem API](https://developers.forem.com/api).

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets.

## Capabilities

* `catalog`
* `discover`
* `about`
* `stream-maps`

### TODO

* `state`

## Settings

| Setting | Required | Default             | Description                  |
| :------ | :------- | :------------------ | :--------------------------- |
| api_key | True     | None                | The Forem API key.           |
| tag     | True     | None                | Tag for filter articles by.  |
| api_url | False    | https://dev.to/api/ | The url for the API service. |

A full list of supported settings and capabilities is available by running: `tap-forem --about`

### Source Authentication and Authorization

Follow the official docs in https://developers.forem.com/api#section/Authentication.

## Usage

You can easily run `tap-forem` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-forem --version
tap-forem --help
tap-forem --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

First, [install uv](https://docs.astral.sh/uv/getting-started/installation/).

Then, install the project dependencies:

```bash
uv sync
```

### Create and Run Tests

Create tests within the `tests` folder and
  then run:

```bash
uv run pytest
```

You can also test the `tap-forem` CLI interface directly using `uv run`:

```bash
uv run tap-forem --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
uv tool install meltano

# Initialize meltano within this directory
cd tap-forem
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-forem --version

# Or run a pipeline:
meltano run tap-forem target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
