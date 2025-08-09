# src/pico_ioc/__init__.py

import functools, inspect, pkgutil, importlib, logging, sys
from typing import Callable, Any, Iterator, Optional, AsyncIterator

try:
    # written at build time by setuptools-scm
    from ._version import __version__
except Exception:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["__version__"]

# ==============================================================================
# --- 1. Container and Chameleon Proxy (Framework-Agnostic) ---
# ==============================================================================
class PicoContainer:
    def __init__(self):
        self._providers: dict[Any, Callable[[], Any]] = {}
        self._singletons: dict[Any, Any] = {}

    def bind(self, key: Any, provider: Callable[[], Any]):
        self._providers[key] = provider

    def has(self, key: Any) -> bool:
        return key in self._providers or key in self._singletons

    def get(self, key: Any) -> Any:
        if key in self._singletons:
            return self._singletons[key]
        if key in self._providers:
            instance = self._providers[key]()
            self._singletons[key] = instance
            return instance
        raise NameError(f"No provider found for key: {key}")

class LazyProxy:
    """
    A full-fledged lazy proxy that delegates almost all operations
    to the real object, which is created only on first access.
    It is completely framework-agnostic.
    """
    def __init__(self, object_creator: Callable[[], Any]):
        object.__setattr__(self, "_object_creator", object_creator)
        object.__setattr__(self, "__real_object", None)

    def _get_real_object(self) -> Any:
        real_obj = object.__getattribute__(self, "__real_object")
        if real_obj is None:
            real_obj = object.__getattribute__(self, "_object_creator")()
            object.__setattr__(self, "__real_object", real_obj)
        return real_obj

    # --- Core Proxying and Representation ---
    @property
    def __class__(self):
        return self._get_real_object().__class__

    def __getattr__(self, name):
        return getattr(self._get_real_object(), name)
        
    def __setattr__(self, name, value):
        setattr(self._get_real_object(), name, value)

    def __delattr__(self, name):
        delattr(self._get_real_object(), name)

    def __str__(self):
        return str(self._get_real_object())

    def __repr__(self):
        return repr(self._get_real_object())
        
    def __dir__(self):
        return dir(self._get_real_object())

    # --- Emulation of container types ---
    def __len__(self): return len(self._get_real_object())
    def __getitem__(self, key): return self._get_real_object()[key]
    def __setitem__(self, key, value): self._get_real_object()[key] = value
    def __delitem__(self, key): del self._get_real_object()[key]
    def __iter__(self): return iter(self._get_real_object())
    def __reversed__(self): return reversed(self._get_real_object())
    def __contains__(self, item): return item in self._get_real_object()

    # --- Emulation of numeric types and operators ---
    def __add__(self, other): return self._get_real_object() + other
    def __sub__(self, other): return self._get_real_object() - other
    def __mul__(self, other): return self._get_real_object() * other
    def __matmul__(self, other): return self._get_real_object() @ other
    def __truediv__(self, other): return self._get_real_object() / other
    def __floordiv__(self, other): return self._get_real_object() // other
    def __mod__(self, other): return self._get_real_object() % other
    def __divmod__(self, other): return divmod(self._get_real_object(), other)
    def __pow__(self, other, modulo=None): return pow(self._get_real_object(), other, modulo)
    def __lshift__(self, other): return self._get_real_object() << other
    def __rshift__(self, other): return self._get_real_object() >> other
    def __and__(self, other): return self._get_real_object() & other
    def __xor__(self, other): return self._get_real_object() ^ other
    def __or__(self, other): return self._get_real_object() | other

    # --- Right-hand side numeric operators ---
    def __radd__(self, other): return other + self._get_real_object()
    def __rsub__(self, other): return other - self._get_real_object()
    def __rmul__(self, other): return other * self._get_real_object()
    def __rmatmul__(self, other): return other @ self._get_real_object()
    def __rtruediv__(self, other): return other / self._get_real_object()
    def __rfloordiv__(self, other): return other // self._get_real_object()
    def __rmod__(self, other): return other % self._get_real_object()
    def __rdivmod__(self, other): return divmod(other, self._get_real_object())
    def __rpow__(self, other): return pow(other, self._get_real_object())
    def __rlshift__(self, other): return other << self._get_real_object()
    def __rrshift__(self, other): return other >> self._get_real_object()
    def __rand__(self, other): return other & self._get_real_object()
    def __rxor__(self, other): return other ^ self._get_real_object()
    def __ror__(self, other): return other | self._get_real_object()

    # --- Unary operators ---
    def __neg__(self): return -self._get_real_object()
    def __pos__(self): return +self._get_real_object()
    def __abs__(self): return abs(self._get_real_object())
    def __invert__(self): return ~self._get_real_object()

    # --- Comparison operators ---
    def __eq__(self, other): return self._get_real_object() == other
    def __ne__(self, other): return self._get_real_object() != other
    def __lt__(self, other): return self._get_real_object() < other
    def __le__(self, other): return self._get_real_object() <= other
    def __gt__(self, other): return self._get_real_object() > other
    def __ge__(self, other): return self._get_real_object() >= other
    def __hash__(self): return hash(self._get_real_object())

    # --- Truthiness, Callability and Context Management ---
    def __bool__(self): return bool(self._get_real_object())
    def __call__(self, *args, **kwargs): return self._get_real_object()(*args, **kwargs)
    def __enter__(self): return self._get_real_object().__enter__()
    def __exit__(self, exc_type, exc_val, exc_tb): return self._get_real_object().__exit__(exc_type, exc_val, exc_tb)

