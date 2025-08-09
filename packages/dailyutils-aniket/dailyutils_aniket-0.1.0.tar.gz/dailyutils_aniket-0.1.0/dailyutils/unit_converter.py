def convert_length(value, from_unit, to_unit):
    units = {
        'm': 1,
        'km': 1000,
        'cm': 0.01,
        'mm': 0.001,
        'mile': 1609.34,
        'yard': 0.9144,
        'foot': 0.3048,
        'inch': 0.0254
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit not in units or to_unit not in units:
        raise ValueError("Unsupported length unit")

    meters = value * units[from_unit]
    return meters / units[to_unit]


def convert_weight(value, from_unit, to_unit):
    units = {
        'kg': 1,
        'g': 0.001,
        'mg': 0.000001,
        'lb': 0.453592,
        'oz': 0.0283495
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit not in units or to_unit not in units:
        raise ValueError("Unsupported weight unit")

    kg = value * units[from_unit]
    return kg / units[to_unit]


def convert_temperature(value, from_unit, to_unit):
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return value

    if from_unit == 'c':
        if to_unit == 'f':
            return (value * 9/5) + 32
        elif to_unit == 'k':
            return value + 273.15
    elif from_unit == 'f':
        if to_unit == 'c':
            return (value - 32) * 5/9
        elif to_unit == 'k':
            return (value - 32) * 5/9 + 273.15
    elif from_unit == 'k':
        if to_unit == 'c':
            return value - 273.15
        elif to_unit == 'f':
            return (value - 273.15) * 9/5 + 32

    raise ValueError("Unsupported temperature conversion")
