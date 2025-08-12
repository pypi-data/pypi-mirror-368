
class MetricFTW:
    """
    A comprehensive unit conversion library for metric and non-metric units.

    Execute the show_available_conversions(detailed=False/True) method to see all supported conversions.

    This class provides conversion capabilities for various measurement categories including:
    - Length (metric and imperial)
    - Mass (metric and imperial)
    - Area (metric and imperial)
    - Volume (metric and imperial)
    - Speed (metric and imperial)
    - Energy (various units)
    - Pressure (various units)
    - Power (various units)
    - Temperature (Celsius, Fahrenheit, Kelvin, Rankine)

    All conversion methods support both individual numbers and iterables (lists, tuples, etc.).
    """

    # === CONVERSION FACTORS AND UNITS ===
    # Length
    metric_longitude = ["pm", "nm", "um", "mm", "cm", "dm", "m", "dam", "hm", "km"]
    metric_longitude_factors = {u: 10**i for i, u in enumerate(metric_longitude)}
    non_metric_longitude_to_cm = {
        "inch": 2.54,
        "foot": 30.48,
        "yard": 91.44,
        "mile": 160934.4,
        "nautical_mile": 185200,
        "angstrom": 1e-8,
        "mil": 0.00254,
        "furlong": 20116.8,
        "fathom": 182.88,
        "light_year": 9.461e17,
        "parsec": 3.086e18,
        "astronomical_unit": 1.496e13
    }

    # Mass
    metric_mass = ["pg", "ng", "ug", "mg", "cg", "dg", "g", "dag", "hg", "kg", "t"]
    metric_mass_factors = {u: 10**i for i, u in enumerate(metric_mass)}
    non_metric_mass_to_g = {
        "ounce": 28.3495,
        "pound": 453.592,
        "stone": 6350.29,
        "ton_us": 907185,
        "ton_uk": 1016046.9,
        "grain": 0.0647989,
        "dram": 1.77185,
        "troy_ounce": 31.1035,
        "carat": 0.2,
        "slug": 14593.9
    }

    # Area
    metric_area = ["mm2", "cm2", "dm2", "m2", "dam2", "hm2", "km2"]
    metric_area_factors = {u: 100**i for i, u in enumerate(metric_area)}
    non_metric_area_to_m2 = {
        "sqin": 0.00064516,
        "sqft": 0.092903,
        "sqyd": 0.836127,
        "acre": 4046.86,
        "hectare": 10000,
        "sqmile": 2.59e6,
        "barn": 1e-28,
        "are": 100,
        "rood": 1011.71
    }

    # Volume
    metric_volume = ["mm3", "cm3", "dm3", "m3", "dam3", "hm3", "km3", "l", "ml", "cl", "dl", "dal", "hl", "kl"]
    metric_volume_factors = {"mm3": 1e-6, "cm3": 1e-3, "dm3": 1, "m3": 1000, "dam3": 1e4, "hm3": 1e5, "km3": 1e8, "l": 1, "ml": 1e-3, "cl": 1e-2, "dl": 1e-1, "dal": 10, "hl": 100, "kl": 1000}
    non_metric_volume_to_l = {
        "gallon_us": 3.78541,
        "gallon_uk": 4.54609,
        "quart": 0.946353,
        "pint": 0.473176,
        "cup": 0.24,
        "fluid_ounce": 0.0295735,
        "cubic_inch": 0.0163871,
        "tablespoon": 0.0147868,
        "teaspoon": 0.00492892,
        "barrel_oil": 158.987,
        "bushel": 35.2391
    }

    # Speed
    metric_speed = ["mm/s", "cm/s", "m/s", "km/h"]
    metric_speed_factors = {"mm/s": 0.001, "cm/s": 0.01, "m/s": 1, "km/h": 0.277778}
    non_metric_speed_to_ms = {
        "mph": 0.44704,
        "knot": 0.514444,
        "fps": 0.3048,
        "mach": 343
    }

    # Energy
    metric_energy = ["J", "kJ", "MJ", "GJ", "TJ"]
    metric_energy_factors = {"J": 1, "kJ": 1000, "MJ": 1e6, "GJ": 1e9, "TJ": 1e12}
    non_metric_energy_to_j = {
        "cal": 4.184,
        "kcal": 4184,
        "Wh": 3600,
        "kWh": 3.6e6,
        "BTU": 1055.06,
        "erg": 1e-7,
        "foot_pound": 1.35582,
        "electron_volt": 1.602e-19
    }

    # Pressure
    metric_pressure = ["Pa", "hPa", "kPa", "MPa", "GPa", "bar", "mbar"]
    metric_pressure_factors = {"Pa": 1, "hPa": 100, "kPa": 1000, "MPa": 1e6, "GPa": 1e9, "bar": 1e5, "mbar": 100}
    non_metric_pressure_to_pa = {
        "atm": 101325,
        "psi": 6894.76,
        "mmHg": 133.322,
        "torr": 133.322,
        "inHg": 3386.39
    }

    # Power
    metric_power = ["W", "kW", "MW", "GW", "TW"]
    metric_power_factors = {"W": 1, "kW": 1000, "MW": 1e6, "GW": 1e9, "TW": 1e12}
    non_metric_power_to_w = {
        "hp": 745.7,
        "metric_hp": 735.499,
        "BTU_per_hour": 0.293071
    }

    # === GENERIC CONVERSION FUNCTIONS ===

    def _handle_iterable_conversion(self, value, conversion_func, *args):
        """
        Helper method to handle both individual values and iterables.

        Args:
            value: Either a number or an iterable of numbers
            conversion_func: The conversion function to apply
            *args: Additional arguments for the conversion function

        Returns:
            Either a single converted value or a list of converted values
        """
        try:
            # Try to iterate over the value
            iter(value)
            # If it's a string, treat it as a single value
            if isinstance(value, str):
                return conversion_func(value, *args)
            # If it's iterable but not a string, process each element
            return [conversion_func(item, *args) for item in value]
        except TypeError:
            # If it's not iterable, it's a single value
            return conversion_func(value, *args)

    def _convert_longitude_single(self, value, from_unit, to_unit):
        """Internal method for converting a single longitude value."""
        # First, convert to cm (base unit for metric length)
        if from_unit in self.metric_longitude:
            cm = value * (10 ** (self.metric_longitude.index(from_unit) - 4))  # cm is at index 4
        elif from_unit in self.non_metric_longitude_to_cm:
            cm = value * self.non_metric_longitude_to_cm[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # Then, from cm to target unit
        if to_unit in self.metric_longitude:
            return cm / (10 ** (self.metric_longitude.index(to_unit) - 4))
        elif to_unit in self.non_metric_longitude_to_cm:
            return cm / self.non_metric_longitude_to_cm[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_longitude(self, value, from_unit, to_unit):
        """
        Convert length measurements between different units.

        Supports both metric units (pm, nm, um, mm, cm, dm, m, dam, hm, km) and
        non-metric units (inch, foot, yard, mile, nautical_mile, angstrom, mil,
        furlong, fathom, light_year, parsec, astronomical_unit).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_longitude(100, "cm", "m")
            1.0
            >>> converter.convert_longitude([1, 2, 3], "m", "ft")
            [3.28084, 6.56168, 9.84252]
        """
        return self._handle_iterable_conversion(value, self._convert_longitude_single, from_unit, to_unit)

    def _convert_mass_single(self, value, from_unit, to_unit):
        """Internal method for converting a single mass value."""
        # First, convert to grams (base unit for metric mass)
        if from_unit in self.metric_mass:
            g = value * (10 ** (self.metric_mass.index(from_unit) - 6))  # g is at index 6
        elif from_unit in self.non_metric_mass_to_g:
            g = value * self.non_metric_mass_to_g[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # Then, from grams to target unit
        if to_unit in self.metric_mass:
            return g / (10 ** (self.metric_mass.index(to_unit) - 6))
        elif to_unit in self.non_metric_mass_to_g:
            return g / self.non_metric_mass_to_g[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_mass(self, value, from_unit, to_unit):
        """
        Convert mass measurements between different units.

        Supports both metric units (pg, ng, ug, mg, cg, dg, g, dag, hg, kg, t) and
        non-metric units (ounce, pound, stone, ton_us, ton_uk, grain, dram,
        troy_ounce, carat, slug).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_mass(1000, "g", "kg")
            1.0
            >>> converter.convert_mass([1, 2], "kg", "pound")
            [2.20462, 4.40924]
        """
        return self._handle_iterable_conversion(value, self._convert_mass_single, from_unit, to_unit)

    def _convert_area_single(self, value, from_unit, to_unit):
        """Internal method for converting a single area value."""
        # First, convert to m2
        if from_unit in self.metric_area:
            m2 = value * (100 ** (self.metric_area.index(from_unit) - 3))  # m2 is at index 3
        elif from_unit in self.non_metric_area_to_m2:
            m2 = value * self.non_metric_area_to_m2[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # Then, from m2 to target unit
        if to_unit in self.metric_area:
            return m2 / (100 ** (self.metric_area.index(to_unit) - 3))
        elif to_unit in self.non_metric_area_to_m2:
            return m2 / self.non_metric_area_to_m2[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_area(self, value, from_unit, to_unit):
        """
        Convert area measurements between different units.

        Supports both metric units (mm2, cm2, dm2, m2, dam2, hm2, km2) and
        non-metric units (sqin, sqft, sqyd, acre, hectare, sqmile, barn, are, rood).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_area(10000, "cm2", "m2")
            1.0
            >>> converter.convert_area([1, 2], "m2", "sqft")
            [10.7639, 21.5278]
        """
        return self._handle_iterable_conversion(value, self._convert_area_single, from_unit, to_unit)

    def _convert_volume_single(self, value, from_unit, to_unit):
        """Internal method for converting a single volume value."""
        # Convert to liters
        if from_unit in self.metric_volume:
            l = value * self.metric_volume_factors[from_unit]
        elif from_unit in self.non_metric_volume_to_l:
            l = value * self.non_metric_volume_to_l[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # From liters to target unit
        if to_unit in self.metric_volume:
            return l / self.metric_volume_factors[to_unit]
        elif to_unit in self.non_metric_volume_to_l:
            return l / self.non_metric_volume_to_l[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_volume(self, value, from_unit, to_unit):
        """
        Convert volume measurements between different units.

        Supports both metric units (mm3, cm3, dm3, m3, dam3, hm3, km3, l, ml, cl, dl, dal, hl, kl)
        and non-metric units (gallon_us, gallon_uk, quart, pint, cup, fluid_ounce, cubic_inch,
        tablespoon, teaspoon, barrel_oil, bushel).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_volume(1000, "ml", "l")
            1.0
            >>> converter.convert_volume([1, 2], "l", "gallon_us")
            [0.264172, 0.528344]
        """
        return self._handle_iterable_conversion(value, self._convert_volume_single, from_unit, to_unit)

    def _convert_speed_single(self, value, from_unit, to_unit):
        """Internal method for converting a single speed value."""
        # Convert to m/s
        if from_unit in self.metric_speed:
            ms = value * self.metric_speed_factors[from_unit]
        elif from_unit in self.non_metric_speed_to_ms:
            ms = value * self.non_metric_speed_to_ms[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # From m/s to target unit
        if to_unit in self.metric_speed:
            return ms / self.metric_speed_factors[to_unit]
        elif to_unit in self.non_metric_speed_to_ms:
            return ms / self.non_metric_speed_to_ms[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_speed(self, value, from_unit, to_unit):
        """
        Convert speed measurements between different units.

        Supports both metric units (mm/s, cm/s, m/s, km/h) and
        non-metric units (mph, knot, fps, mach).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_speed(100, "km/h", "m/s")
            27.7778
            >>> converter.convert_speed([60, 120], "mph", "km/h")
            [96.5606, 193.1212]
        """
        return self._handle_iterable_conversion(value, self._convert_speed_single, from_unit, to_unit)

    def _convert_energy_single(self, value, from_unit, to_unit):
        """Internal method for converting a single energy value."""
        # Convert to J
        if from_unit in self.metric_energy:
            j = value * self.metric_energy_factors[from_unit]
        elif from_unit in self.non_metric_energy_to_j:
            j = value * self.non_metric_energy_to_j[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # From J to target unit
        if to_unit in self.metric_energy:
            return j / self.metric_energy_factors[to_unit]
        elif to_unit in self.non_metric_energy_to_j:
            return j / self.non_metric_energy_to_j[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_energy(self, value, from_unit, to_unit):
        """
        Convert energy measurements between different units.

        Supports both metric units (J, kJ, MJ, GJ, TJ) and
        various energy units (cal, kcal, Wh, kWh, BTU, erg, foot_pound, electron_volt).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_energy(1000, "J", "kJ")
            1.0
            >>> converter.convert_energy([1, 2], "kWh", "J")
            [3600000.0, 7200000.0]
        """
        return self._handle_iterable_conversion(value, self._convert_energy_single, from_unit, to_unit)

    def _convert_pressure_single(self, value, from_unit, to_unit):
        """Internal method for converting a single pressure value."""
        # Convert to Pa
        if from_unit in self.metric_pressure:
            pa = value * self.metric_pressure_factors[from_unit]
        elif from_unit in self.non_metric_pressure_to_pa:
            pa = value * self.non_metric_pressure_to_pa[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # From Pa to target unit
        if to_unit in self.metric_pressure:
            return pa / self.metric_pressure_factors[to_unit]
        elif to_unit in self.non_metric_pressure_to_pa:
            return pa / self.non_metric_pressure_to_pa[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_pressure(self, value, from_unit, to_unit):
        """
        Convert pressure measurements between different units.

        Supports both metric units (Pa, hPa, kPa, MPa, GPa, bar, mbar) and
        various pressure units (atm, psi, mmHg, torr, inHg).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_pressure(1, "atm", "Pa")
            101325.0
            >>> converter.convert_pressure([1, 2], "bar", "psi")
            [14.5038, 29.0076]
        """
        return self._handle_iterable_conversion(value, self._convert_pressure_single, from_unit, to_unit)

    def _convert_power_single(self, value, from_unit, to_unit):
        """Internal method for converting a single power value."""
        # Convert to W
        if from_unit in self.metric_power:
            w = value * self.metric_power_factors[from_unit]
        elif from_unit in self.non_metric_power_to_w:
            w = value * self.non_metric_power_to_w[from_unit]
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # From W to target unit
        if to_unit in self.metric_power:
            return w / self.metric_power_factors[to_unit]
        elif to_unit in self.non_metric_power_to_w:
            return w / self.non_metric_power_to_w[to_unit]
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_power(self, value, from_unit, to_unit):
        """
        Convert power measurements between different units.

        Supports both metric units (W, kW, MW, GW, TW) and
        various power units (hp, metric_hp, BTU_per_hour).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation
            to_unit (str): Target unit abbreviation

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_power(1000, "W", "kW")
            1.0
            >>> converter.convert_power([1, 2], "hp", "W")
            [745.7, 1491.4]
        """
        return self._handle_iterable_conversion(value, self._convert_power_single, from_unit, to_unit)

    def _convert_temperature_single(self, value, from_unit, to_unit):
        """Internal method for converting a single temperature value."""
        # Supports: C, F, K, R (Rankine)
        if from_unit == to_unit:
            return value
        # Convert to Celsius
        if from_unit == "C":
            c = value
        elif from_unit == "F":
            c = (value - 32) * 5/9
        elif from_unit == "K":
            c = value - 273.15
        elif from_unit == "R":
            c = (value - 491.67) * 5/9
        else:
            raise ValueError(f"Source unit not supported: {from_unit}")
        # From Celsius to target unit
        if to_unit == "C":
            return c
        elif to_unit == "F":
            return c * 9/5 + 32
        elif to_unit == "K":
            return c + 273.15
        elif to_unit == "R":
            return (c + 273.15) * 9/5
        else:
            raise ValueError(f"Target unit not supported: {to_unit}")

    def convert_temperature(self, value, from_unit, to_unit):
        """
        Convert temperature measurements between different scales.

        Supports Celsius (C), Fahrenheit (F), Kelvin (K), and Rankine (R).

        Args:
            value: Number or iterable of numbers to convert
            from_unit (str): Source unit abbreviation (C, F, K, R)
            to_unit (str): Target unit abbreviation (C, F, K, R)

        Returns:
            Converted value(s) - single number if input was single number,
            list if input was iterable

        Examples:
            >>> converter = MetricFTW()
            >>> converter.convert_temperature(0, "C", "F")
            32.0
            >>> converter.convert_temperature([0, 100], "C", "K")
            [273.15, 373.15]
        """
        return self._handle_iterable_conversion(value, self._convert_temperature_single, from_unit, to_unit)

    def show_available_conversions(self, detailed=False):
        """
        Display all available conversion units organized by category.

        This method prints comprehensive information about all supported units
        for each measurement category (length, mass, area, volume, speed, energy,
        pressure, power, and temperature).

        Args:
            detailed (bool): If True, shows detailed descriptions for each unit.
                           If False (default), shows a compact list of units.

        Examples:
            >>> converter = MetricFTW()
            >>> converter.show_available_conversions()  # Shows compact view
            >>> converter.show_available_conversions(detailed=True)  # Shows detailed descriptions
        """

        # Unit descriptions for detailed view
        unit_descriptions = {
            # Length units
            "pm": "picometer - extremely small length, atomic scale measurements",
            "nm": "nanometer - wavelength of light, molecular dimensions",
            "um": "micrometer - microscopic measurements, cell biology",
            "mm": "millimeter - small precise measurements, engineering",
            "cm": "centimeter - everyday measurements, human scale",
            "dm": "decimeter - rarely used, 10 centimeters",
            "m": "meter - standard unit of length in SI system",
            "dam": "decameter - rarely used, 10 meters",
            "hm": "hectometer - rarely used, 100 meters",
            "km": "kilometer - long distances, geography",
            "inch": "inch - imperial unit, common in US measurements",
            "foot": "foot - imperial unit, human height, room dimensions",
            "yard": "yard - imperial unit, fabric, sports fields",
            "mile": "mile - long distances in imperial system",
            "nautical_mile": "nautical mile - maritime and aviation navigation",
            "angstrom": "angstrom - atomic and molecular dimensions",
            "mil": "mil - thousandth of an inch, thin materials",
            "furlong": "furlong - horse racing, old agricultural measurements",
            "fathom": "fathom - maritime depth measurements",
            "light_year": "light year - astronomical distances",
            "parsec": "parsec - astronomical unit for stellar distances",
            "astronomical_unit": "astronomical unit - Earth-Sun distance",

            # Mass units
            "pg": "picogram - microscopic particles, molecular masses",
            "ng": "nanogram - drug dosages, trace amounts",
            "ug": "microgram - pharmaceutical doses, pollutants",
            "mg": "milligram - medication doses, jewelry",
            "cg": "centigram - rarely used metric unit",
            "dg": "decigram - rarely used metric unit",
            "g": "gram - standard mass unit, cooking, science",
            "dag": "decagram - rarely used, 10 grams",
            "hg": "hectogram - rarely used, 100 grams",
            "kg": "kilogram - human weight, everyday objects",
            "t": "metric ton - heavy machinery, cargo",
            "ounce": "ounce - imperial mass, cooking in US",
            "pound": "pound - human weight in imperial system",
            "stone": "stone - human weight in UK (14 pounds)",
            "ton_us": "US ton - heavy cargo, 2000 pounds",
            "ton_uk": "UK ton - heavy cargo, 2240 pounds",
            "grain": "grain - bullets, precious metals (1/7000 pound)",
            "dram": "dram - apothecary weight, small quantities",
            "troy_ounce": "troy ounce - precious metals (gold, silver)",
            "carat": "carat - gemstone weight (200 milligrams)",
            "slug": "slug - physics unit related to acceleration",

            # Other categories would continue...
        }

        if not detailed:
            print("=== AVAILABLE UNIT CONVERSIONS ===")
            print("NOTE: You can convert from ANY unit to ANY other unit within the same category\n")

            all_length = list(self.metric_longitude) + list(self.non_metric_longitude_to_cm.keys())
            print("LENGTH (convert between any of these):")
            print(f"  All units: {', '.join(all_length)}\n")

            all_mass = list(self.metric_mass) + list(self.non_metric_mass_to_g.keys())
            print("MASS (convert between any of these):")
            print(f"  All units: {', '.join(all_mass)}\n")

            all_area = list(self.metric_area) + list(self.non_metric_area_to_m2.keys())
            print("AREA (convert between any of these):")
            print(f"  All units: {', '.join(all_area)}\n")

            all_volume = list(self.metric_volume) + list(self.non_metric_volume_to_l.keys())
            print("VOLUME (convert between any of these):")
            print(f"  All units: {', '.join(all_volume)}\n")

            all_speed = list(self.metric_speed) + list(self.non_metric_speed_to_ms.keys())
            print("SPEED (convert between any of these):")
            print(f"  All units: {', '.join(all_speed)}\n")

            all_energy = list(self.metric_energy) + list(self.non_metric_energy_to_j.keys())
            print("ENERGY (convert between any of these):")
            print(f"  All units: {', '.join(all_energy)}\n")

            all_pressure = list(self.metric_pressure) + list(self.non_metric_pressure_to_pa.keys())
            print("PRESSURE (convert between any of these):")
            print(f"  All units: {', '.join(all_pressure)}\n")

            all_power = list(self.metric_power) + list(self.non_metric_power_to_w.keys())
            print("POWER (convert between any of these):")
            print(f"  All units: {', '.join(all_power)}\n")

            print("TEMPERATURE (convert between any of these):")
            print(f"  All units: C (Celsius), F (Fahrenheit), K (Kelvin), R (Rankine)\n")
            return

        print("=== DETAILED UNIT CONVERSIONS WITH DESCRIPTIONS ===\n")

        print("LENGTH UNITS:")
        all_length = list(self.metric_longitude) + list(self.non_metric_longitude_to_cm.keys())
        for unit in all_length:
            if unit in unit_descriptions:
                print(f"  {unit}: {unit_descriptions[unit]}")
            else:
                print(f"  {unit}: length measurement unit")

        print("\nMASS UNITS:")
        all_mass = list(self.metric_mass) + list(self.non_metric_mass_to_g.keys())
        for unit in all_mass:
            if unit in unit_descriptions:
                print(f"  {unit}: {unit_descriptions[unit]}")
            else:
                print(f"  {unit}: mass measurement unit")

        print("\nAREA UNITS:")
        all_area = list(self.metric_area) + list(self.non_metric_area_to_m2.keys())
        area_descriptions = {
            "mm2": "square millimeter - tiny areas, precision measurements",
            "cm2": "square centimeter - small areas, everyday measurements",
            "dm2": "square decimeter - moderate areas, rarely used",
            "m2": "square meter - standard area unit, room sizes",
            "dam2": "square decameter - large areas, rarely used",
            "hm2": "square hectometer - very large areas, equivalent to hectare",
            "km2": "square kilometer - geographical areas, cities",
            "sqin": "square inch - small areas in imperial system",
            "sqft": "square foot - room areas, real estate in US",
            "sqyd": "square yard - fabric, carpeting, sports fields",
            "acre": "acre - agricultural land, real estate",
            "hectare": "hectare - agricultural land, 10,000 m²",
            "sqmile": "square mile - large geographical areas",
            "barn": "barn - nuclear cross-sections (very tiny area)",
            "are": "are - 100 square meters, rarely used",
            "rood": "rood - old agricultural unit, quarter acre"
        }
        for unit in all_area:
            desc = area_descriptions.get(unit, "area measurement unit")
            print(f"  {unit}: {desc}")

        print("\nVOLUME UNITS:")
        all_volume = list(self.metric_volume) + list(self.non_metric_volume_to_l.keys())
        volume_descriptions = {
            "mm3": "cubic millimeter - tiny volumes",
            "cm3": "cubic centimeter - small volumes, medical doses",
            "dm3": "cubic decimeter - equivalent to liter",
            "m3": "cubic meter - standard volume unit, room volumes",
            "l": "liter - everyday liquid measurements",
            "ml": "milliliter - small liquid amounts, medicine",
            "cl": "centiliter - rarely used, 10 milliliters",
            "dl": "deciliter - rarely used, 100 milliliters",
            "gallon_us": "US gallon - fuel, large liquid containers",
            "gallon_uk": "UK gallon - larger than US gallon",
            "quart": "quart - cooking, quarter of a gallon",
            "pint": "pint - beverages, half a quart",
            "cup": "cup - cooking measurements",
            "fluid_ounce": "fluid ounce - small liquid measurements",
            "cubic_inch": "cubic inch - small volumes in imperial",
            "tablespoon": "tablespoon - cooking, 15 milliliters",
            "teaspoon": "teaspoon - cooking, 5 milliliters",
            "barrel_oil": "oil barrel - petroleum industry standard",
            "bushel": "bushel - agricultural dry goods"
        }
        for unit in all_volume:
            desc = volume_descriptions.get(unit, "volume measurement unit")
            print(f"  {unit}: {desc}")

        print("\nSPEED UNITS:")
        all_speed = list(self.metric_speed) + list(self.non_metric_speed_to_ms.keys())
        speed_descriptions = {
            "m/s": "meters per second - scientific measurements",
            "km/h": "kilometers per hour - vehicle speeds",
            "mph": "miles per hour - vehicle speeds in US/UK",
            "knot": "knot - maritime and aviation speeds",
            "fps": "feet per second - projectile speeds",
            "mach": "mach number - supersonic speeds relative to sound"
        }
        for unit in all_speed:
            desc = speed_descriptions.get(unit, "speed measurement unit")
            print(f"  {unit}: {desc}")

        print("\nENERGY UNITS:")
        all_energy = list(self.metric_energy) + list(self.non_metric_energy_to_j.keys())
        energy_descriptions = {
            "J": "joule - standard energy unit",
            "kJ": "kilojoule - food energy, 1000 joules",
            "cal": "calorie - food energy, heat",
            "kcal": "kilocalorie - food Calories (capital C)",
            "Wh": "watt-hour - electrical energy consumption",
            "kWh": "kilowatt-hour - household electricity bills",
            "BTU": "British thermal unit - heating/cooling",
            "erg": "erg - very small energy unit in CGS system",
            "foot_pound": "foot-pound - mechanical work in imperial",
            "electron_volt": "electron volt - atomic and particle physics"
        }
        for unit in all_energy:
            desc = energy_descriptions.get(unit, "energy measurement unit")
            print(f"  {unit}: {desc}")

        print("\nPRESSURE UNITS:")
        all_pressure = list(self.metric_pressure) + list(self.non_metric_pressure_to_pa.keys())
        pressure_descriptions = {
            "Pa": "pascal - standard pressure unit",
            "kPa": "kilopascal - moderate pressures",
            "bar": "bar - atmospheric pressure, weather",
            "atm": "atmosphere - standard atmospheric pressure",
            "psi": "pounds per square inch - tire pressure, US",
            "mmHg": "millimeters of mercury - blood pressure",
            "torr": "torr - vacuum measurements, same as mmHg",
            "inHg": "inches of mercury - barometric pressure"
        }
        for unit in all_pressure:
            desc = pressure_descriptions.get(unit, "pressure measurement unit")
            print(f"  {unit}: {desc}")

        print("\nPOWER UNITS:")
        all_power = list(self.metric_power) + list(self.non_metric_power_to_w.keys())
        power_descriptions = {
            "W": "watt - standard power unit",
            "kW": "kilowatt - household appliances",
            "MW": "megawatt - power plants, large facilities",
            "hp": "horsepower - engine power, mechanical",
            "metric_hp": "metric horsepower - slightly different from hp",
            "BTU_per_hour": "BTU per hour - heating/cooling capacity"
        }
        for unit in all_power:
            desc = power_descriptions.get(unit, "power measurement unit")
            print(f"  {unit}: {desc}")

        print("\nTEMPERATURE UNITS:")
        temp_descriptions = {
            "C": "Celsius - water freezes at 0°, boils at 100°",
            "F": "Fahrenheit - water freezes at 32°, boils at 212°",
            "K": "Kelvin - absolute temperature scale, starts at absolute zero",
            "R": "Rankine - absolute scale using Fahrenheit degrees"
        }
        for unit, desc in temp_descriptions.items():
            print(f"  {unit}: {desc}")

        print("\nNOTE: You can convert from ANY unit to ANY other unit within the same category!")

if __name__ == "__main__":
    converter = MetricFTW()
    converter.show_available_conversions(detailed=True)