# ==============================================================================
# --- 2. The Scanner and `init` Facade ---
# ==============================================================================
def _resolve_param(container: PicoContainer, p: inspect.Parameter) -> Any:
    if p.name == 'self' or p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
        raise RuntimeError("Invalid param for resolution")

    if container.has(p.name):
        return container.get(p.name)

    ann = p.annotation
    if ann is not inspect._empty and container.has(ann):
        return container.get(ann)

    if ann is not inspect._empty:
        try:
            for base in getattr(ann, "__mro__", ())[1:]:
                if base is object:
                    break
                if container.has(base):
                    return container.get(base)
        except Exception:
            pass

    if container.has(str(p.name)):
        return container.get(str(p.name))

    key = p.name if not (ann and ann is not inspect._empty) else ann
    return container.get(key)


def _scan_and_configure(
    package_or_name,
    container: PicoContainer,
    exclude: Optional[Callable[[str], bool]] = None
):
    package = importlib.import_module(package_or_name) if isinstance(package_or_name, str) else package_or_name
    logging.info(f"🚀 Scanning in '{package.__name__}'...")
    component_classes, factory_classes = [], []
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        # Skip excluded modules (used by auto_exclude_caller and custom excludes)
        if exclude and exclude(name):
            logging.info(f"  ⏭️ Skipping module {name} (excluded)")
            continue
        try:
            module = importlib.import_module(name)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, '_is_component'):
                    component_classes.append(obj)
                elif hasattr(obj, '_is_factory_component'):
                    factory_classes.append(obj)
        except Exception as e:
            logging.warning(f"  ⚠️ Module {name} not processed: {e}")

    for factory_cls in factory_classes:
        try:
            sig = inspect.signature(factory_cls.__init__)
            instance = factory_cls(container) if 'container' in sig.parameters else factory_cls()
            for _, method in inspect.getmembers(instance, inspect.ismethod):
                if hasattr(method, '_provides_name'):
                    container.bind(getattr(method, '_provides_name'), method)
        except Exception as e:
            logging.error(f"  ❌ Error in factory {factory_cls.__name__}: {e}", exc_info=True)

    for component_cls in component_classes:
        key = getattr(component_cls, '_component_key', component_cls)
        def create_component(cls=component_cls):
            sig = inspect.signature(cls.__init__)
            deps = {}
            for p in sig.parameters.values():
                if p.name == 'self' or p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                    continue
                deps[p.name] = _resolve_param(container, p)
            return cls(**deps)
        container.bind(key, create_component)

_container = None

def init(root_package, *, exclude: Optional[Callable[[str], bool]] = None, auto_exclude_caller: bool = True):
    global _container
    if _container:
        return _container

    combined_exclude = exclude
    if auto_exclude_caller:
        # módulo que invoca a init()
        try:
            caller_frame = inspect.stack()[1].frame
            caller_module = inspect.getmodule(caller_frame)
            caller_name = getattr(caller_module, "__name__", None)
        except Exception:
            caller_name = None

        if caller_name:
            if combined_exclude is None:
                def combined_exclude(mod: str, _caller=caller_name):
                    return mod == _caller
            else:
                prev = combined_exclude
                def combined_exclude(mod: str, _caller=caller_name, _prev=prev):
                    return mod == _caller or _prev(mod)

    _container = PicoContainer()
    logging.info("🔌 Initializing 'pico-ioc'...")
    _scan_and_configure(root_package, _container, exclude=combined_exclude)
    logging.info("✅ Container configured and ready.")
    return _container

# ==============================================================================
# --- 3. The Decorators ---
# ==============================================================================
def factory_component(cls):
    setattr(cls, '_is_factory_component', True)
    return cls

def provides(key: Any, *, lazy: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return LazyProxy(lambda: func(*args, **kwargs)) if lazy else func(*args, **kwargs)
        # mantenemos compat con _provides_name (por si alguien lo usa)
        setattr(wrapper, '_provides_name', key)
        return wrapper
    return decorator

def component(cls=None, *, name: str = None):
    def decorator(cls):
        setattr(cls, '_is_component', True)
        setattr(cls, '_component_key', name if name is not None else cls)
        return cls
    return decorator(cls) if cls else decorator

