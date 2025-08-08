# ABOUTME: Output rendering - formatting repository maps for text and JSON output
"""Output rendering and formatting for repository maps."""

from typing import List, Set, Optional, Dict, Any, Union

from .parser import Tag, CodeParser


class MapRenderer:
    """Renders repository maps in various formats."""
    
    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.tree_cache = dict()
        self.tree_context_cache = dict()
    
    def get_mtime(self, fname: str) -> Optional[float]:
        """Get modification time of a file."""
        import os
        try:
            return os.path.getmtime(fname)
        except FileNotFoundError:
            return None
    
    def render_tree(self, abs_fname: str, rel_fname: str, lois: List[int]) -> str:
        """Render a file's tree structure with highlighted lines of interest."""
        mtime = self.get_mtime(abs_fname)
        if mtime is None:
            return ""
        
        return self.parser.render_tree(abs_fname, rel_fname, lois, mtime, self.tree_cache)
    
    def to_tree(self, tags: List[Union[Tag, tuple]], chat_rel_fnames: Set[str]) -> str:
        """Convert tags to tree format string."""
        if not tags:
            return ""
        
        cur_fname = None
        cur_abs_fname = None
        lois = None
        output = ""
        
        # Add a bogus tag at the end so we trip the this_fname != cur_fname
        dummy_tag = (None,)
        for tag in sorted(tags) + [dummy_tag]:
            this_rel_fname = tag[0] if tag != dummy_tag else None
            if this_rel_fname and this_rel_fname in chat_rel_fnames:
                continue
            
            # Output the final real entry in the list
            if this_rel_fname != cur_fname:
                if lois is not None:
                    output += "\n"
                    output += cur_fname + ":\n"
                    output += self.render_tree(cur_abs_fname, cur_fname, lois)
                    lois = None
                elif cur_fname:
                    output += "\n" + cur_fname + "\n"
                if isinstance(tag, Tag):
                    lois = []
                    cur_abs_fname = tag.fname
                cur_fname = this_rel_fname
            
            if lois is not None and isinstance(tag, Tag):
                lois.append(tag.line)
        
        # Truncate long lines, in case we get minified js or something else crazy
        output = "\n".join([line[:100] for line in output.splitlines()]) + "\n"
        
        return output
    
    def render_json(
        self,
        ranked_tags: List[Tag],
        other_fnames: List[str],
        tokens: int,
        root: str
    ) -> Dict[str, Any]:
        """Render the map as JSON data."""
        output_data = {
            "files": {},
            "summary": {
                "total_files": len(other_fnames),
                "tokens": tokens,
                "root": root
            }
        }
        
        for tag in ranked_tags:
            if isinstance(tag, tuple) and len(tag) == 1:
                # File-only entry
                fname = tag[0]
                if fname and fname not in output_data["files"]:
                    output_data["files"][fname] = {"symbols": []}
            elif hasattr(tag, 'rel_fname'):
                # Tag with symbol info
                fname = tag.rel_fname
                if fname not in output_data["files"]:
                    output_data["files"][fname] = {"symbols": []}
                
                output_data["files"][fname]["symbols"].append({
                    "name": tag.name,
                    "kind": tag.kind,
                    "line": tag.line
                })
        
        return output_data