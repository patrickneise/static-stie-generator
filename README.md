# Static Site Generator - A [boot.dev](https://boot.dev) Project

A static site generator built from scratch from the [boot.dev](https://boot.dev) Python track.

## Usage

Add markdown files and folder in the `content` directory.

Static assets (css, js, images) are added to the `static` directory.

Build the site and run local development server:
```
./main.sh
```

All generated HTML pages and static content will be in the `public` folder.

A starter [template file](template.html) and [CSS file](static/index.css) are included.

## Develop

This repo contains a [devcontainer](https://code.visualstudio.com/docs/devcontainers/create-dev-container) to support isolated dev environment with all required languages and tooling.

Prereqs for using devcontainer ([Getting Started Guide](https://code.visualstudio.com/docs/devcontainers/containers#_getting-started)):

- VSCode
- [VSCode Remote Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Docker

The [devcontainer](.devcontainer/devcontainer.json) that contains:

- Python
- Golang
- [bootdev cli](https://github.com/bootdotdev/bootdev)
- a few VSCode extensions