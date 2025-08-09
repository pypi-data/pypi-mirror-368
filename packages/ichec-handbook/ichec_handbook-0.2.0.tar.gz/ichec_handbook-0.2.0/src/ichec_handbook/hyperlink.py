from pathlib import Path

from pydantic import BaseModel


class Hyperlink(BaseModel):

    link: str

    def resolve(self, root: Path) -> str:
        resolved = self.link
        if resolved.startswith("/"):
            resolved = resolved.lstrip("/")
        elif resolved.startswith("."):
            resolved = str(root) + resolved[1:]
        else:
            resolved = str(root) + "/" + resolved
        return resolved

    def is_local(self) -> bool:
        if not self.link.endswith(".md"):
            return False
        return not (self.link.startswith("http") or self.link.startswith("#"))

    def wikify(self) -> str:
        if self.is_local() and not self.link.endswith("index.md"):
            return self.link.split("/")[-1]
        return self.link
