"""Compose. A command line utility for making React.js componets.

Composes helps you to create the structure for a React.js component,
following the View-Actions-index pattern.
"""
import argparse
import os.path
import re
import sys
from pathlib import Path
from typing import Dict, TextIO

INDEX = """\
import React from 'react'
import PropTypes from 'prop-types'
import Actions, {{ actionPropTypes }} from './Actions'
import View from './View'

const {name} = (props) => (
  <View {{...props}} {{...Actions(props)}} />
)

const propTypes = {{ }}

{name}.displayName = '{name}'

{name}.propTypes = propTypes

View.propTypes = {{
  ...propTypes,
  ...actionPropTypes,
}}

export default {name}
"""

SIMPLE_INDEX = """\
import React from 'react'
import PropTypes from 'prop-types'
import styles from './styles.module.css'

const {name} = (props) => (
  <></>
)

{name}.displayName = '{name}'

{name}.propTypes = {{ }}

export default {name}
"""

VIEW = """\
import React from 'react'
import styles from './styles.module.css'

const View = (props) => (
  <>
  </>
)

View.displayName = '{name}/View'

export default View
"""

ACTIONS = """\
import React from 'react'
import PropTypes from 'prop-types'

const Actions = (props) => {{ }}

export const actionPropTypes = {{ }}

export default Actions
"""


def make_args_parser():
    parser = argparse.ArgumentParser(prog='compose', description=__doc__)
    parser.add_argument('dir',
                         nargs='?',
                         type=Path,
                         default='.',
                         help='Directorio donde se creará el componente.')
    parser.add_argument('component_name',
                         help='Nombre del componente creado.')
    parser.add_argument('-y',
                         '--yes',
                         dest='skip_confirm',
                         action='store_true',
                         help='Saltarse confirmación. (Sí a todo)')
    parser.add_argument('-s',
                         '--simple',
                         action='store_true',
                         help='Crear componente sin Actions ni View.')
    return parser


def confirm(prompt: str, true_value: str) -> bool:
    return input(prompt).casefold() == true_value.casefold()


def is_component_name(name: str) -> bool:
    return re.match(r'^[A-Z][\w]*$', name) is not None


def render_template(file: TextIO, template: str, **context):
    file.write(template.format(**context))


def make_component(name: str, base: Path, file_template_mapping: Dict[str,
                                                                      str]):
    root: Path = base / name

    if not root.exists():
        root.mkdir(parents=True)

    context = {'name': name}

    for path, template in file_template_mapping.items():
        item_path: Path = root / path
        with item_path.open('w') as file:
            render_template(file, template, **context)


def get_templates(simple=False):
    if simple:
        return {'index.js': SIMPLE_INDEX, 'styles.module.css': ''}

    return {
        'index.js': INDEX,
        'Actions.js': ACTIONS,
        'View.js': VIEW,
        'styles.module.css': '',
    }


def main():
    args = make_args_parser().parse_args()

    base_path: Path = args.dir

    component_name: str = args.component_name

    if not is_component_name(component_name):
        print(
            'Error: El nombre del componente debe comenzar '
            'en una letra mayúscula y no debe contener espacios.',
            file=sys.stderr)
        sys.exit(1)

    templates = get_templates(simple=args.simple)

    print('Esta operación resultará en el siguiente arbol de archivos:\n',
          f'{base_path / component_name}{os.path.sep}')

    def print_tree(filenames):
        *filenames, last_filename= filenames
        for filename in filenames:
            print(f'    |---- {filename}')
        print(f'    \\---- {last_filename}')

    print_tree(templates.keys())

    print('Si alguno de estos archivos ya existe, serán sobreescritos.')

    if not args.skip_confirm and not confirm('¿Desea continuar? (s/n) ', 's'):
        print('Operación cancelada.')
        sys.exit(0)

    make_component(component_name, base_path, templates)

    print('Operación realizada exitosamente.')


if __name__ == '__main__':
    main()
