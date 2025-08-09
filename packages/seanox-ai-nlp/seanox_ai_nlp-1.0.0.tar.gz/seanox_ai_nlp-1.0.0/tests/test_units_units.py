# tests/test_units_units.py

from seanox_ai_nlp.units import units
from typing import Optional, NamedTuple

import pytest
import os


class Unit(NamedTuple):
    label: str
    start: int
    end: int
    text: str
    categories: tuple[str, ...]
    unit: str
    value: Optional[str] = None


@pytest.mark.parametrize("text", [(
    "Die Batterie h\u00e4lt ca. 10h bei \u221220.5 \u00b0C."
    "Das Solarpanel produziert etwa 1.2 \u00d7 10^3W unter optimalen Bedingungen."
    "Mit einem Gewicht von \u223c2.3 kg ist das Ger\u00e4t leicht tragbar."
    "Der Reifendruck liegt bei 2500hPa, empfohlen sind aber nur 2.5 bar."
    "Die Entfernung zum n\u00e4chsten Ladepunkt betr\u00e4gt rund 18 km, bei einer Durchschnittsgeschwindigkeit von 50km/h."
    "Einige Nutzer berichten sogar von 21.5kWh Verbrauch auf 100km."

    "Die Verpackung hat Ma\u00dfe von 35\u00d722\u00d712 cm und ein Volumen von ca. 9.24 l."
    "Der L\u00fcfter erzeugt 34dB Ger\u00e4uschpegel unter Last."
    "Laut Hersteller betr\u00e4gt die Akkulaufzeit 12\u201314 h je nach Nutzung."
    "Das Ger\u00e4t arbeitet in einem Temperaturbereich zwischen \u221210 \u00b0C und +45 \u00b0C."
    "Der Stromverbrauch liegt bei max. 65 W, die Ladezeit bei 3.5h \u00fcber ein Netzteil mit 20V und 3.25A."
    "Die GPS-Genauigkeit betr\u00e4gt etwa \u00b15 m."
    "Bei Windst\u00e4rken \u00fcber 60 km/h sollte das Ger\u00e4t gesichert werden."

    "Das Plato befand sich auf 550 m H\u00f6he bei einem relativen Luftdruck von 960hPa."
    "Die Signalreichweite lag bei bis zu 120 m auf freier Fl\u00e4che."
    "Nach dem Update verbesserte sich die Bootzeit um 2.3 s, und die durchschnittliche CPU-Temperatur sank auf 36.5 \u00b0C."
    "Die Ladegeschwindigkeit wurde mit 0.8C angegeben."
    "Der Preis liegt aktuell bei etwa 299.99 \u20ac."

    "Das Display misst 15.6 \" bei einer Aufl\u00f6sung von 1920\u00d71080 px."
    "Ein Node vom Kubernetes-Cluster mind. benötigt 1vCore und 512MiB."

    "Das Produkt misst 10\u00d720\u00d730 cm und hat ein Volumen von 6 l."
    "Der Energiebedarf liegt bei ca. 5 - 10 kWh"
    "Der Durchmesser misst ca. 1\u002d11nm (Hyphen-Minus)"
    "Der Durchmesser misst ca. 2 \u2013 22nm (En Dash)"
    "Der Durchmesser misst ca. 3\u2014 33nm (Em Dash)"
    "Der Durchmesser misst ca. 4 \u221244nm (Minus Sign)"

    "Die Difference betr\u00e4gt ca. \u002d11nm (Hyphen-Minus)"
    "Die Difference betr\u00e4gt ca. \u2013 22nm (En Dash)"
    "Die Difference betr\u00e4gt ca. \u2014 33nm (Em Dash)"
    "Die Difference betr\u00e4gt ca. \u221244nm (Minus Sign)"
)])
def test_units_01(text):
    expected = [
        Unit(label='UNIT-VALUE', start=22, end=25, text='10h', categories=('time',), unit='h', value='10'),
        Unit(label='UNIT', start=37, end=38, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT-VALUE', start=70, end=81, text='1.2 × 10^3W', categories=('power',), unit='W', value='1.2 × 10^3'),
        Unit(label='UNIT-VALUE', start=133, end=139, text='2.3 kg', categories=('mass',), unit='kg', value='2.3'),
        Unit(label='UNIT', start=144, end=147, text='das', categories=('time',), unit='das', value=None),
        Unit(label='UNIT-VALUE', start=195, end=202, text='2500hPa', categories=('time',), unit='hPa', value='2500'),
        Unit(label='UNIT-VALUE', start=228, end=235, text='2.5 bar', categories=('pressure',), unit='bar', value='2.5'),
        Unit(label='UNIT-VALUE', start=287, end=292, text='18 km', categories=('length',), unit='km', value='18'),
        Unit(label='UNIT-VALUE', start=337, end=343, text='50km/h', categories=('length', 'time'), unit='km/h', value='50'),
        Unit(label='UNIT-VALUE', start=378, end=385, text='21.5kWh', categories=('energy',), unit='kWh', value='21.5'),
        Unit(label='UNIT-VALUE', start=400, end=405, text='100km', categories=('length',), unit='km', value='100'),
        Unit(label='UNIT-VALUE', start=434, end=445, text='35×22×12 cm', categories=('length',), unit='cm', value='35×22×12'),
        Unit(label='UNIT-VALUE', start=470, end=476, text='9.24 l', categories=('volume',), unit='l', value='9.24'),
        Unit(label='UNIT-VALUE', start=496, end=500, text='34dB', categories=('acoustics', 'it', 'storage'), unit='dB', value='34'),
        Unit(label='UNIT-VALUE', start=567, end=574, text='12–14 h', categories=('time',), unit='h', value='12–14'),
        Unit(label='UNIT', start=610, end=612, text='in', categories=('length',), unit='in', value=None),
        Unit(label='UNIT', start=651, end=652, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT', start=662, end=663, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT-VALUE', start=698, end=702, text='65 W', categories=('power',), unit='W', value='65'),
        Unit(label='UNIT-VALUE', start=721, end=725, text='3.5h', categories=('time',), unit='h', value='3.5'),
        Unit(label='UNIT-VALUE', start=748, end=751, text='20V', categories=('electricity',), unit='V', value='20'),
        Unit(label='UNIT-VALUE', start=795, end=799, text='±5 m', categories=('length',), unit='m', value='±5'),
        Unit(label='UNIT-VALUE', start=821, end=828, text='60 km/h', categories=('length', 'time'), unit='km/h', value='60'),
        Unit(label='UNIT', start=836, end=839, text='das', categories=('time',), unit='das', value=None),
        Unit(label='UNIT-VALUE', start=889, end=894, text='550 m', categories=('length',), unit='m', value='550'),
        Unit(label='UNIT-VALUE', start=934, end=940, text='960hPa', categories=('time',), unit='hPa', value='960'),
        Unit(label='UNIT-VALUE', start=977, end=982, text='120 m', categories=('length',), unit='m', value='120'),
        Unit(label='UNIT-VALUE', start=1050, end=1055, text='2.3 s', categories=('time',), unit='s', value='2.3'),
        Unit(label='UNIT', start=1113, end=1114, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT-VALUE', start=1149, end=1153, text='0.8C', categories=('electricity',), unit='C', value='0.8'),
        Unit(label='UNIT-VALUE', start=1255, end=1267, text='1920×1080 px', categories=('graphics', 'it'), unit='px', value='1920×1080'),
        Unit(label='UNIT-VALUE', start=1315, end=1321, text='1vCore', categories=('amount', 'it', 'processing'), unit='vCore', value='1'),
        Unit(label='UNIT-VALUE', start=1326, end=1332, text='512MiB', categories=('acoustics', 'it', 'storage'), unit='MiB', value='512'),
        Unit(label='UNIT-VALUE', start=1351, end=1362, text='10×20×30 cm', categories=('length',), unit='cm', value='10×20×30'),
        Unit(label='UNIT-VALUE', start=1387, end=1390, text='6 l', categories=('volume',), unit='l', value='6'),
        Unit(label='UNIT-VALUE', start=1459, end=1465, text='1-11nm', categories=('length',), unit='nm', value='1-11'),
        Unit(label='UNIT-VALUE', start=1506, end=1514, text='2 – 22nm', categories=('length',), unit='nm', value='2 – 22'),
        Unit(label='UNIT-VALUE', start=1550, end=1557, text='3— 33nm', categories=('length',), unit='nm', value='3— 33'),
        Unit(label='UNIT', start=1559, end=1561, text='Em', categories=('length',), unit='Em', value=None),
        Unit(label='UNIT-VALUE', start=1593, end=1600, text='4 −44nm', categories=('length',), unit='nm', value='4 −44'),
        Unit(label='UNIT-VALUE', start=1640, end=1645, text='-11nm', categories=('length',), unit='nm', value='-11'),
        Unit(label='UNIT-VALUE', start=1689, end=1693, text='22nm', categories=('length',), unit='nm', value='22'),
        Unit(label='UNIT-VALUE', start=1732, end=1736, text='33nm', categories=('length',), unit='nm', value='33'),
        Unit(label='UNIT', start=1738, end=1740, text='Em', categories=('length',), unit='Em', value=None),
        Unit(label='UNIT-VALUE', start=1774, end=1778, text='44nm', categories=('length',), unit='nm', value='44'),
    ]
    actual = [
        Unit(
            label=entity.label,
            start=entity.start,
            end=entity.end,
            text=entity.text,
            categories=entity.categories,
            unit=entity.unit,
            value=entity.value
        )
        for entity in units(text)
    ]
    print()
    print(f",{os.linesep}".join([str(unit) for unit in actual]))
    assert actual == expected, f"\nExpected:\n{expected}\n\nGot:\n{actual}"


@pytest.mark.parametrize("text", [(
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph)."
    "It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)])
def test_units_02(text):
    expected = [
        Unit(label='UNIT-VALUE', start=54, end=68, text='900 - 950 km/h', categories=('length', 'time'), unit='km/h', value='900 - 950'),
        Unit(label='UNIT-VALUE', start=70, end=77, text='559 mph', categories=('length',), unit='mph', value='559'),
        Unit(label='UNIT', start=105, end=107, text='in', categories=('length',), unit='in', value=None),
        Unit(label='UNIT', start=129, end=133, text='km/h', categories=('length', 'time'), unit='km/h', value=None),
        Unit(label='UNIT', start=155, end=158, text='mph', categories=('length',), unit='mph', value=None)
    ]
    actual = [
        Unit(
            label=entity.label,
            start=entity.start,
            end=entity.end,
            text=entity.text,
            categories=entity.categories,
            unit=entity.unit,
            value=entity.value
        )
        for entity in units(text)
    ]
    print()
    print(f",{os.linesep}".join([str(unit) for unit in actual]))
    assert actual == expected, f"\nExpected:\n{expected}\n\nGot:\n{actual}"
