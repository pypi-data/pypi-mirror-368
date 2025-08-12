"""
Type mapping and introspection utilities for frameworks like FastAPI, SQLAlchemy, Pydantic.

This module provides sophisticated type inspection capabilities for extracting type information
from function arguments, class fields, and annotations. It supports:

- Function argument mapping with type hints
- Dataclass field inspection
- Class field mapping from type hints
- Annotated type unwrapping and metadata extraction
- Partial function handling
- Safe type hint resolution with forward references

Integrates with the advanced type checking system from typemapping.origins and typemapping.type_check.
"""

import inspect
import sys
from dataclasses import MISSING, dataclass, fields
from functools import lru_cache, partial
from inspect import Parameter, signature
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_type_hints,
)

# Import our compatibility layer
from typemapping.compat import (
    get_annotated_metadata,
    get_args,
    get_origin,
    is_annotated_type,
    strip_annotated,
)

# Import our advanced type checking functions
from typemapping.type_check import (  # is_Annotated,
    extended_isinstance,
    generic_issubclass,
    get_optional_inner_type,
    is_equal_type,
    is_optional_type,
)

# Python 3.8 compatibility - Field is not subscriptable
if sys.version_info >= (3, 9):
    from dataclasses import Field
else:
    from dataclasses import Field as _Field

    Field = _Field  # type: ignore

T = TypeVar("T")


@dataclass
class VarTypeInfo:
    """
    Comprehensive type information for function arguments or class fields.

    This class encapsulates all type-related information including the original
    annotation, resolved base type, default values, and metadata from Annotated types.
    """

    name: str
    argtype: Optional[Type[Any]]  # Original type annotation
    basetype: Optional[Type[Any]]  # Resolved type (unwrapped from Annotated)
    default: Optional[Any]
    has_default: bool = False
    extras: Optional[Tuple[Any, ...]] = None  # Metadata from Annotated[T, ...]

    @property
    def origin(self) -> Optional[Type[Any]]:
        """Get the origin of the base type (e.g., list from List[int])."""
        if self.basetype is None:
            return None
        return cast(Optional[Type[Any]], get_origin(self.basetype))

    @property
    def args(self) -> Tuple[Any, ...]:
        """Get the type arguments (e.g., (int,) from List[int])."""
        return get_args(self.basetype) if self.basetype is not None else ()

    def isequal(self, arg: Any) -> bool:
        """
        Check if this type info equals another type using advanced type equality.

        Uses our enhanced is_equal_type for precise comparison.
        """
        if arg is None or self.basetype is None:
            return arg is self.basetype

        if is_annotated_type(arg):
            return self.isequal(get_args(arg)[0])

        return is_equal_type(self.basetype, arg)

    def istype(self, tgttype: type) -> bool:
        """
        Check if this type info is compatible with target type.

        Uses our advanced type checking system for sophisticated compatibility.
        """
        if tgttype is None or self.basetype is None:
            return False

        if is_annotated_type(tgttype):
            # For Python 3.8 compatibility, we need to handle this carefully
            args = get_args(tgttype)
            if args:
                return self.istype(args[0])
            return False

        try:
            # Use our advanced generic_issubclass for better type relationships
            return self.isequal(tgttype) or generic_issubclass(self.basetype, tgttype)
        except (TypeError, AttributeError):
            return False

    def isinstance_check(self, obj: Any) -> bool:
        """
        Check if object is instance of this type using extended isinstance.

        This provides runtime type validation with support for generics.
        """
        if self.basetype is None:
            return obj is None

        try:
            return extended_isinstance(obj, self.basetype)
        except (TypeError, AttributeError):
            return False

    def getinstance(self, tgttype: Type[T], default: bool = True) -> Optional[T]:
        """
        Get instance of target type from extras or default.

        This is useful for extracting framework-specific objects from Annotated metadata.
        """
        if not isinstance(tgttype, type):
            return None

        # Search in Annotated metadata
        if self.extras is not None:
            founds = [e for e in self.extras if isinstance(e, tgttype)]
            if len(founds) > 0:
                return founds[0]

        # Check default value
        if default and self.has_default and isinstance(self.default, tgttype):
            return self.default

        return None

    def hasinstance(self, tgttype: type, default: bool = True) -> bool:
        """Check if has instance of target type."""
        return self.getinstance(tgttype, default) is not None

    def get_all_instances(self, tgttype: Type[T]) -> List[T]:
        """Get all instances of target type from extras and default."""
        instances = []

        # From extras
        if self.extras is not None:
            instances.extend([e for e in self.extras if isinstance(e, tgttype)])

        # From default
        if self.has_default and isinstance(self.default, tgttype):
            instances.append(self.default)

        return instances


