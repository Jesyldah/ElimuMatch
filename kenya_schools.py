"""
Kenya secondary school catalog for Elimu Match PoC.

One sample school per county (all 47) so the sponsor portal is nationally
representative and not limited to a subset of counties.
"""

from __future__ import annotations

# school_id → name, county, Day/Boarding
# IDs 1–20 preserve the original cohort schools; 21–47 cover remaining counties.
SCHOOLS: dict[int, dict[str, str]] = {
    # —— Original 20 ——
    1:  {'name': 'Kilimani Day Secondary', 'county': 'Nairobi', 'type': 'Day'},
    2:  {'name': 'Nyandarua Mixed Secondary', 'county': 'Nyandarua', 'type': 'Boarding'},
    3:  {'name': 'Kisumu Lakeside Secondary', 'county': 'Kisumu', 'type': 'Day'},
    4:  {'name': 'Machakos Hilltop Secondary', 'county': 'Machakos', 'type': 'Boarding'},
    5:  {'name': 'Nakuru Valley Secondary', 'county': 'Nakuru', 'type': 'Day'},
    6:  {'name': 'Mombasa Coast Secondary', 'county': 'Mombasa', 'type': 'Day'},
    7:  {'name': 'Eldoret Highlands Secondary', 'county': 'Uasin Gishu', 'type': 'Boarding'},
    8:  {'name': 'Thika Green Secondary', 'county': 'Kiambu', 'type': 'Day'},
    9:  {'name': 'Kakamega Forest Secondary', 'county': 'Kakamega', 'type': 'Boarding'},
    10: {'name': 'Nyeri Ridge Secondary', 'county': 'Nyeri', 'type': 'Boarding'},
    11: {'name': 'Kitale Plains Secondary', 'county': 'Trans Nzoia', 'type': 'Day'},
    12: {'name': 'Garissa Horizon Secondary', 'county': 'Garissa', 'type': 'Boarding'},
    13: {'name': 'Meru Mountain Secondary', 'county': 'Meru', 'type': 'Boarding'},
    14: {'name': 'Bungoma West Secondary', 'county': 'Bungoma', 'type': 'Day'},
    15: {'name': 'Embu Sunrise Secondary', 'county': 'Embu', 'type': 'Day'},
    16: {'name': 'Kericho Highlands Secondary', 'county': 'Kericho', 'type': 'Boarding'},
    17: {'name': 'Malindi Shore Secondary', 'county': 'Kilifi', 'type': 'Day'},
    18: {'name': 'Narok Savannah Secondary', 'county': 'Narok', 'type': 'Boarding'},
    19: {'name': 'Isiolo North Secondary', 'county': 'Isiolo', 'type': 'Boarding'},
    20: {'name': 'Busia Border Secondary', 'county': 'Busia', 'type': 'Day'},
    # —— Remaining counties (21–47) ——
    21: {'name': 'Kabarnet Rift Secondary', 'county': 'Baringo', 'type': 'Boarding'},
    22: {'name': 'Bomet Tea Highlands Secondary', 'county': 'Bomet', 'type': 'Day'},
    23: {'name': 'Iten Escarpment Secondary', 'county': 'Elgeyo-Marakwet', 'type': 'Boarding'},
    24: {'name': 'Homa Bay Lakeside Secondary', 'county': 'Homa Bay', 'type': 'Day'},
    25: {'name': 'Kajiado Plains Secondary', 'county': 'Kajiado', 'type': 'Boarding'},
    26: {'name': 'Kerugoya Valley Secondary', 'county': 'Kirinyaga', 'type': 'Day'},
    27: {'name': 'Kisii Highlands Secondary', 'county': 'Kisii', 'type': 'Boarding'},
    28: {'name': 'Kitui East Secondary', 'county': 'Kitui', 'type': 'Day'},
    29: {'name': 'Kwale Coast Secondary', 'county': 'Kwale', 'type': 'Day'},
    30: {'name': 'Nanyuki Plateau Secondary', 'county': 'Laikipia', 'type': 'Boarding'},
    31: {'name': 'Lamu Island Secondary', 'county': 'Lamu', 'type': 'Day'},
    32: {'name': 'Wote Ukambani Secondary', 'county': 'Makueni', 'type': 'Day'},
    33: {'name': 'Mandera Frontier Secondary', 'county': 'Mandera', 'type': 'Boarding'},
    34: {'name': 'Marsabit Desert Secondary', 'county': 'Marsabit', 'type': 'Boarding'},
    35: {'name': 'Migori River Secondary', 'county': 'Migori', 'type': 'Day'},
    36: {'name': 'Murang\'a Hills Secondary', 'county': 'Murang\'a', 'type': 'Day'},
    37: {'name': 'Kapsabet Nandi Secondary', 'county': 'Nandi', 'type': 'Boarding'},
    38: {'name': 'Nyamira Highlands Secondary', 'county': 'Nyamira', 'type': 'Day'},
    39: {'name': 'Maralal Samburu Secondary', 'county': 'Samburu', 'type': 'Boarding'},
    40: {'name': 'Siaya Lakeside Secondary', 'county': 'Siaya', 'type': 'Day'},
    41: {'name': 'Voi Taita Secondary', 'county': 'Taita-Taveta', 'type': 'Boarding'},
    42: {'name': 'Hola Tana Secondary', 'county': 'Tana River', 'type': 'Day'},
    43: {'name': 'Chuka Tharaka Secondary', 'county': 'Tharaka-Nithi', 'type': 'Day'},
    44: {'name': 'Lodwar Turkana Secondary', 'county': 'Turkana', 'type': 'Boarding'},
    45: {'name': 'Mbale Vihiga Secondary', 'county': 'Vihiga', 'type': 'Day'},
    46: {'name': 'Wajir North Secondary', 'county': 'Wajir', 'type': 'Boarding'},
    47: {'name': 'Kapenguria West Pokot Secondary', 'county': 'West Pokot', 'type': 'Boarding'},
}

N_SCHOOLS = len(SCHOOLS)
assert N_SCHOOLS == 47, f'Expected 47 schools, got {N_SCHOOLS}'
assert len({m['county'] for m in SCHOOLS.values()}) == 47, 'Each county must appear exactly once'


def counties() -> list[str]:
    return sorted({m['county'] for m in SCHOOLS.values()})
