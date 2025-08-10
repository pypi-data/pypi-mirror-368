import yaml
import json

class RuleChecker:
    def __init__(self, rules_path):
        with open(rules_path, 'r') as f:
            if rules_path.endswith('.json'):
                self.rules = json.load(f)
            else:
                self.rules = yaml.safe_load(f)

    def check_constant(self, row):
        broken = []
        for rule in self.rules['constant']:
            if not eval(rule['expr'], {}, {'row': row}):
                broken.append((rule['name'], rule.get('suggestion', 'No suggestion provided')))
        return broken

    def check_phase(self, row, phase):
        broken = []
        for rule in self.rules.get(phase, []):
            if not eval(rule['expr'], {}, {'row': row}):
                broken.append((rule['name'], rule.get('suggestion', 'No suggestion provided')))
        return broken

    def check_all(self, row, phase):
        broken = self.check_constant(row)
        broken += self.check_phase(row, phase)
        return broken
