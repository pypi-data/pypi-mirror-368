"""
Generate slugs and provide flexible string filters.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Mapping


def slugify(value: str, *, separator: str|None = '-', keep: str|None = '_', as_separator: str|None = None, strip_separator: bool = True, strip_keep: bool = True, if_none: str|None = 'none', additional_conversions: Mapping[str,str]|None = None) -> str:
    """ 
    Generate a slug.

    Difference between `keep` and `as_separator`
    - `keep`: these characters are kept as is in the resulting slug
    - `as_separator`: these characters are transformed to a separator before the operation

    Identical to `django.utils.text.slugify` if no options are given.
    """
    if value is None:
        return if_none
    
    separator = separator if separator is not None else ''
    keep = keep if keep is not None else ''

    if as_separator:
        value = re.sub(f"[{re.escape(as_separator)}]", separator, value)

    # Normalize the string: replace diacritics by standard characters, lower the string, etc
    value = str(value)
    if additional_conversions:
        converted_value = ''
        for char in value:
            converted_char = additional_conversions.get(char)
            if converted_char is None:
                converted_char = char
            converted_value += converted_char
        value = converted_value
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()

    # Remove special characters
    remove_sequence = r'^a-zA-Z0-9\s' + re.escape(separator) + re.escape(keep)
    value = re.sub(f"[{remove_sequence}]", "", value)

    # Replace spaces and successive separators by a single separator
    replace_sequence = r'\s' + re.escape(separator)
    value = re.sub(f"[{replace_sequence}]+", separator, value)
    
    # Strips separator and kept characters
    strip_chars = (separator if strip_separator else '') + (keep if strip_keep else '')
    value = value.strip(strip_chars)

    return value


def slugify_snake(value: str, separator: str|None = '_', if_none: str|None = 'none', additional_conversions: Mapping[str,str]|None = None) -> str:
    """
    CamèlCase => camel_case
    """
    if value is None:
        return if_none
    
    separator = separator if separator is not None else ''
    
    # Normalize the string: replace diacritics by standard characters, etc
    # NOTE: don't lower the string
    value = str(value)
    if additional_conversions:
        converted_value = ''
        for char in value:
            converted_char = additional_conversions.get(char)
            if converted_char is None:
                converted_char = char
            converted_value += converted_char
        value = converted_value
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-_\s]+", separator, value).strip(separator)
    value = re.sub(r'(.)([A-Z][a-z]+)', f'\\1{separator}\\2', value)
    return re.sub(r'([a-z0-9])([A-Z])', f'\\1{separator}\\2', value).lower()


def slugen(value: str, separator: str|None = '-', keep: str|None = None) -> str:
    """
    Similar as `slugify` except than some defaults are changed compared to Django's version and some additional letters are handled.
    Closer to the results of the postgresql's "unaccent" function.
    """
    #Input examples that give different results than `slugify`: `AN_INPUT`, `Ørland`
    if value is None:
        return value
    
    value = value.replace('_', '-')
    
    return slugify(value, separator=separator, keep=keep, if_none=None, additional_conversions={ # non-ASCII letters that are not separated by "NFKD" normalization
        "œ": "oe",
        "Œ": "OE",
        "ø": "o",
        "Ø": "O",
        "æ": "ae",
        "Æ": "AE",
        "ß": "ss",
        "ẞ": "SS",
        "đ": "d",
        "Đ": "D",
        "ð": "d",
        "Ð": "D",
        "þ": "th",
        "Þ": "th",
        "ł": "l",
        "Ł": "L",
        "´": "", # in order to have same result as for "'"
    })


class Filter:
    def __init__(self, spec: str|re.Pattern, *, normalize: bool = False):
        self.normalize = normalize

        if isinstance(spec, re.Pattern):
            self.spec = spec

        elif isinstance(spec, str) and spec.startswith('^'):
            m = re.match(r'^(.*\$)(A|I|L|U|M|S|X)+$', spec, re.IGNORECASE)
            if m:
                pattern = m[1]
                flags = re.NOFLAG
                for letter in m[2]:
                    flags |= re.RegexFlag[letter.upper()]
            else:
                pattern = spec
                flags = re.NOFLAG

            self.spec = re.compile(pattern, flags)

        elif isinstance(spec, str):
            if self.normalize:
                spec = self.normalize_spec(spec)

            if '*' in spec:
                name_parts = spec.split('*')
                pattern_parts = [re.escape(name_part) for name_part in name_parts]
                pattern = r'^' + r'.*'.join(pattern_parts) + r'$'
                self.spec = re.compile(pattern)
            else:
                self.spec = spec

        else:
            raise TypeError(f"Filter spec must be a string or regex pattern, got {type(spec).__name__}")
       

    def __repr__(self) -> str:
        return self.spec.pattern if isinstance(self.spec, re.Pattern) else self.spec


    def matches(self, value: str, is_normalized: bool = False):
        if value is None:
            value = ""
        elif not isinstance(value, str):
            value = str(value)

        if self.normalize and not is_normalized:
            value = self.normalize_value(value)

        if isinstance(self.spec, re.Pattern):
            if self.spec.match(value):
                return True
            
        elif self.spec == value:
            return True


    @classmethod
    def normalize_spec(cls, spec: str):
        return slugify(spec, separator=None, keep='*', strip_keep=False, if_none=None)
    
    
    @classmethod
    def normalize_value(cls, value: str):
        return slugify(value, separator=None, keep=None, if_none=None)


class Filters:
    def __init__(self, specs: list[str|re.Pattern]|str|re.Pattern, *, normalize: bool = False):
        self.filters: list[Filter] = []

        if specs:
            if isinstance(specs, (str,re.Pattern)):
                specs = [specs]

            for spec in specs:
                self.filters.append(Filter(spec, normalize=normalize))


    def __len__(self):
        return len(self.filters)


    def matches(self, value: str, if_no_filter: bool = False):
        if not self.filters:
            return if_no_filter
        
        if value is None:
            value = ""
        elif not isinstance(value, str):
            value = str(value)
        
        normalized_value = None    

        for str_filter in self.filters:
            if str_filter.normalize:
                if normalized_value is None:
                    normalized_value = Filter.normalize_value(value)
                if str_filter.matches(normalized_value, is_normalized=True):
                    return True
            else:
                if str_filter.matches(value):
                    return True
                
        return False
