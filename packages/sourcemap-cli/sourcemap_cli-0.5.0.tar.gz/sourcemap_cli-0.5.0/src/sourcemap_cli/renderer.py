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
                
                # Extract the actual signature from the source code
                signature = self._extract_signature(tag)
                
                output_data["files"][fname]["symbols"].append({
                    "name": tag.name,
                    "kind": tag.kind,
                    "line": tag.line,
                    "signature": signature
                })
        
        return output_data
    
    def _extract_signature(self, tag: Tag) -> str:
        """Extract the full signature for a symbol from the source code."""
        if tag.line <= 0:  # Invalid line number
            return tag.name
        
        try:
            # Read the source code
            code = self.parser.read_text(tag.fname) or ""
            if not code:
                return tag.name
            
            lines = code.splitlines()
            if tag.line > len(lines):
                return tag.name
            
            # Tree-sitter line numbers are 0-based, so tag.line is already 0-based
            target_line_idx = tag.line
            if target_line_idx >= len(lines):
                return tag.name
            
            # Search around the target line for the actual definition
            search_start = max(0, target_line_idx - 2)
            search_end = min(len(lines), target_line_idx + 3)
            
            for line_idx in range(search_start, search_end):
                line = lines[line_idx].strip()
                
                # Look for function/class definitions that contain our symbol name
                if tag.kind == "def" and tag.name in line:
                    if ("def " in line or "class " in line or "function " in line or 
                        line.startswith("@") or "=" in line):
                        
                        signature = line
                        
                        # Look for continuation lines (parameters on multiple lines)
                        current_idx = line_idx
                        while current_idx + 1 < len(lines):
                            next_line = lines[current_idx + 1].strip()
                            # If the line has unclosed parentheses or looks like a continuation
                            if (signature.count('(') > signature.count(')') or
                                next_line.startswith(')') or
                                (signature.endswith(',') or signature.endswith('(')) and
                                not next_line.endswith(':')):
                                signature += " " + next_line
                                current_idx += 1
                                if next_line.endswith(':'):
                                    break
                            else:
                                break
                        
                        return signature
            
            # Fallback: just return the line where the tag was found
            return lines[target_line_idx].strip() or tag.name
                
        except Exception as e:
            # If anything goes wrong, just return the symbol name
            return tag.name