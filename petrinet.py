class Petrinet:
    """
    A class representing a Petri net.
    """

    def __init__(self) -> None:
        """
        Initialize the Petri net with default values.
        """
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


    def update_net(self, m: list[int], t: list[tuple[tuple[int, ...], tuple[int, ...]]]) -> None:
        """
        Update the Petri net with a new marking and transitions.

        Args:
            m: The initial marking of the Petri net.
            t: The transitions of the Petri net.
        """
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
        """
        Change the number of tokens in a specific place.

        Args:
            amount: The amount to change the tokens by.
            place: The index of the place to change.

        Returns:
            True if the change was successful, False otherwise.
        """
        if 0 <= place < self.places and self.mark[place] + amount >= 0:
            self.mark[place] += amount
            self.initial_mark = tuple(self.mark)
            return True
        return False

    def set_mark(self, new_mark: list[int]) -> None:
        """
        Set the marking of the Petri net to a new marking.

        Args:
            new_mark: The new marking to set.
        """
        for i in range(len(self.mark)):
            self.mark[i] = new_mark[i]

    def fire_trans(self, t_id: int) -> bool:
        """
        Fire a transition if it is enabled.

        Args:
            t_id: The ID of the transition to fire.

        Returns:
            True if the transition was fired, False otherwise.
        """
        if t_id not in self.ids:
            return False
        t_pre, t_post = self.ids[t_id]
        tmp = tuple(p1 - p2 for p1, p2 in zip(self.mark, t_pre))
        if self._valid_mark(tmp):
            self.mark = [p1 + p2 for p1, p2 in zip(tmp, t_post)]
            return True
        else: return False

    def analysis(self) -> None:
        """
        Analyze the Petri net to build the reachability graph and check for boundedness.
        """
        visit = set()
        path = []
        self.mark = list(self.initial_mark)
        self.g = {}
        self.marks = 0
        self.edges = 0
        self.bounded = None
        self.m_null = None
        self.m_last = None

        def dfs(mark: tuple[int, ...]) -> bool:
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
    def _valid_mark(mark: tuple[int, ...]) -> bool:
        """
        Check if a marking is valid (all places have non-negative tokens and <= 10000).

        Args:
            mark: The marking to check.

        Returns:
            True if the marking is valid, False otherwise.
        """
        if any((p < 0 or p > 10000) for p in mark):
            return False
        return True

    @staticmethod
    def _a_greater_b(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
        """
        Check if marking a is strictly greater than marking b.

        Args:
            a: The first marking.
            b: The second marking.

        Returns:
            True if a > b, False otherwise.
        """
        one_greater = False
        for ai, bi in zip(a, b):
            if bi > ai:
                return False
            if ai > bi:
                one_greater = True
        return one_greater

    def _infinite(self, path: list[tuple[int, ...]], mark: tuple[int, ...]) -> bool:
        """
        Check if the current path leads to an infinite marking (unbounded).

        Args:
            path: The current path of markings in the DFS.
            mark: The current marking.

        Returns:
            True if an infinite marking is detected, False otherwise.
        """
        for prev_mark in path:
            if self._a_greater_b(mark, prev_mark):
                self.m_null = prev_mark
                self.m_last = mark
                return True
        return False