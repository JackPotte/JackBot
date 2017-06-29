import collections

def rec_anagram(counter):
    if sum(counter.values()) == 0:
        yield ''
    else:
        for c in counter:
            if counter[c] != 0:
                counter[c] -= 1
                for _ in rec_anagram(counter):
                    yield c + _
                counter[c] += 1

def anagram(word):
    return rec_anagram(collections.Counter(word))

anagrammes = anagram(u'Utilisateur:JackBot/test')
for c in anagrammes:
	print c