class _NoDefault:
    """Sentinel object for parameters with no default value."""

    def __repr__(self) -> str:
        return "NO_DEFAULT"

    def __str__(self) -> str:
        return "NO_DEFAULT"


NO_DEFAULT = _NoDefault()


@lru_cache(maxsize=256)
def _get_module_globals(module_name: str) -> Dict[str, Any]:
    """Get module globals with caching for type hint resolution."""
    try:
        return vars(sys.modules[module_name]).copy()
    except KeyError:
        return {}


def is_safe_lambda(func: Callable[..., Any]) -> bool:
    """
    Check if a lambda function is safe to execute (no parameters, simple body).
    Safe lambdas are those without parameters that we can execute without side effects.
    """
    try:
        if not (inspect.isfunction(func) and func.__name__ == "<lambda>"):
            return False

        sig = inspect.signature(func)
        # Check if lambda has no parameters
        return len(sig.parameters) == 0
    except (ValueError, TypeError):
        return False


def try_execute_lambda(func: Callable[..., Any]) -> Tuple[bool, Optional[Any]]:
    """Versão segura que só executa lambdas isolados."""
    if not is_safe_lambda(func):
        return False, None

    code = func.__code__

    # Rejects if lambda has access to closure variables and globals
    if code.co_names or code.co_freevars:
        return False, None

    try:
        result = func()
        return True, result
    except Exception:
        return False, None


def infer_lambda_return_type(func: Callable[..., Any]) -> Optional[Type[Any]]:
    """
    Infer the return type of a lambda by executing it.

    For simple lambdas without parameters, we try to execute them safely.
    For lambdas with parameters, we cannot infer the type without execution.
    """
    if not (inspect.isfunction(func) and func.__name__ == "<lambda>"):
        return None

    # Try to execute parameterless lambdas
    success, result = try_execute_lambda(func)
    if success:
        # Execution succeeded, return the type of the result
        # This correctly handles None returns
        return type(result)

    # Execution failed or lambda has parameters
    return None


