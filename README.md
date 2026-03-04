# Prixio Marketplace — Claude Code Plugins

A curated directory of Claude Code plugins for Prixio LLC business operations.

## Structure

- **`/plugins`** - Plugins developed and maintained by Prixio LLC

## Installation

Plugins can be installed directly from this marketplace via Claude Code's plugin system.

To install, run `/plugin install prixio-accounting@prixio-marketplace`

or browse for the plugin in `/plugin > Discover`

## Available Plugins

| Plugin | Description | Category |
|--------|-------------|----------|
| [prixio-accounting](./plugins/prixio-accounting) | Georgian accounting & tax compliance (rs.ge, VAT, salary, dividends) | Productivity |

## Plugin Structure

Each plugin follows the standard Claude Code plugin structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── agents/              # Agent definitions (optional)
├── skills/              # Skill definitions (optional)
├── commands/            # Slash commands (optional)
└── README.md            # Documentation
```

## License

Please see each plugin for the relevant license information.
