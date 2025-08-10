"""Click-based CLI for termcap"""
import click
import sys
import os
import tempfile
from pathlib import Path

from .config_manager import get_config_manager
from .cli_config import show_config, list_templates, reset_config


def get_default_settings():
    """Get default settings from config manager"""
    manager = get_config_manager()
    config = manager.load_config()
    
    return {
        'template': config['general']['default_template'],
        'geometry': config['general']['default_geometry'],
        'min_duration': config['general']['default_min_duration'],
        'max_duration': config['general']['default_max_duration'],
        'loop_delay': config['general']['default_loop_delay'],
        'command': os.environ.get('SHELL', '/bin/bash'),
    }


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx, version):
    """Terminal capture tool - Record terminal sessions as SVG animations"""
    if version:
        try:
            from importlib.metadata import version as get_version
            version_str = get_version('termcap')
        except ImportError:
            # Fallback for Python < 3.8
            import pkg_resources
            version_str = pkg_resources.require('termcap')[0].version
        click.echo(f'termcap {version_str}')
        return


@main.command()
@click.argument('output_path', required=False)
@click.option('-c', '--command', help='Program to record (default: $SHELL)')
@click.option('-g', '--geometry', help='Terminal geometry (WIDTHxHEIGHT)')
def record(output_path, command, geometry):
    """Record a terminal session to a cast file"""
    import tempfile
    import shlex
    from .term import get_terminal_size, TerminalMode, record as term_record
    
    defaults = get_default_settings()
    
    # Set defaults
    if command is None:
        command = defaults['command']
    if output_path is None:
        _, output_path = tempfile.mkstemp(prefix='termtosvg_', suffix='.cast')
    
    # Parse geometry
    if geometry:
        try:
            columns, lines = map(int, geometry.split('x'))
        except ValueError:
            click.echo(f"Error: Invalid geometry '{geometry}'. Use format like '80x24'", err=True)
            sys.exit(1)
    else:
        columns, lines = get_terminal_size(sys.stdout.fileno())
    
    # Record session
    process_args = shlex.split(command)
    click.echo(f'Recording started, enter "exit" command or Control-D to end')
    
    with TerminalMode(sys.stdin.fileno()):
        records = term_record(process_args, columns, lines, sys.stdin.fileno(), sys.stdout.fileno())
        with open(output_path, 'w') as cast_file:
            for record_ in records:
                print(record_.to_json_line(), file=cast_file)
    
    click.echo(f'Recording ended, cast file is {output_path}')

@main.command()
@click.argument('input_file')
@click.argument('output_path', required=False)
@click.option('-D', '--loop-delay', type=int, help='Delay between animation loops (ms)')
@click.option('-m', '--min-duration', type=int, help='Minimum frame duration (ms)')
@click.option('-M', '--max-duration', type=int, help='Maximum frame duration (ms)')
@click.option('-s', '--still-frames', is_flag=True, help='Output still frames instead of animation')
@click.option('-t', '--template', help='SVG template to use')
def render(input_file, output_path, loop_delay, min_duration, max_duration, still_frames, template):
    """Render a cast file to SVG animation"""
    import tempfile
    from .asciicast import read_records
    from .term import timed_frames
    from . import anim
    
    defaults = get_default_settings()
    
    # Set defaults
    if template is None:
        template = defaults['template']
    if min_duration is None:
        min_duration = defaults['min_duration']
    if max_duration is None:
        max_duration = defaults['max_duration']
    if loop_delay is None:
        loop_delay = defaults['loop_delay']
    
    if output_path is None:
        if still_frames:
            output_path = tempfile.mkdtemp(prefix='termtosvg_')
        else:
            _, output_path = tempfile.mkstemp(prefix='termtosvg_', suffix='.svg')
    
    # Render
    click.echo('Rendering started')
    asciicast_records = read_records(input_file)
    geometry, frames = timed_frames(asciicast_records, min_duration, max_duration, loop_delay)
    
    if still_frames:
        anim.render_still_frames(frames=frames, geometry=geometry, directory=output_path, template=template)
        click.echo(f'Rendering ended, SVG frames are located at {output_path}')
    else:
        anim.render_animation(frames, geometry, output_path, template)
        click.echo(f'Rendering ended, SVG animation is {output_path}')


@main.group()
def config():
    """Configuration management commands"""
    pass


@config.command('show')
def config_show():
    """Show current configuration"""
    show_config()


@config.command('templates')
def config_templates():
    """List available templates"""
    list_templates()


@config.command('reset')
def config_reset():
    """Reset configuration to defaults"""
    if click.confirm('Are you sure you want to reset configuration to defaults?'):
        reset_config()


@config.command('set')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def config_set(section, key, value):
    """Set a configuration value"""
    manager = get_config_manager()
    
    # Try to convert numeric values
    if value.isdigit():
        value = int(value)
    elif value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
        
    manager.set_setting(section, key, value)
    click.echo(f'Set {section}.{key} = {value}')


@config.command('get')
@click.argument('section')
@click.argument('key')
def config_get(section, key):
    """Get a configuration value"""
    manager = get_config_manager()
    value = manager.get_setting(section, key)
    if value is not None:
        click.echo(f'{section}.{key} = {value}')
    else:
        click.echo(f'Configuration key {section}.{key} not found')


@main.group()
def template():
    """Template management commands"""
    pass


@template.command('install')
@click.argument('name')
@click.argument('template_file', type=click.Path(exists=True))
def template_install(name, template_file):
    """Install a custom template"""
    manager = get_config_manager()
    try:
        manager.install_custom_template(name, Path(template_file))
        click.echo(f'Template "{name}" installed successfully')
    except Exception as e:
        click.echo(f'Error installing template: {e}', err=True)
        sys.exit(1)


@template.command('remove')
@click.argument('name')
def template_remove(name):
    """Remove a custom template"""
    manager = get_config_manager()
    try:
        if click.confirm(f'Are you sure you want to remove template "{name}"?'):
            manager.remove_custom_template(name)
            click.echo(f'Template "{name}" removed successfully')
    except Exception as e:
        click.echo(f'Error removing template: {e}', err=True)
        sys.exit(1)


@template.command('list')
def template_list():
    """List all available templates"""
    list_templates()


if __name__ == '__main__':
    main()
