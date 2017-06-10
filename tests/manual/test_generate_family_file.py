if __name__ != "__main__":
    raise Exception("generate_family_file can only be tested using the manual test runner due to monkey patching")

import sys, os
sys.path.append(os.getcwd())

from generate_family_file import FamilyFileGenerator
try:
  os.remove('families/test_family.py')
except Exception:
  pass
FamilyFileGenerator('http://nl.wikipedia.org/wiki/Hoofdpagina', 'test').run()
os.remove('families/test_family.py')
#FamilyFileGenerator('https://nl.wikipedia.org/wiki/Hoofdpagina', 'test').run()
#os.remove('families/test_family.py')
FamilyFileGenerator('http://techessentials.org/wiki/Main_Page', 'test').run()
os.remove('families/test_family.py')
FamilyFileGenerator('http://botwiki.sno.cc/wiki/Main_Page', 'test').run()
os.remove('families/test_family.py')

