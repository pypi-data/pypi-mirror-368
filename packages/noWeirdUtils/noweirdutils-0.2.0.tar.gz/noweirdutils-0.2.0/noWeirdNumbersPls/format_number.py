def format_number(number, thou_sep='.', dec_sep=',', prefix='', suffix='', style='default', decimals=None):
    """
    Format a number (or list/tuple/set of numbers) with custom separators, rounding, and style.

    Parameters:
        number: int, float, Decimal, or iterable of these. The number(s) to format.
        thou_sep: str, thousands separator (default: '.')
        dec_sep: str, decimal separator (default: ',')
        prefix: str, string to prepend to the formatted number (default: '')
        suffix: str, string to append to the formatted number (default: '')
        style: str, one of 'default', 'scientific', 'percent', 'binary', 'hex', 'roman' (default: 'default')
        decimals: int or None, number of decimal places (default: None, auto for style)

    Returns:
        str or iterable of str: Formatted number(s).

    Raises:
        TypeError: If input is not a number or valid iterable.
        ValueError: For invalid separator or style options.
    """
    import decimal
    def _format_single(num, thou_sep, dec_sep, prefix, suffix, style, decimals):
        # Validate input type
        if not isinstance(num, (int, float, decimal.Decimal)):
            raise TypeError("Input must be int, float, or Decimal")
        # Rounding
        if style != 'percent' and decimals is not None:
            try:
                d = decimal.Decimal(str(num))
                quant = decimal.Decimal('1.' + '0'*decimals)
                num = float(d.quantize(quant, rounding=decimal.ROUND_HALF_UP))
            except Exception:
                num = round(float(num), decimals)
        # Styles
        if style == 'scientific':
            s = f"{num:.{decimals if decimals is not None else 6}e}"
        elif style == 'percent':
            # For percent, round after multiplying by 100, using decimals+2
            val = num * 100
            if decimals is not None:
                try:
                    d = decimal.Decimal(str(val))
                    quant = decimal.Decimal('1.' + '0'*(decimals))
                    val = float(d.quantize(quant, rounding=decimal.ROUND_HALF_UP))
                except Exception:
                    val = round(float(val), decimals)
            s = f"{val:.{decimals if decimals is not None else 2}f}%"
        elif style == 'binary':
            # For binary representation, use mathematical rounding (0.5 always rounds up)
            rounded_num = int(num + 0.5) if num >= 0 else int(num - 0.5)
            s = bin(rounded_num)
        elif style == 'hex':
            # For hexadecimal representation, use mathematical rounding (0.5 always rounds up)
            rounded_num = int(num + 0.5) if num >= 0 else int(num - 0.5)
            s = hex(rounded_num)
        elif style == 'roman':
            def to_roman(n):
                # Roman numerals only support positive integers
                if n <= 0:
                    return ""
                val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
                syb = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
                roman_num = ''
                i = 0
                while n > 0:
                    for _ in range(n // val[i]):
                        roman_num += syb[i]
                        n -= val[i]
                    i += 1
                return roman_num
            # For Roman numerals, use mathematical rounding (0.5 always rounds up)
            rounded_num = int(num + 0.5) if num >= 0 else int(num - 0.5)
            s = to_roman(rounded_num)
        else:
            # Default: formatted with separators
            if isinstance(num, int):
                s = f"{num:,}".replace(',', thou_sep)
            else:
                if thou_sep == 'TEMP' or dec_sep == 'TEMP':
                    raise ValueError("Separators cannot be 'TEMP'")
                if thou_sep == "" and dec_sep == "":
                    raise ValueError("Only one separator can be an empty string")
                s = f"{num:,.{decimals if decimals is not None else 2}f}"
                s = s.replace(',', 'TEMP')
                s = s.replace('.', dec_sep)
                s = s.replace('TEMP', thou_sep)
        return f"{prefix}{s}{suffix}"

    def _format_iterable(obj, **kwargs):
        if isinstance(obj, (list, tuple, set)):
            return type(obj)(_format_single(x, **kwargs) for x in obj)
        return _format_single(obj, **kwargs)

    return _format_iterable(number, thou_sep=thou_sep, dec_sep=dec_sep, prefix=prefix, suffix=suffix, style=style, decimals=decimals)

def deformat_number(number, thou_sep='.', dec_sep=',', enforce_type=None, prefix='', suffix='', style='default'):
    """
    Convert a formatted number string (or list/tuple/set) back to a numeric type.

    Parameters:
        number: str or iterable of str. The formatted number(s) to parse.
        thou_sep: str, thousands separator used in the string (default: '.')
        dec_sep: str, decimal separator used in the string (default: ',')
        enforce_type: type or None. If set to int, float, or decimal.Decimal, force output to that type.
        prefix: str, string to remove from the start (default: '')
        suffix: str, string to remove from the end (default: '')
        style: str, one of 'default', 'binary', 'hex', 'roman' (default: 'default')

    Returns:
        int, float, Decimal, or iterable of these: Parsed number(s).

    Raises:
        ValueError: If the string cannot be converted to a number.
        TypeError: If enforce_type is not supported.
    """
    import decimal, re

    def _deformat_single(numstr, thou_sep, dec_sep, enforce_type, prefix, suffix, style):
        if not isinstance(numstr, str):
            raise ValueError("Input must be a string.")
        # Remove prefix/suffix if present
        if prefix and numstr.startswith(prefix):
            numstr = numstr[len(prefix):]
        if suffix and numstr.endswith(suffix):
            numstr = numstr[:-len(suffix)]
        # Styles
        if style == 'binary':
            return int(numstr, 2)
        elif style == 'hex':
            return int(numstr, 16)
        elif style == 'roman':
            def from_roman(s):
                roman_numeral_map = {'M':1000,'CM':900,'D':500,'CD':400,'C':100,'XC':90,'L':50,'XL':40,'X':10,'IX':9,'V':5,'IV':4,'I':1}
                i = 0
                num = 0
                while i < len(s):
                    if i+1<len(s) and s[i:i+2] in roman_numeral_map:
                        num += roman_numeral_map[s[i:i+2]]
                        i += 2
                    else:
                        num += roman_numeral_map[s[i]]
                        i += 1
                return num
            return from_roman(numstr)
        # Remove separators
        number_clean = numstr.replace(thou_sep, '').replace(dec_sep, '.')
        try:
            if enforce_type is int:
                return int(float(number_clean))
            elif enforce_type is float:
                return float(number_clean)
            elif enforce_type is decimal.Decimal:
                return decimal.Decimal(number_clean)
            elif enforce_type is None:
                try:
                    return float(number_clean)
                except Exception:
                    try:
                        return int(float(number_clean))
                    except Exception:
                        return decimal.Decimal(number_clean)
            else:
                raise TypeError("enforce_type must be int, float, decimal.Decimal, or None.")
        except Exception as e:
            raise ValueError(f"Could not deformat number: {e}")

    def _deformat_iterable(obj, **kwargs):
        if isinstance(obj, (list, tuple, set)):
            return type(obj)(_deformat_single(x, **kwargs) for x in obj)
        return _deformat_single(obj, **kwargs)

    return _deformat_iterable(number, thou_sep=thou_sep, dec_sep=dec_sep, enforce_type=enforce_type, prefix=prefix, suffix=suffix, style=style)

def set_decimals(x, decimals=2, force_float=False):
    """
    Robustly set the number of decimals for a number.

    Parameters:
        x (int, float, Decimal, or str): The number to round. Strings must be numeric.
        decimals (int): Number of decimal places to round to (max 1000 for safety).
        force_float (bool): If True, always return float. If False, return int if result is integral.

    Returns:
        float or int or None: Rounded number as float (or int if force_float is False and result is integral), or None if input is None.

    Raises:
        TypeError: If input is not a number or numeric string.
        ValueError: If input cannot be converted to a number with specified decimals.

    Notes:
        - Uses the decimal module for precision and to avoid floating-point issues.
        - Falls back to float rounding if decimal fails.
        - For extreme decimal values, precision is capped for performance and safety.
    """
    from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, getcontext
    if x is None:
        return None
    if isinstance(x, str):
        try:
            x = float(x.replace(",", "."))
        except Exception:
            raise ValueError("String input must be numeric.")
    if not isinstance(x, (int, float, Decimal)):
        raise TypeError("Input must be int, float, Decimal, or numeric string")
    # Set a reasonable max precision for decimals
    MAX_DECIMALS = 1000
    safe_decimals = min(decimals, MAX_DECIMALS)
    try:
        getcontext().prec = safe_decimals + 20
        d = Decimal(str(x))
        quant = Decimal('1.' + '0' * safe_decimals)
        result = d.quantize(quant, rounding=ROUND_HALF_UP)
        if not force_float and result == result.to_integral():
            return int(result)
        return float(result)
    except (InvalidOperation, ValueError):
        # Fallback: try to round with float if Decimal fails
        try:
            res = round(float(x), safe_decimals)
            if not force_float and res == int(res):
                return int(res)
            return float(res)
        except Exception as e:
            raise ValueError(f"Could not convert input to a number with specified decimals: {e}")


class NotWeird:
    """
    A convenient object-oriented wrapper for number formatting operations.

    This class provides a fluent interface for formatting numbers with chainable methods.
    The object stores formatting settings internally, which are automatically applied
    to all formatting operations unless explicitly overridden in specific method calls.

    Example:
        >>> nw = NotWeird(1234567.89)
        >>> nw.notAnglo().add_prefix('€')       # Sets format and prefix on the object
        >>> print(nw.default())                # "€1.234.567,89"
        >>> print(nw.percent())                # "€123456789,00%"
        >>> print(nw.default(prefix='$'))      # "$1.234.567,89" (temporary override)
        >>> print(nw.default())                # "€1.234.567,89" (back to stored prefix)
    """

    def __init__(self, number, thou_sep='.', dec_sep=',', prefix='', suffix='', decimals=None):
        """
        Initialize NotWeird with a number and default formatting options.

        Args:
            number: The number(s) to format
            thou_sep: Default thousands separator
            dec_sep: Default decimal separator
            prefix: Default prefix string
            suffix: Default suffix string
            decimals: Default number of decimal places
        """
        self._number = number
        self._thou_sep = thou_sep
        self._dec_sep = dec_sep
        self._prefix = prefix
        self._suffix = suffix
        self._decimals = decimals

    def format(self, style='default', thou_sep=None, dec_sep=None, prefix=None, suffix=None, decimals=None):
        """
        Format the number with specified or default options.

        Args:
            style: Formatting style ('default', 'scientific', 'percent', 'binary', 'hex', 'roman')
            thou_sep: Thousands separator (uses default if None)
            dec_sep: Decimal separator (uses default if None)
            prefix: Prefix string (uses default if None)
            suffix: Suffix string (uses default if None)
            decimals: Decimal places (uses default if None)

        Returns:
            str or iterable: Formatted number(s)
        """
        return format_number(
            self._number,
            thou_sep=thou_sep if thou_sep is not None else self._thou_sep,
            dec_sep=dec_sep if dec_sep is not None else self._dec_sep,
            prefix=prefix if prefix is not None else self._prefix,
            suffix=suffix if suffix is not None else self._suffix,
            style=style,
            decimals=decimals if decimals is not None else self._decimals
        )

    def default(self, thou_sep=None, dec_sep=None, prefix=None, suffix=None, decimals=None):
        """Format with default style."""
        return self.format('default', thou_sep=thou_sep, dec_sep=dec_sep,
                          prefix=prefix, suffix=suffix, decimals=decimals)

    def scientific(self, thou_sep=None, dec_sep=None, prefix=None, suffix=None, decimals=6):
        """Format in scientific notation."""
        return self.format('scientific', thou_sep=thou_sep, dec_sep=dec_sep,
                          prefix=prefix, suffix=suffix, decimals=decimals)

    def percent(self, thou_sep=None, dec_sep=None, prefix=None, suffix=None, decimals=2):
        """Format as percentage."""
        return self.format('percent', thou_sep=thou_sep, dec_sep=dec_sep,
                          prefix=prefix, suffix=suffix, decimals=decimals)

    def binary(self, prefix=None, suffix=None):
        """Format as binary."""
        return self.format('binary', prefix=prefix, suffix=suffix)

    def hex(self, prefix=None, suffix=None):
        """Format as hexadecimal."""
        return self.format('hex', prefix=prefix, suffix=suffix)

    def roman(self, prefix=None, suffix=None):
        """Format as Roman numerals."""
        return self.format('roman', prefix=prefix, suffix=suffix)

    # Convenient locale-style methods
    def notAnglo(self):
        """Set non-Anglo number format (. for thousands, , for decimal).
        Used in most of the world including Europe, Latin America, and many other regions."""
        self._thou_sep = '.'
        self._dec_sep = ','
        return self

    def anglo(self):
        """Set Anglo number format (, for thousands, . for decimal).
        Used in English-speaking countries like US, UK, Australia, Canada."""
        self._thou_sep = ','
        self._dec_sep = '.'
        return self

    def add_prefix(self, prefix):
        """Set prefix and modify this instance."""
        self._prefix = prefix
        return self

    def add_suffix(self, suffix):
        """Set suffix and modify this instance."""
        self._suffix = suffix
        return self

    def with_decimals(self, decimals):
        """Set decimal places and modify this instance."""
        self._decimals = decimals
        return self

    # Alternative property-style setters
    def set_prefix(self, prefix):
        """Set prefix (alternative to add_prefix)."""
        self._prefix = prefix
        return self

    def set_suffix(self, suffix):
        """Set suffix (alternative to add_suffix)."""
        self._suffix = suffix
        return self

    def set_decimals(self, decimals):
        """Set decimal places (alternative to with_decimals)."""
        self._decimals = decimals
        return self

    def set_separators(self, thou_sep=None, dec_sep=None):
        """Set thousands and/or decimal separators."""
        if thou_sep is not None:
            self._thou_sep = thou_sep
        if dec_sep is not None:
            self._dec_sep = dec_sep
        return self

    def precise(self, decimals=2, force_float=False):
        """Apply precise decimal rounding using set_decimals and modify this instance."""
        self._number = set_decimals(self._number, decimals=decimals, force_float=force_float)
        return self

    # Parsing methods
    @classmethod
    def parse(cls, formatted_string, thou_sep='.', dec_sep=',', prefix='', suffix='', style='default', enforce_type=None):
        """
        Parse a formatted string back to a number and return NotWeird instance.

        Args:
            formatted_string: The formatted string to parse
            thou_sep: Thousands separator used in the string
            dec_sep: Decimal separator used in the string
            prefix: Prefix to remove
            suffix: Suffix to remove
            style: Style used for formatting
            enforce_type: Type to enforce (int, float, Decimal, or None)

        Returns:
            NotWeird: New instance with the parsed number
        """
        parsed_number = deformat_number(formatted_string, thou_sep=thou_sep, dec_sep=dec_sep,
                                      prefix=prefix, suffix=suffix, style=style, enforce_type=enforce_type)
        return cls(parsed_number, thou_sep=thou_sep, dec_sep=dec_sep, prefix=prefix, suffix=suffix)

    def __str__(self):
        """String representation using default formatting."""
        return str(self.default())

    def __repr__(self):
        """Developer representation."""
        return f"<NotWeird {self._number} (thou_sep='{self._thou_sep}', dec_sep='{self._dec_sep}')>"

    @property
    def number(self):
        """Get the underlying number."""
        return self._number

    @property
    def formatted(self):
        """Get the fully formatted string with all parameters applied (prefix + formatted_number + suffix)."""
        return self.default()

    @property
    def formatted_percent(self):
        """Get the percentage formatted string with all parameters applied."""
        return self.percent()

    @property
    def formatted_scientific(self):
        """Get the scientific formatted string with all parameters applied."""
        return self.scientific()

    @property
    def formatted_binary(self):
        """Get the binary formatted string with all parameters applied."""
        return self.binary()

    @property
    def formatted_hex(self):
        """Get the hexadecimal formatted string with all parameters applied."""
        return self.hex()

    @property
    def formatted_roman(self):
        """Get the Roman numeral formatted string with all parameters applied."""
        return self.roman()

    # Raw formatting properties (without prefix/suffix)
    @property
    def raw_default(self):
        """Get the default formatted number without prefix/suffix."""
        return self.default(prefix='', suffix='')

    @property
    def raw_percent(self):
        """Get the percentage formatted number without prefix/suffix."""
        return self.percent(prefix='', suffix='')

    @property
    def raw_scientific(self):
        """Get the scientific formatted number without prefix/suffix."""
        return self.scientific(prefix='', suffix='')

    @property
    def raw_binary(self):
        """Get the binary formatted number without prefix/suffix."""
        return self.binary(prefix='', suffix='')

    @property
    def raw_hex(self):
        """Get the hexadecimal formatted number without prefix/suffix."""
        return self.hex(prefix='', suffix='')

    @property
    def raw_roman(self):
        """Get the Roman numeral formatted number without prefix/suffix."""
        return self.roman(prefix='', suffix='')

    if __name__ == "__main__":

        from format_number import NotWeird

        n = NotWeird(1234567.89)