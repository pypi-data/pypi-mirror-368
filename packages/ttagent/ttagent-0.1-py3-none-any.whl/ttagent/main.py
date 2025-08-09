import argparse
import asyncio
import importlib
import inspect
import logging
import sys
from typing import Any

parser = argparse.ArgumentParser(description='Run ttagent')
parser.add_argument('agent', metavar='AGENT_PATH', type=str, help='Agent path')


def main() -> None:
    call_args = parser.parse_args()
    sys.exit(run(call_args.agent))


def run(path: str) -> int:
    agent = _import_agent(path)

    try:
        asyncio.run(agent.run())
    except Exception:
        logging.exception('Agent %s crashed', str(path))

    return 0


def _import_agent(path: str) -> Any:  # noqa ANN401
    module_str, _, target_str = path.partition(':')

    if not (module_str and target_str):
        raise ImportError('App path must be in format "<module>:<object-or-class>"')

    module = importlib.import_module(module_str)
    obj_or_cls = getattr(module, target_str, None)

    if not obj_or_cls:
        raise ImportError(f'Target object or class not found: {obj_or_cls}')

    if inspect.isclass(obj_or_cls):
        obj_or_cls = obj_or_cls()

    return obj_or_cls
