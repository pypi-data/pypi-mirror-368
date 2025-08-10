# termcap - Terminal Capture Tool

*A modern Python package for recording terminal sessions as SVG animations, based on the original [termtosvg project](https://github.com/nbedos/termtosvg).*

## Overview

termcap is a terminal session recorder that generates standalone SVG animations. This package is a modernized version of termtosvg with the following enhancements:

- 🎯 **Modern CLI Interface**: Based on `click` with intuitive subcommands
- ⚙️ **Configuration Management**: TOML-based configuration with `platformdirs`
- 🎨 **Template Management**: Easy installation and management of custom templates
- 🔧 **Enhanced User Experience**: Better error handling and user feedback

## Installation

```bash
pip install termcap
```

## Quick Start

### Basic Recording

```bash
# Record a terminal session
termcap record session.cast

# Render to SVG animation
termcap render session.cast animation.svg
```

### Using Templates

```bash
# List available templates
termcap template list

# Use a specific template
termcap render session.cast animation.svg --template gjm8

# Install a custom template
termcap template install my_template template.svg
```

### Configuration Management

```bash
# Show current configuration
termcap config show

# Set configuration values
termcap config set general default_template my_template
termcap config set general default_geometry 100x30

# Reset to defaults
termcap config reset
```

## Command Reference

### Main Commands

- `termcap record [output.cast]` - Record a terminal session
- `termcap render input.cast [output.svg]` - Render cast file to SVG
- `termcap --version` - Show version information
- `termcap --help` - Show help message

### Configuration Commands

- `termcap config show` - Display current configuration
- `termcap config set SECTION KEY VALUE` - Set configuration value
- `termcap config get SECTION KEY` - Get configuration value
- `termcap config reset` - Reset configuration to defaults
- `termcap config templates` - List available templates

### Template Commands

- `termcap template list` - List all available templates
- `termcap template install NAME FILE` - Install custom template
- `termcap template remove NAME` - Remove custom template

## Configuration

termcap uses a TOML configuration file located at:
- Linux: `~/.config/termcap/config.toml`
- macOS: `~/Library/Application Support/termcap/config.toml`
- Windows: `%APPDATA%\termcap\config.toml`

### Default Configuration

```toml
[general]
default_template = "gjm8"
default_geometry = "82x19"
default_min_duration = 17
default_max_duration = 3000
default_loop_delay = 1000

[templates]
custom_templates_enabled = true
builtin_templates_enabled = true

[output]
default_output_dir = "~/termcap_recordings"
auto_timestamp = true
```

## Templates

### Built-in Templates

termcap includes several built-in templates:
- `gjm8` - Default colorful template
- `dracula` - Dark theme with purple accents
- `solarized_dark` / `solarized_light` - Solarized color schemes
- `ubuntu` - Ubuntu-styled terminal
- `putty` - PuTTY-like appearance
- `window_frame` - Terminal with window frame
- And more...

### Custom Templates

Custom templates are stored in:
- Linux: `~/.config/termcap/templates/`
- macOS: `~/Library/Application Support/termcap/templates/`
- Windows: `%APPDATA%\termcap\templates\`

## Migration from termtosvg

If you're migrating from termtosvg, termcap maintains backward compatibility:

```bash
# These commands work the same way
termcap animation.svg
termcap record session.cast
termcap render session.cast animation.svg

# But you can also use the new modern interface
termcap record session.cast
termcap render session.cast animation.svg --template dracula
```

## Development

### Requirements

- Python 3.5+
- click
- platformdirs
- toml
- lxml
- pyte
- wcwidth

### Testing

```bash
python -m pytest termcap/tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is dual-licensed:

- **MIT License** - For new termcap features and enhancements (see [LICENSE-MIT](LICENSE-MIT))
- **BSD 3-Clause License** - For original termtosvg code (see [LICENSE-BSD](LICENSE-BSD))

You may choose either license for your use of this software.

### License Details

- The original termtosvg code by Nicolas Bedos remains under BSD 3-Clause License
- New termcap features, CLI interface, and enhancements by rexwzh are under MIT License
- Users can choose to use the software under either license terms

## Author

- **termcap**: rexwzh (1073853456@qq.com)
- **Original termtosvg**: Nicolas Bedos

## Changelog

### Version 0.1.1

- ✅ Rebranded as termcap
- ✅ Added click-based modern CLI interface
- ✅ Added TOML configuration management
- ✅ Added platformdirs for proper config directory handling
- ✅ Added template management commands
- ✅ Maintained full backward compatibility
- ✅ Improved error handling and user feedback
- ✅ Comprehensive test suite ensures reliability
- ✅ Added dual licensing (MIT + BSD)
