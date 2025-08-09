import subprocess


class SpellChecker:

    def __init__(self):
        self.dictionary = "en_GB"

    def check(self, doc: str) -> list[str]:
        cmd = f"hunspell -d {self.dictionary} -H << {doc}"
        ret = subprocess.run(
            cmd, check=True, shell=True, capture_output=True, text=True
        )
        return ret.stdout.splitlines()
