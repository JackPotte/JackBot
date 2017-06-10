import os
transpath = os.path.join(os.path.split(__file__)[0], '..', 'userinterfaces', 'transliteration.py')
import imp
transliteration = imp.load_source('transliteration', transpath)

def test_different_encodings():
    encodings="""ascii
    big5
    cp874
    cp932
    cp936
    cp949
    cp950
    cp1250
    cp1251
    cp1252
    cp1253
    cp1254
    cp1255
    cp1256
    cp1257
    cp1258
    gb18030
    latin_1
    utf_8"""
    encodings = [x.strip() for x in encodings.split()]
    for encoding in encodings:
        yield check_transliteration, encoding

def check_transliteration(encoding):
    tler = transliteration.transliterator(encoding)
        
