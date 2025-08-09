import logging
from pathlib import Path

from .document.hyperlink import Hyperlink

logger = logging.getLogger(__name__)


class LinkValidator:
    def __init__(self) -> None:
        pass

    def find_link(self, root: Path, link: Hyperlink, pages: list):
        resolved_link = link.resolve(root)
        for page in pages:
            if resolved_link == str(page.file_path):
                return resolved_link
        return None

    def check_for_orphaned_pages(self, links):
        orphaned_pages = []
        for file_path, count in links.items():
            if "pages" in str(file_path) and count == 0:
                orphaned_pages.append(file_path)

        if orphaned_pages:
            msg = "The following pages are not linked from anywhere:\n"
            for page in orphaned_pages:
                msg += page + "\n"
            raise RuntimeError(msg)

    def on_failed_links(self, links):
        msg = "Failed link validation. The following links don't resolve:\n"
        for href, filepath in links:
            msg += f"File: {filepath} | Link: {href}\n"
        raise RuntimeError(msg)

    def validate_links(self, pages):
        logger.info("Starting link validation")

        link_counts = {str(page.file_path): 0 for page in pages}

        failed_links = []

        for page in pages:
            page_dir = page.file_path.parent
            for link in page.links:
                href = Hyperlink(link["href"])
                if not href.is_local():
                    continue
                link_target = self.find_link(page_dir, href, pages)
                if not link_target:
                    failed_links.append((href.link, page.file_path))
                    continue
                link_counts[link_target] = link_counts[link_target] + 1

        if failed_links:
            self.on_failed_links(failed_links)

        self.check_for_orphaned_pages(link_counts)

        logger.info("Finished link validation")
