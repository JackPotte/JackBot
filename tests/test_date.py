import date

def test_date_formats():
    for formatName in date.formats.keys():
        yield date.testMapEntry, formatName, False

test_date_formats.slow = True
