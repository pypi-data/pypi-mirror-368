# ABOUTME: PageRank-based ranking algorithm - identifying important code symbols
"""PageRank-based ranking algorithm for identifying important code symbols."""

import math
from collections import defaultdict, Counter
from pathlib import Path
from typing import Set, Dict, List, Tuple, Optional, Callable

import networkx as nx

from .parser import Tag


class SymbolRanker:
    """Ranks code symbols by importance using PageRank algorithm."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def get_ranked_tags(
        self,
        chat_fnames: List[str],
        other_fnames: List[str],
        mentioned_fnames: Set[str],
        mentioned_idents: Set[str],
        tags_by_file: Dict[str, List[Tag]],
        get_rel_fname: Callable[[str], str],
        progress: Optional[Callable[[str], None]] = None
    ) -> List[Tag]:
        """
        Rank tags using PageRank algorithm based on symbol references and definitions.
        
        Args:
            chat_fnames: Files currently in the chat context
            other_fnames: Other files to consider
            mentioned_fnames: Files mentioned in the conversation
            mentioned_idents: Identifiers mentioned in the conversation
            tags_by_file: Dictionary mapping file paths to their tags
            get_rel_fname: Function to convert absolute paths to relative paths
            progress: Optional progress callback
            
        Returns:
            List of tags ranked by importance
        """
        defines = defaultdict(set)
        references = defaultdict(list)
        definitions = defaultdict(set)
        
        personalization = dict()
        
        fnames = set(chat_fnames).union(set(other_fnames))
        chat_rel_fnames = set()
        
        fnames = sorted(fnames)
        
        # Default personalization for unspecified files is 1/num_nodes
        personalize = 100 / len(fnames) if fnames else 1
        
        for fname in fnames:
            if progress:
                progress(f"Processing {fname}")
            
            rel_fname = get_rel_fname(fname)
            current_pers = 0.0
            
            if fname in chat_fnames:
                current_pers += personalize
                chat_rel_fnames.add(rel_fname)
            
            if rel_fname in mentioned_fnames:
                current_pers = max(current_pers, personalize)
            
            # Check path components against mentioned_idents
            path_obj = Path(rel_fname)
            path_components = set(path_obj.parts)
            basename_with_ext = path_obj.name
            basename_without_ext, _ = path_obj.name.rsplit('.', 1) if '.' in path_obj.name else (path_obj.name, '')
            components_to_check = path_components.union(
                {basename_with_ext, basename_without_ext})
            
            matched_idents = components_to_check.intersection(mentioned_idents)
            if matched_idents:
                current_pers += personalize
            
            if current_pers > 0:
                personalization[rel_fname] = current_pers
            
            tags = tags_by_file.get(fname, [])
            if not tags:
                continue
            
            for tag in tags:
                if tag.kind == "def":
                    defines[tag.name].add(rel_fname)
                    key = (rel_fname, tag.name)
                    definitions[key].add(tag)
                elif tag.kind == "ref":
                    references[tag.name].append(rel_fname)
        
        if not references:
            references = dict((k, list(v)) for k, v in defines.items())
        
        idents = set(defines.keys()).intersection(set(references.keys()))
        
        G = nx.MultiDiGraph()
        
        # Add self-edges for definitions with no references
        for ident in defines.keys():
            if ident in references:
                continue
            for definer in defines[ident]:
                G.add_edge(definer, definer, weight=0.1, ident=ident)
        
        # Build the graph
        for ident in idents:
            if progress:
                progress(f"Processing {ident}")
            
            definers = defines[ident]
            
            mul = 1.0
            
            # Boost importance for certain naming patterns
            is_snake = ("_" in ident) and any(c.isalpha() for c in ident)
            is_kebab = ("-" in ident) and any(c.isalpha() for c in ident)
            is_camel = any(c.isupper() for c in ident) and any(c.islower() for c in ident)
            
            if ident in mentioned_idents:
                mul *= 10
            if (is_snake or is_kebab or is_camel) and len(ident) >= 8:
                mul *= 10
            if ident.startswith("_"):
                mul *= 0.1
            if len(defines[ident]) > 5:
                mul *= 0.1
            
            for referencer, num_refs in Counter(references[ident]).items():
                for definer in definers:
                    use_mul = mul
                    if referencer in chat_rel_fnames:
                        use_mul *= 50
                    
                    # Scale down high frequency mentions
                    num_refs = math.sqrt(num_refs)
                    
                    G.add_edge(referencer, definer,
                               weight=use_mul * num_refs, ident=ident)
        
        # Run PageRank
        if personalization:
            pers_args = dict(personalization=personalization,
                             dangling=personalization)
        else:
            pers_args = dict()
        
        try:
            ranked = nx.pagerank(G, weight="weight", **pers_args)
        except ZeroDivisionError:
            try:
                ranked = nx.pagerank(G, weight="weight")
            except ZeroDivisionError:
                return []
        
        # Distribute rank from each source node across its out edges
        ranked_definitions = defaultdict(float)
        for src in G.nodes:
            if progress:
                progress(f"Ranking {src}")
            
            src_rank = ranked[src]
            total_weight = sum(data["weight"] for _src, _dst, data in G.out_edges(src, data=True))
            
            for _src, dst, data in G.out_edges(src, data=True):
                data["rank"] = src_rank * data["weight"] / total_weight
                ident = data["ident"]
                ranked_definitions[(dst, ident)] += data["rank"]
        
        # Build final ranked tags list
        ranked_tags = []
        ranked_definitions = sorted(
            ranked_definitions.items(), reverse=True, key=lambda x: (x[1], x[0])
        )
        
        for (fname, ident), rank in ranked_definitions:
            if fname in chat_rel_fnames:
                continue
            ranked_tags += list(definitions.get((fname, ident), []))
        
        # Add files without tags
        rel_other_fnames_without_tags = set(
            get_rel_fname(fname) for fname in other_fnames)
        
        fnames_already_included = set(rt[0] for rt in ranked_tags)
        
        top_rank = sorted([(rank, node) for (node, rank) in ranked.items()], reverse=True)
        for rank, fname in top_rank:
            if fname in rel_other_fnames_without_tags:
                rel_other_fnames_without_tags.remove(fname)
            if fname not in fnames_already_included:
                ranked_tags.append((fname,))
        
        for fname in rel_other_fnames_without_tags:
            ranked_tags.append((fname,))
        
        return ranked_tags