import pyro as p

from .session_item import SessionItem


_DEFAULT_STORE = p.poutine.runtime._PYRO_PARAM_STORE


def _setter(store):
    p.poutine.runtime._PYRO_PARAM_STORE = store
    p.primitives._PYRO_PARAM_STORE = store
    p.primitives._param = p.poutine.runtime.effectful(
        store.get_param, type='param')


param_store = SessionItem(setter=_setter, default=_DEFAULT_STORE)