def get_safe_type_hints(
    obj: Any, localns: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get type hints safely, handling ForwardRef and Self references.

    This function provides robust type hint extraction that handles:
    - Forward references (strings)
    - Self references in class methods
    - Nested classes
    - Module-level type resolution
    - Lambda functions (NEW!)
    - Python 3.8 compatibility with None types
    """

    # For lambdas, we can't get type hints the normal way
    if inspect.isfunction(obj) and obj.__name__ == "<lambda>":
        # Try to infer return type for lambdas
        return_type = infer_lambda_return_type(obj)
        if return_type is not None:
            return {"return": return_type}
        return {}

    try:
        if inspect.isclass(obj):
            cls: Optional[Any] = obj
        elif inspect.isfunction(obj) or inspect.ismethod(obj):
            # Handle nested classes and methods
            qualname_parts = obj.__qualname__.split(".")
            cls = obj
            for part in qualname_parts[:-1]:
                try:
                    module = sys.modules.get(obj.__module__)
                    if module is None:
                        cls = None
                        break
                    cls = getattr(module, part, None)
                    if cls is None:
                        break
                except (AttributeError, KeyError):
                    cls = None
                    break
        else:
            cls = None

        # Get module globals safely
        globalns = {}
        if hasattr(obj, "__module__") and obj.__module__ in sys.modules:
            try:
                globalns = _get_module_globals(obj.__module__)
            except Exception:
                pass

        # For functions, also include their actual module's namespace
        if hasattr(obj, "__globals__"):
            # Function has its own globals, merge them
            globalns.update(obj.__globals__)

        # Add the class to global namespace for self-references
        if cls and inspect.isclass(cls):
            globalns[cls.__name__] = cls
            # Handle nested classes
            if "." in obj.__qualname__:
                parts = obj.__qualname__.split(".")
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:
                        break
                    try:
                        module = sys.modules.get(obj.__module__)
                        if module:
                            nested_cls = getattr(module, part, None)
                            if nested_cls and inspect.isclass(nested_cls):
                                globalns[part] = nested_cls
                    except (AttributeError, KeyError):
                        pass

        # Add localns to globalns if provided
        if localns:
            globalns.update(localns)

        # For Python 3.8, we need to handle None type specially
        if sys.version_info < (3, 9):
            globalns["NoneType"] = type(None)

        # Try to get type hints
        hints = get_type_hints(
            obj, globalns=globalns, localns=localns, include_extras=True
        )

        # Normalize None returns for consistency across Python versions
        if "return" in hints and hints["return"] is None:
            hints["return"] = type(None)

        return hints

    except (NameError, AttributeError, TypeError, RecursionError):
        # Fallback to basic inspection if type hints fail
        try:
            if hasattr(obj, "__annotations__"):
                # Safely access annotations
                try:
                    annotations: Dict[str, Any] = obj.__annotations__.copy()
                except (AttributeError, TypeError):
                    return {}

                # Try to resolve forward refs if we have namespace
                if globalns or localns:
                    resolved = {}
                    ns = {}
                    if globalns:
                        ns.update(globalns)
                    if localns:
                        ns.update(localns)

                    for name, annotation in annotations.items():
                        if isinstance(annotation, str) and annotation in ns:
                            resolved[name] = ns[annotation]
                        else:
                            resolved[name] = annotation

                    # Normalize None returns
                    if "return" in resolved and resolved["return"] is None:
                        resolved["return"] = type(None)

                    return resolved
                else:
                    # Normalize None returns even in fallback
                    if "return" in annotations and annotations["return"] is None:
                        annotations["return"] = type(None)
                    return annotations
        except Exception:
            pass
        return {}


def resolve_class_default(param: Parameter) -> Tuple[bool, Any]:
    """Resolve default value for class parameter."""
    if param.default is not Parameter.empty:
        return True, param.default
    return False, NO_DEFAULT


def resolve_dataclass_default(
    field: Any,
) -> Tuple[bool, Any]:  # Python 3.8 compat - can't use Field[Any]
    """Resolve default value for dataclass field."""
    if field.default is not MISSING:
        return True, field.default
    elif field.default_factory is not MISSING:
        # For dataclass fields, we return the factory itself for consistency
        # The caller should decide when to call it
        try:
            # Try to call factory for simple cases
            if callable(field.default_factory):
                factory_result = field.default_factory()
                return True, factory_result
        except Exception:
            # If factory fails, return the factory itself
            pass
        return True, field.default_factory
    return False, NO_DEFAULT


def field_factory(
    obj: Union[Any, Parameter],  # Python 3.8 compat - can't use Field[Any]
    hint: Any,
    bt_default_fallback: bool = True,
) -> VarTypeInfo:
    """
    Create VarTypeInfo from field or parameter.

    This is the core function that extracts comprehensive type information
    from function parameters or dataclass fields.
    """
    resolve_default = (
        resolve_class_default
        if isinstance(obj, Parameter)
        else resolve_dataclass_default
    )

    has_default, default = resolve_default(obj)  # type: ignore

    # Process the hint to handle forward references
    if hint is not inspect._empty and hint is not None:
        # If hint is a string (forward reference), keep it as is for now
        # It will be resolved later by the caller with proper namespace
        argtype = hint
    elif bt_default_fallback and default not in (NO_DEFAULT, None):
        argtype = type(default)
    else:
        argtype = None

    return make_funcarg(
        name=obj.name,
        tgttype=argtype,
        annotation=hint,
        default=default,
        has_default=has_default,
    )


def make_funcarg(
    name: str,
    tgttype: Optional[Type[Any]],
    annotation: Optional[Type[Any]] = None,
    default: Any = None,
    has_default: bool = False,
) -> VarTypeInfo:
    """
    Create VarTypeInfo with proper handling of Annotated types.

    This function unwraps Annotated types and extracts metadata for framework use.
    """
    # Use annotation if provided, otherwise fall back to tgttype
    type_to_check = annotation if annotation is not None else tgttype
    basetype = tgttype
    extras = None

    if type_to_check is not None and is_annotated_type(type_to_check):
        # Use our compat layer for Python 3.8 support
        basetype = strip_annotated(type_to_check)
        metadata = get_annotated_metadata(type_to_check)
        if metadata:
            extras = metadata

    return VarTypeInfo(
        name=name,
        argtype=tgttype,
        basetype=basetype,
        default=default,
        extras=extras,
        has_default=has_default,
    )


def unwrap_partial(
    func: Callable[..., Any],
) -> Tuple[Callable[..., Any], List[Any], Dict[str, Any]]:
    """
    Recursively unwrap partial functions.

    This handles nested partials correctly, preserving argument order and precedence.
    """
    partial_kwargs: Dict[Any, Any] = {}
    partial_args: List[Any] = []

    # Handle nested partials
    while isinstance(func, partial):
        # Merge keywords, with inner partials taking precedence
        new_kwargs = func.keywords or {}
        for k, v in partial_kwargs.items():
            if k not in new_kwargs:
                new_kwargs[k] = v
        partial_kwargs = new_kwargs

        # Prepend args from this partial
        partial_args = list(func.args or []) + partial_args
        func = func.func

    return func, partial_args, partial_kwargs


# ===== FIELD MAPPING STRATEGIES =====


def map_init_field(
    cls: Type[Any],
    bt_default_fallback: bool = True,
    localns: Optional[Dict[str, Any]] = None,
) -> List[VarTypeInfo]:
    """
    Map fields from __init__ method.

    This strategy extracts type information from constructor parameters.
    """
    init_method = cls.__init__

    # If it's object.__init__, return empty list since it has no useful parameters
    if init_method is object.__init__:
        return []

    hints = get_safe_type_hints(init_method, localns)
    sig = signature(init_method)
    items = [(name, param) for name, param in sig.parameters.items() if name != "self"]

    return [
        field_factory(obj, hints.get(name), bt_default_fallback) for name, obj in items
    ]


def map_dataclass_fields(
    cls: type,
    bt_default_fallback: bool = True,
    localns: Optional[Dict[str, Any]] = None,
) -> List[VarTypeInfo]:
    """
    Map dataclass fields.

    This strategy extracts type information from dataclass field definitions.
    """
    hints = get_safe_type_hints(cls, localns)
    items = [(field.name, field) for field in fields(cls)]

    return [
        field_factory(obj, hints.get(name), bt_default_fallback) for name, obj in items
    ]


def map_model_fields(
    cls: type,
    bt_default_fallback: bool = True,
    localns: Optional[Dict[str, Any]] = None,
) -> List[VarTypeInfo]:
    """
    Map model fields from type hints and class attributes.

    This strategy works with any class that has type hints, useful for
    model classes, configuration classes, etc.
    """
    hints = get_safe_type_hints(cls, localns)
    items = []

    for name in hints:
        # Skip methods and properties that might have side effects
        attr = None
        try:
            # Use getattr carefully to avoid triggering descriptors
            if hasattr(cls, name):
                attr_descriptor = getattr(type(cls), name, None)
                if isinstance(attr_descriptor, property):
                    # Skip properties to avoid side effects
                    attr = Parameter.empty
                elif callable(getattr(cls, name, None)):
                    # Skip methods
                    attr = Parameter.empty
                else:
                    attr = getattr(cls, name, Parameter.empty)
            else:
                attr = Parameter.empty
        except (AttributeError, TypeError):
            attr = Parameter.empty

        param = Parameter(
            name,
            Parameter.POSITIONAL_OR_KEYWORD,
            default=attr,
        )
        items.append((name, param))

    return [
        field_factory(obj, hints.get(name), bt_default_fallback) for name, obj in items
    ]


# ===== FUNCTION MAPPING UTILITIES =====


def map_return_type(
    func: Callable[..., Any], localns: Optional[Dict[str, Any]] = None
) -> VarTypeInfo:
    """
    Map function return type, with special handling for lambdas.

    This version is lambda-friendly and attempts to infer return types
    for simple parameterless lambdas.
    """
    sig = inspect.signature(func)
    hints = get_safe_type_hints(func, localns)
    raw_return_type = hints.get("return", sig.return_annotation)

    if raw_return_type is inspect.Signature.empty:
        raw_return_type = None

    # For lambdas, get_safe_type_hints already handles type inference
    # No need to call infer_lambda_return_type again here

    # Handle special case for None return type
    if raw_return_type is None and "return" in hints:
        # Check if the annotation was explicitly None (not just missing)
        func_annotations = getattr(func, "__annotations__", {})
        if "return" in func_annotations and func_annotations["return"] is None:
            raw_return_type = type(None)

    # Use function name, or a descriptive name for lambdas
    func_name = func.__name__ if func.__name__ != "<lambda>" else "lambda_function"

    return make_funcarg(
        name=func_name,
        tgttype=raw_return_type,
        annotation=raw_return_type,
    )


def get_return_type(func: Callable[..., Any]) -> Optional[Type[Any]]:
    """Get function return type."""
    returntype = map_return_type(func)
    return returntype.basetype


def map_func_args(
    func: Callable[..., Any],
    localns: Optional[Dict[str, Any]] = None,
    bt_default_fallback: bool = True,
) -> Tuple[Sequence[VarTypeInfo], VarTypeInfo]:
    """Map function arguments and return type."""
    funcargs = get_func_args(func, localns, bt_default_fallback)
    return_type = map_return_type(func, localns)
    return funcargs, return_type


def get_func_args(
    func: Callable[..., Any],
    localns: Optional[Dict[str, Any]] = None,
    bt_default_fallback: bool = True,
) -> Sequence[VarTypeInfo]:
    """
    Get function arguments as VarTypeInfo list.

    This function handles partial functions, type hints, and default values
    to provide comprehensive argument information.
    """
    # Handle partial functions
    original_func, partial_args, partial_kwargs = unwrap_partial(func)

    sig = inspect.signature(original_func)
    hints = get_safe_type_hints(original_func, localns)

    funcargs: List[VarTypeInfo] = []

    # Skip parameters that are filled by partial args
    skip_count = len(partial_args)

    for i, (name, param) in enumerate(sig.parameters.items()):
        # Skip parameters filled by positional partial args
        if i < skip_count:
            continue

        # Skip parameters filled by partial kwargs
        if name in partial_kwargs:
            continue

        # Skip *args and **kwargs
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        annotation = hints.get(name, param.annotation)

        # If annotation is a string (forward reference) and we have it in hints,
        # it should already be resolved. If not, try to resolve it from localns
        if isinstance(annotation, str) and localns and annotation in localns:
            annotation = localns[annotation]

        arg = field_factory(param, annotation, bt_default_fallback)
        funcargs.append(arg)

    return funcargs


# ===== FIELD TYPE UTILITIES =====

def get_field_type_(
    tgt: Type[Any],
    fieldname: str,
    localns: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    """
    Get field type from various sources, incluindo anotações herdadas em Python 3.8.

    Estratégias de busca:
    1. Anotações de classe (percorrendo __mro__ para herança)
    2. Anotações de __init__  (percorrendo __mro__)
    3. Propriedades (return)
    4. Métodos (return)
    """
    # 1) Class‑level, incluindo bases
    for base in getattr(tgt, "__mro__", (tgt,)):
        try:
            hints = get_safe_type_hints(base, localns)
            if fieldname in hints:
                return hints[fieldname]
        except (TypeError, AttributeError):
            continue

    # 2) __init__ nas bases
    for base in getattr(tgt, "__mro__", (tgt,)):
        try:
            init = getattr(base, "__init__", None)
            if init is not None and init is not object.__init__:
                init_hints = get_safe_type_hints(init, localns)
                if fieldname in init_hints:
                    return init_hints[fieldname]
        except (TypeError, AttributeError):
            continue

    # 3) Propriedade ou método
    try:
        attr = getattr(tgt, fieldname, None)
        if attr is None:
            return None

        if isinstance(attr, property):
            fget = attr.fget
            if fget:
                try:
                    prop_hints = get_safe_type_hints(fget, localns)
                    return prop_hints.get("return")
                except (TypeError, AttributeError):
                    pass

        elif callable(attr):
            try:
                meth_hints = get_safe_type_hints(attr, localns)
                return meth_hints.get("return")
            except (TypeError, AttributeError):
                pass

    except (TypeError, AttributeError):
        pass

    return None


def get_field_type(
    tgt: Type[Any],
    fieldname: str,
    localns: Optional[Dict[str, Any]] = None,
) -> Optional[Type[Any]]:
    """
    Envolve get_field_type_ para remover Annotated[T, ...] se presente.
    """
    btype = get_field_type_(tgt, fieldname, localns)
    if btype is not None and is_annotated_type(btype):
        return strip_annotated(btype)
    return btype

def get_nested_field_type(model: Type[Any], field_path: str) -> Optional[Type[Any]]:
    """
    Get the type of a nested field path like 'cls1.cls2.cls3'.
    If any field in the path is Optional, the final type will be Optional.
    """
    if not field_path:
        return None

    # Simple case
    if "." not in field_path:
        return get_field_type(model, field_path)

    fields = field_path.split(".")
    current_type = model
    is_path_optional = False

    for field_name in fields:
        if current_type is None:
            return None

        field_type = get_field_type(current_type, field_name)
        if field_type is None:
            return None

        if is_optional_type(field_type):
            is_path_optional = True
            current_type = get_optional_inner_type(field_type)
        else:
            current_type = field_type

    return Optional[current_type] if is_path_optional else current_type  # type: ignore


# ===== CONVENIENCE FUNCTIONS FOR FRAMEWORK INTEGRATION =====


def extract_metadata(var_info: VarTypeInfo, target_type: Type[T]) -> List[T]:
    """
    Extract all metadata instances of target type from VarTypeInfo.

    Useful for framework-specific annotations like FastAPI dependencies,
    SQLAlchemy column definitions, etc.
    """
    return var_info.get_all_instances(target_type)


def has_metadata(var_info: VarTypeInfo, target_type: Type[Any]) -> bool:
    """Check if VarTypeInfo has metadata of specific type."""
    return var_info.hasinstance(target_type)


def get_first_metadata(var_info: VarTypeInfo, target_type: Type[T]) -> Optional[T]:
    """Get first metadata instance of target type."""
    return var_info.getinstance(target_type)


def filter_fields_by_metadata(
    fields: List[VarTypeInfo], target_type: Type[Any]
) -> List[VarTypeInfo]:
    """Filter fields that have specific metadata type."""
    return [field for field in fields if has_metadata(field, target_type)]


def group_fields_by_type(
    fields: List[VarTypeInfo],
) -> Dict[Type[Any], List[VarTypeInfo]]:
    """Group fields by their base type."""
    groups: Dict[Type[Any], List[VarTypeInfo]] = {}
    for field in fields:
        if field.basetype is not None:
            if field.basetype not in groups:
                groups[field.basetype] = []
            groups[field.basetype].append(field)
    return groups
