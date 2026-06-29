from types import UnionType
from typing import Union, get_origin, get_args


class TypesHelper:
  @staticmethod
  def turn_opts_into_tuple(type_var: type) -> tuple:
    origin = get_origin(type_var)
    is_union = origin is Union or isinstance(type_var, UnionType)
    if is_union:
      return get_args(type_var)
    return (origin or type_var,) # origin of generic type or type_var
