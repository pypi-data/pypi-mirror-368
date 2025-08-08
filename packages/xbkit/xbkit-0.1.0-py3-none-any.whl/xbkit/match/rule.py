class MatchRule:
    def __init__(self, rule: list[list[str]]):
        self.rule = rule
        pass

    def match(self, val: str) -> bool:
        for rule_item in self.rule:
            if not any(v in val for v in rule_item):
                return False
        return True
