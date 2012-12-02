class matrix(object):
    def __init__(self, *dims):
        self._shortcuts = [i for i in self._create_shortcuts(dims)]
        self._li = [None] * (self._shortcuts.pop())
        self._shortcuts.reverse()

    def _create_shortcuts(self, dims):
        dimList = list(dims)
        dimList.reverse()
        number = 1
        yield 1
        for i in dimList:
            number *= i
            yield number

    def _flat_index(self, index):
        if len(index) != len(self._shortcuts):
            raise TypeError()

        flatIndex = 0
        for i, num in enumerate(index):
            flatIndex += num * self._shortcuts[i]
        return flatIndex

    def __getitem__(self, index):
        return self._li[self._flat_index(index)]

    def __setitem__(self, index, value):
        self._li[self._flat_index(index)] = value
