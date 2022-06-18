import tableaux.utils.multiset as multiset


class TlSet:
    def __init__(self, tl_set=None, tl_multiset=None, full_set=None, full_multiset=None):
        self.set = tl_set if tl_set else set()
        self.multiset = tl_multiset if tl_multiset else multiset.Multiset()

        self.full_set = full_set if full_set else set()
        self.full_multiset = full_multiset if full_multiset else multiset.Multiset()

    def __contains__(self, element):
        return element in self.set

    def __len__(self):
        return len(self.set)

    def __iter__(self):
        return iter(self.set)

    def pop(self):
        selected_element = self.set.pop()
        self.multiset.pop(selected_element)
        return selected_element

    def add(self, element, multiplicity=1):
        self.set.add(element)
        self.multiset.add(element, multiplicity)

    def remove(self, element, multiplicity=1):
        self.multiset.remove(element, multiplicity)
        if element not in self.multiset:
            self.set.remove(element)

    def discard(self, element, multiplicity=1):
        self.multiset.discard(element, multiplicity)
        if element not in self.multiset:
            self.set.discard(element)

    def copy(self):
        return TlSet(self.set.copy(), self.multiset.copy())




if __name__ == '__main__':
    tl_set = TlSet()
    tl_set.add('a')
    tl_set.add('a')
    tl_set.add('b')
    print(tl_set.set)
    print(tl_set.multiset)
