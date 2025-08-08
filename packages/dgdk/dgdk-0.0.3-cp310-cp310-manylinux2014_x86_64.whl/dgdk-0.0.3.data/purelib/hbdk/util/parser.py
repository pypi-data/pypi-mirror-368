r"""
Add additional features to argparse
"""

import sys

import hbdk

_appeared_namespace_and_dest = set()


def add_warning_for_duplidate_arguments(parser) -> None:
    r"""
    Add warning for Python argparse parser to print warning if duplicate arguments detected
    :param parser: parser returned from argparse.ArgumentParser()
    """
    try:
        # pylint: disable=protected-access
        from argparse import _StoreAction, _StoreConstAction, _StoreTrueAction, _StoreFalseAction
    except ImportError:
        if hbdk.__release_type__ == "dev":
            print(
                "WARNING: Fail to run add_warning_for_duplidate_arguments(). Incompatible argparse?",
                file=sys.stderr)
        return
    actions = {
        None: _StoreAction,
        'store': _StoreAction,
        'store_const': _StoreConstAction,
        'store_true': _StoreTrueAction,
        'store_false': _StoreFalseAction,
    }
    for key, action in actions.items():
        store_fixed_value = key in ('store_true', 'store_false')
        if store_fixed_value:

            class _ActionWrapper(action):
                def __call__(self,
                             parser,
                             namespace,
                             values,
                             option_string=None,
                             **kwargs):  # pylint: disable=arguments-differ
                    s = (id(namespace), self.dest)
                    if s in _appeared_namespace_and_dest:
                        print(
                            "WARNING: specify %s multi times. Assume this is specified only once."
                            % (option_string or ""),
                            file=sys.stderr)
                    else:
                        _appeared_namespace_and_dest.add(s)
                    # pylint: disable=bad-super-call, arguments-differ
                    super(type(self), self).__call__(parser, namespace, values,
                                                     option_string, **kwargs)
        else:

            class _ActionWrapper(action):
                def __call__(self,
                             parser,
                             namespace,
                             values,
                             option_string=None,
                             **kwargs):  # pylint: disable=arguments-differ
                    s = (id(namespace), self.dest)
                    if s in _appeared_namespace_and_dest:
                        print(
                            "WARNING: specify %s multi times. Use %s=%s" %
                            (option_string or "", option_string or "",
                             str(values)),
                            file=sys.stderr)
                    else:
                        _appeared_namespace_and_dest.add(s)
                    # pylint: disable=bad-super-call, arguments-differ
                    super(type(self), self).__call__(parser, namespace, values,
                                                     option_string, **kwargs)

        _ActionWrapper.__name__ = action.__name__ + "_warn_duplicate"
        parser.register('action', key, _ActionWrapper)
