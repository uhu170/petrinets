class Petrinet:

    def __init__(self) -> None:
        self.trans = None
        self.mark = None
        self.initial_mark = None
        self.places = None
        self.g = None
        self.bounded = None
        self.m_null = None
        self.m_last = None
        self.ids = None
        self.marks = None
        self.edges = None


    def update_net(self, m, t) -> None:
        self.trans = t
        self.mark = m
        self.initial_mark = tuple(m)
        self.places = len(m)
        self.g = {}
        self.bounded = None
        self.m_null = None
        self.m_last = None
        self.marks = 0
        self.edges = 0

        self.ids = {}
        for i, tr in enumerate(self.trans):
            self.ids[self.places + i] = tr

    def change_mark(self, amount: int, place: int) -> bool:
        if 0 <= place < self.places and self.mark[place] + amount >= 0:
            self.mark[place] += amount
            self.initial_mark = tuple(self.mark)
            return True
        return False

    def set_mark(self, new_mark):
        for i in range(len(self.mark)):
            self.mark[i] = new_mark[i]

    def fire_trans(self, t_id) -> bool:
        if t_id not in self.ids:
            return False
        t_pre, t_post = self.ids[t_id]
        tmp = tuple(p1 - p2 for p1, p2 in zip(self.mark, t_pre))
        if self._valid_mark(tmp):
            self.mark = [p1 + p2 for p1, p2 in zip(tmp, t_post)]
            return True
        else: return False

    def analysis(self) -> None:
        visit = set()
        path = []
        self.mark = list(self.initial_mark)
        self.g = {}
        self.marks = 0
        self.edges = 0
        self.bounded = None
        self.m_null = None
        self.m_last = None

        def dfs(mark) -> bool:
            mark = tuple(mark)
            if mark in visit:
                return True
            visit.add(mark)

            if self._infinite(path, mark):
                return False

            path.append(mark)
            self.g[mark] = set()
            self.marks += 1
            for i, t in enumerate(self.trans):
                t_pre, t_post = t
                tmp = tuple(p1 - p2 for p1, p2 in zip(mark, t_pre))
                if self._valid_mark(tmp):
                    tmp = tuple(p1 + p2 for p1, p2 in zip(tmp, t_post))
                    self.g[mark].add((tmp, i))
                    self.edges += 1
                    if not dfs(tmp):
                        return False
            path.pop()
            return True


        if dfs(self.mark):
            self.bounded = True
        else:
            self.bounded = False


    @staticmethod
    def _valid_mark(mark) -> bool:
        if any((p < 0 or p > 10000) for p in mark):
            return False
        return True

    @staticmethod
    def _a_greater_b(a, b) -> bool:
        one_greater = False
        for ai, bi in zip(a, b):
            if bi > ai:
                return False
            if ai > bi:
                one_greater = True
        return one_greater

    def _infinite(self, path, mark) -> bool:
        for prev_mark in path:
            if self._a_greater_b(mark, prev_mark):
                self.m_null = prev_mark
                self.m_last = mark
                return True
        return False