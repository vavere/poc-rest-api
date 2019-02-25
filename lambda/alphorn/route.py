import re


class RouteEntry:
    _PARAMS = re.compile(r'{\w+}')

    def __init__(self, view_func, name, path, method, cors):
        self.view_func = view_func
        self.name = name

        # order matters! parse_view_args uses path and parse_pattern uses view_args
        self.path = path
        self.view_args = self._parse_view_args()
        self.pattern = self._parse_pattern()

        self.method = method
        self.cors = cors

    def _parse_view_args(self):
        """derive view function arguments from path
        blatantly stolen from Chalice, thanks guys

        :return: list of view function args extracted from path
        :rtype: list
        """
        if '{' not in self.path:
            return []
        # The [1:-1] slice is to remove the braces e.g {foobar} -> foobar
        results = [r[1:-1] for r in self._PARAMS.findall(self.path)]
        return results

    def _parse_pattern(self):
        """transforms a path with params to a regex string to be used for matching
        """
        pattern = f'^{self.path}$'
        for arg in self.view_args:
            # transform /sample/{greeting} to /sample/(?P<greeting>.*?)
            pattern = pattern.replace(f'{{{arg}}}', f'(?P<{arg}>[^/]*?)')
        return pattern

    def match(self, path):
        """returns true or false if path is allowed by self.path

        where self.path == /sample/{greeting}
        while path == /sample/1234

        :param path: path to be matched
        :type path: string
        """
        return re.match(self.pattern, path, re.I)
