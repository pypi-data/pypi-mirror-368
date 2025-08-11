"""
EntityList class for manipulating NER entity lists with various input formats.

This class consolidates ops for NER dict manipulation into a clean, chainable API
for working with results in different formats.
"""

import re
import string
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Union


class Entity:
    """
    A wrapper class for individual entity dictionaries that provides attribute access.
    
    Allows accessing entity properties as attributes:
    - entity.label (or entity.key depending on format)
    - entity.text (or entity.value depending on format) 
    - entity.start, entity.end, entity.score
    - entity.span (tuple of start and end). Overrides start & end if provided simultaneously.
    """
    
    @staticmethod
    def detect_field_names(entity_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        Auto-detect text and label field names from an entity dictionary.
        
        Args:
            entity_dict: Entity dictionary to analyze
            
        Returns:
            Dictionary with 'text_field' and 'label_field' keys
        """
        if not entity_dict:
            return {'text_field': 'text', 'label_field': 'label'}
        
        # Detect text field
        text_field = 'text'
        if 'text' in entity_dict:
            text_field = 'text'
        elif 'value' in entity_dict:
            text_field = 'value'
        elif 'word' in entity_dict:
            text_field = 'word'
        
        # Detect label field
        label_field = 'label'
        if 'label' in entity_dict:
            label_field = 'label'
        elif 'key' in entity_dict:
            label_field = 'key'
        
        return {'text_field': text_field, 'label_field': label_field}
    
    @staticmethod
    def _normalize_validate_entity(entity_dict: Dict[str, Any], text_field:str=None) -> Dict[str, Any]:
        """
        Validate and normalize entity dictionary.
        
        Args:
            entity_dict: The entity dictionary to validate
            
        Returns:
            Normalized entity dictionary
        """
        if not isinstance(entity_dict, dict):
            raise TypeError("entity_dict must be a dictionary")
        
        span = None
        if "span" in entity_dict:
            span = entity_dict.pop("span")
        
        # Handle span parameter
        if span is not None:
            if not isinstance(span, (tuple, list)) or len(span) != 2:
                raise ValueError("span must be a tuple/list of (start, end)")
            entity_dict['start'], entity_dict['end'] = span
        
        # Validate and normalize start/end
        if 'start' not in entity_dict or 'end' not in entity_dict:
            raise ValueError("Entity missing required 'start' or 'end' field")
        
        # Auto-cast to int
        try:
            entity_dict['start'] = int(entity_dict['start'])
            entity_dict['end'] = int(entity_dict['end'])
        except (ValueError, TypeError):
            raise ValueError("Entity start/end values cannot be converted to integers")
        
        if entity_dict['start'] < 0 or entity_dict['end'] < 0:
            raise ValueError("Entity has negative start/end values")
        if entity_dict['start'] > entity_dict['end']:
            raise ValueError("Entity has start > end")
        
        # Validate text length if text field exists
        if text_field in entity_dict and entity_dict[text_field] is not None:
            expected_length = entity_dict['end'] - entity_dict['start']
            actual_length = len(entity_dict[text_field])
            if actual_length != expected_length:
                raise ValueError(f"Text length ({actual_length}) doesn't match span length ({expected_length}) for field '{entity_dict[text_field]}'")
        
        return entity_dict

    def __init__(self, entity_dict: Dict[str, Any], text_field: Optional[str] = None, label_field: Optional[str] = None):
        """
        Initialize Entity wrapper with auto-detection or explicit field mapping.
        
        Args:
            entity_dict: The underlying entity dictionary
            text_field: Name of the text field ('text', 'value', etc.). If None, auto-detect.
            label_field: Name of the label field ('label', 'key', etc.). If None, auto-detect.
        """
        self._entity = entity_dict
        
        # Auto-detect field names if not provided
        if not text_field or not label_field:
            detected = self.detect_field_names(entity_dict)
            self._text_field = text_field or detected['text_field']
            self._label_field = label_field or detected['label_field']
        else:
            self._text_field = text_field
            self._label_field = label_field
        
        # Validate and normalize the entity after field detection
        self._entity = self._normalize_validate_entity(self._entity, self._text_field)
    
    @property
    def label(self) -> str:
        """Get the entity label."""
        return self._entity.get(self._label_field)
    
    @label.setter
    def label(self, value: str) -> None:
        """Set the entity label."""
        if value is None:
            raise ValueError("Label cannot be None")
        self._entity[self._label_field] = value

    @property
    def text(self) -> Optional[str]:
        """Get the entity text."""
        return self._entity.get(self._text_field)
    
    @text.setter
    def text(self, value: str) -> None:
        """Set the entity text."""
        if value is None:
            raise ValueError("Text cannot be None")
        self._entity[self._text_field] = value

    @property
    def start(self) -> int:
        """Get the start position."""
        return self._entity.get('start')
    
    @start.setter
    def start(self, value: int) -> None:
        """Set the start position."""
        if value is None or value < 0:
            raise ValueError("Start position must be a non-negative integer")
        self._entity['start'] = value   
    
    @property
    def end(self) -> int:
        """Get the end position."""
        return self._entity.get('end')
    
    @end.setter
    def end(self, value: int) -> None:
        """Set the end position."""
        if value is None or value < 0:
            raise ValueError("End position must be a non-negative integer")
        self._entity['end'] = value
    
    @property
    def score(self) -> Optional[float]:
        """Get the confidence score."""
        return self._entity.get('score')
    
    @score.setter
    def score(self, value: float) -> None:
        """Set the confidence score."""
        self._entity['score'] = value 
    
    @property
    def span(self) -> Tuple[int, int]:
        """Get the entity span as a tuple (start, end)."""
        return (self.start, self.end)
    
    def __repr__(self) -> str:
        """String representation of the entity."""
        return f"Entity({self._entity})"
    
    def __str__(self):
        """String representation of the entity with label and text."""
        return f"{self.label}: {self.text} ({self.start}-{self.end}) {self.score}"
    
    def __getitem__(self, key):
        """Get item using object[key] syntax."""
        return self._entity[key]

    def __setitem__(self, key, value):
        """Set item using object[key] = value syntax."""
        self._entity[key] = value

    def __delitem__(self, key):
        """Delete item using del object[key] syntax."""
        del self._entity[key]

    def __contains__(self, key):
        """Check if key exists using 'key in object' syntax."""
        return key in self._entity

    def keys(self):
        """Return dictionary keys."""
        return self._entity.keys()

    def values(self):
        """Return dictionary values."""
        return self._entity.values()

    def items(self):
        """Return dictionary items."""
        return self._entity.items()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity back to a dictionary."""
        return deepcopy(self._entity)
    
    def copy(self) -> 'Entity':
        """Create a deep copy of this Entity."""
        return Entity(deepcopy(self._entity), text_field=self._text_field, label_field=self._label_field)
    

class EntityList:
    """
    A class for manipulating lists of entity dictionaries between various input formats.
    
    Supports two main formats:
    - Default format: {'start': 0, 'end': 4, 'text': 'hello', 'label': 'greeting', 'score': 0.999}
    - Table format: {'start': 0, 'end': 4, 'value': 'hello', 'key': 'greeting', 'score': 0.999}
    
    The text & label key names might be different but are consistent within the same list.
    """


    def __init__(self, entities: Union[List[Dict[str, Any]], List['Entity']], source_text: Optional[str] = None):
        """
        Initialize EntityList with auto-detection.
        During initialization, it will validate the entities and source text.
        Sorts them by start position
        
        Args:
            entities: List of entity dictionaries or Entity objects
            source_text: Optional source text that entities refer to
        """
        # Store raw entities temporarily for field detection
        entity_objects = []
        if entities:
            for entity in entities:
                if isinstance(entity, dict):
                    entity_objects.append(Entity(entity))
                elif isinstance(entity, Entity):
                    entity_objects.append(entity.copy())

        sorted_entities = sorted(entity_objects, key=lambda e: e.start, reverse=False)

        self._entities = sorted_entities
        self._source_text = source_text
        if source_text:
            self._source_text = self._validate(self._source_text)
        
        # set defaults
        self._text_field = 'text'
        self._label_field = 'label'

    def _validate(self, source_text: str = None) -> bool:
        """
        Validate if the entity texts match the source text at their span positions.
        
        Args:
            source_text: The source text to validate against
            
        Returns:
            True if valid, False otherwise
        """
        if source_text is None:
            source_text = self._source_text
            if source_text is None:
                raise ValueError("source_text must be provided or set on the EntityList")
        else:  # so we don't validate the source text every time
            for entity in self._entities:
                if entity.text != source_text[entity.start:entity.end]:
                    raise ValueError(
                        f"Entity text '{entity.text}' does not match source text at span ({entity.start}, {entity.end})"
                    )
        return source_text
    
    @property
    def entities(self) -> List[Dict[str, Any]]:
        """Get the list of entities."""
        return self._entities
    
    def __len__(self) -> int:
        """Return the number of entities."""
        return len(self._entities)
    
    def __iter__(self):
        """Iterate over Entity instances."""
        yield from self._entities

    def __getitem__(self, index):
        """Get Entity instance by index or slice."""
        if isinstance(index, slice):
            # Return a new EntityList when slicing
            sliced_entities = self._entities[index]
            return EntityList(sliced_entities, source_text=self._source_text)
        else:
            # Return an Entity instance for single index
            return self._entities[index].copy()
    
    def copy(self) -> 'EntityList':
        """Create a deep copy of this EntityList."""
        return EntityList(
            self._entities, 
            source_text=self._source_text
        )
    
    # Format Operations
    def to_format(self, text_field: str, label_field: str, return_span: bool = False, score_precision: Optional[int] = None, return_index:bool = True, return_score:bool = True) -> 'EntityList':
        """Convert entities to any format."""

        converted = []
        for e in self._entities:
            entity_dict = {
                    text_field: e.text,
                    label_field: e.label,
                }
            if return_score and e.score is not None:
                entity_dict['score'] = round(e.score, score_precision) if score_precision is not None else e.score
            if return_span:
                entity_dict['span'] = (e.start, e.end)
            if return_index:
                entity_dict['start'] = e.start
                entity_dict['end'] = e.end
            converted.append(entity_dict)
        return converted

    def to_format_default(self, **kwargs) -> 'EntityList':
        default_kwargs = {
            'text_field': 'text',
            'label_field': 'label',
            'return_span': False
        }
        default_kwargs.update(kwargs)

        return self.to_format(**default_kwargs)
    def to_format_table(self, **kwargs) -> 'EntityList':
        default_kwargs = {
            'text_field': 'value',
            'label_field': 'key',
            'return_span': False,
            "score_precision": 4,
        }
        default_kwargs.update(kwargs)
        return self.to_format(**default_kwargs)
    def to_format_span(self, **kwargs) -> 'EntityList':
        default_kwargs = {
            'text_field': 'value',
            'label_field': 'key',
            'return_span': True,
            "score_precision": 4,
        }
        default_kwargs.update(kwargs)
        return self.to_format(**default_kwargs)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Return entities as a list of dictionaries."""
        return [entity.to_dict() for entity in self._entities]

    @staticmethod
    def allowed_merges(between_text: str, label: str) -> bool:
        """
        Check if the text between two entities allows merging based on label.

        Args:
            between_text: The text between two entities
            label: The label of the current entity  # legacy
        Returns:
            bool: True if merging is allowed, False otherwise
        """
        if between_text == " ":
            return True
        if between_text in string.punctuation:
            return True
        return False

    # Entity Manipulation
    def merge_consecutive(self, source_text: Optional[str] = None) -> 'EntityList':
        """
        Merge consecutive entities with the same label. If source_text exists,
        it will check if the text between entities allows merging based on allowed_merges logic,
        otherwise it will merge only consecutive ones.
        
        Args:
            source_text: The source text that entities refer to
            
        Returns:
            New EntityList with merged consecutive entities
        """
        if source_text or self._source_text:
            source_text = self._validate(source_text)
        entity_list = self.sort(reverse=False)

        merged_entities = [entity_list._entities[0]]
        
        for i in range(1, len(entity_list._entities)):
            prev_entity = merged_entities[-1]
            current_entity = entity_list._entities[i]
            current_label = current_entity.label
            merge = False
            between_text = ""
            
            if (prev_entity.label == current_entity.label and prev_entity.end - current_entity.start <= 1):
                if prev_entity.end == current_entity.start:
                    merge = True
                elif source_text and (prev_entity.end + 1 == current_entity.start):
                    between_text = source_text[prev_entity.end:current_entity.start]
                    if self.allowed_merges(between_text, current_label):
                        prev_entity.end = current_entity.end
                        merge = True
                        
            if not merge:
                merged_entities.append(current_entity.copy())
            else:
                prev_entity.end = current_entity.end
                if current_entity.text:
                    prev_entity.text = prev_entity.text + between_text + current_entity.text
        
        return merged_entities
    
    def split_long_entities(self, max_length: int, source_text: Optional[str] = None) -> 'EntityList':
        """
        Split entities that are longer than max_length.
        
        Args:
            max_length: Maximum allowed entity length
            source_text: Optional source text to extract updated text fields from
            
        Returns:
            New EntityList with long entities split
        """
        if not self._entities:
            return self.copy()
        
        source_text = self._validate(source_text)
        
        split_entities = []
        
        for entity in self._entities:
            entity_length = entity.end - entity.start
            
            if entity_length <= max_length:
                split_entities.append(entity.copy())
            else:
                start = entity.start
                end = entity.end
                
                while end - start > max_length:
                    new_entity = entity.copy()
                    new_entity.start = start
                    new_entity.end = start + max_length
                    
                    # Update text field if source_text is provided
                    if source_text is not None and self._text_field in entity:
                        new_entity.text = source_text[start:start + max_length]
                    
                    split_entities.append(new_entity)
                    start += max_length
                
                # Add the remaining part
                if start < end:
                    new_entity = entity.copy()
                    new_entity.start = start
                    new_entity.end = end
                    
                    # Update text field if source_text is provided
                    if source_text is not None and entity.text is not None:
                        new_entity.text = source_text[start:end]
                    
                    split_entities.append(new_entity)
        
        return EntityList(split_entities, source_text=source_text)
    
    def filter_by_score(self, min_score: float, max_score: float = 1.0) -> 'EntityList':
        """
        Filter entities by score range.
        
        Args:
            min_score: Minimum score threshold
            max_score: Maximum score threshold
            
        Returns:
            New EntityList with filtered entities
        """
        filtered = [
            e for e in self._entities 
            if e.score and min_score <= e.score <= max_score
        ]
        
        return EntityList(filtered, source_text=self._source_text)
    
    def filter_by_label(self, labels: Union[str, List[str]], exclude: bool = False) -> 'EntityList':
        """
        Filter entities by label(s).
        
        Args:
            labels: Label or list of labels to filter by
            exclude: If True, exclude these labels instead of including them
            
        Returns:
            New EntityList with filtered entities
        """
        if isinstance(labels, str):
            labels = [labels]
        
        if exclude:
            filtered = [e for e in self._entities if e.label not in labels]
        else:
            filtered = [e for e in self._entities if e.label in labels]
        
        return EntityList(filtered, source_text=self._source_text)
    
    def sort(self, reverse: bool = False) -> 'EntityList':
        """
        Sort entities by their start position.
        
        Args:
            reverse: If True, sort in descending order
            
        Returns:
            New EntityList with sorted entities
        """
        sorted_entities = sorted(self._entities, key=lambda e: e.start, reverse=reverse)
        return EntityList(sorted_entities, source_text=self._source_text)
    
    # Label Operations
    
    def map_labels(self, label_map: Dict[str, str], strict: bool = True, default_label: Optional[str] = None) -> 'EntityList':
        """
        Map entity labels using a dictionary mapping.
        
        Args:
            label_map: Dictionary mapping old labels to new labels
            strict: If True, raise error for unmapped labels. If False, use default behavior.
            default_label: Default label for unmapped entities when strict=False. If None, keep original label.
            
        Returns:
            New EntityList with mapped labels
        """
        mapped_entities = []
        
        for entity in self._entities:
            new_entity = entity.copy()
            old_label = entity.label
            if old_label in label_map:
                new_entity.label = label_map[old_label]
            elif default_label is not None and not strict:
                new_entity.label = default_label
            else:
                raise ValueError(f"Label '{old_label}' not found in label_map and no default_label provided")

            mapped_entities.append(new_entity)
        
        return EntityList(mapped_entities, source_text=self._source_text)
    
    def add_text_from_source(self, source_text: str) -> 'EntityList':
        """
        Add text field to entities based on their start/end positions.
        
        Args:
            source_text: The source text to extract entity text from
            
        Returns:
            New EntityList with text field added
        """
        entities_with_text = []
        
        for entity in self._entities:
            new_entity = entity.copy()
            extracted_text = source_text[entity.start:entity.end]
            new_entity.text = extracted_text
            entities_with_text.append(new_entity)
        
        return EntityList(entities_with_text, source_text=source_text)
    
    def add_unk_entities(self, source_text: Optional[str] = None) -> 'EntityList':
        """
        Add 'UNK' entities for spans in the source text that are not covered by existing entities.
        Always ignores whitespace.
        
        Args:
            source_text: The source text to check for uncovered spans
            
        Returns:
            New EntityList with 'UNK' entities added
        """
        
        source_text = self._validate(source_text)
        
        placeholder = list(source_text)
        for r in self._entities:
            placeholder[r.start:r.end]= " " * (r.end-r.start)

        placeholder = "".join(placeholder)
        unk_entities = []
        for match in re.finditer(r'\S+', placeholder):
            start = match.start()
            end = match.end()
            unk_entities.append(Entity({
                "start": start,
                "end": end,
                "text": placeholder[start:end],
                "label": "UNK",
                "score": None
            }))
        new_entities = self._entities + unk_entities
        return EntityList(new_entities, source_text=source_text)
    
    # Comparison & Analysis
    def compare_with(self, other: 'EntityList', source_text: str, merge: bool = True) -> Dict[str, Any]:
        """
        Compare this EntityList with another for evaluation purposes.
        
        Args:
            other: Another EntityList to compare against
            source_text: Source text for merging operations
            merge: Whether to merge consecutive entities before comparison
            
        Returns:
            Dictionary with comparison results
        """
        def has_overlap(slice1: Tuple[int, int], slice2: Tuple[int, int]) -> bool:
            return slice1[0] < slice2[1] and slice1[1] > slice2[0]
        
        if merge:
            baseline = self.merge_consecutive(source_text)
            new_predictions = other.merge_consecutive(source_text)
        
        score = 0
        positive_score = 0
        diff = []
        old_diff = [0] * len(new_predictions)
        
        for attr in baseline:
            attr_slice = (attr.start, attr.end)
            attr_label = attr.label
            
            match_found = False
            for idx, pred in enumerate(new_predictions):
                pred_slice = (pred.start, pred.end)
                pred_label = pred.label
                
                if attr_slice == pred_slice:
                    match_found = True
                    if attr_label == pred_label:
                        break
                    elif attr_label == 'UNK':
                        old_diff[idx] = 1
                        positive_score += 1
                        break
                    else:
                        old_diff[idx] = -1
                        score -= 1
                        break
                elif has_overlap(attr_slice, pred_slice):
                    match_found = True
                    old_diff[idx] = -1
                    if attr_label == "UNK":
                        old_diff[idx] = 1
                        positive_score += 1
                        break
                    elif attr_label == pred_label:
                        score -= 1
                        break
                    else:
                        score -= 2
                        break
            
            if not match_found and attr_label != 'UNK':
                score -= 2
                diff.append(1)
            else:
                diff.append(0)
        
        return {
            "negative_score": score,
            "positive_score": positive_score,
            "diff_baseline": diff,
            "diff_new_preds": old_diff,
            "baseline_entities": baseline,
            "comparison_entities": new_predictions
        }
    
    def has_overlap(self, entity: Union[Dict,'Entity']) -> Dict[str, Any]:
        """
        Check for overlapping entities between this EntityList and another.
        
        Args:
            other: Another EntityList to check against
            
        Returns:
            Dictionary with overlap information
        """
        overlaps = []
        if isinstance(entity, dict):
            entity = Entity(entity)
        
        for existing_entity in self._entities:
            if existing_entity.start < entity.end and existing_entity.end > entity.start:
                return existing_entity.to_dict()
            
    def add_entities(self, entities: Union[List[Dict[str, Any]], List['Entity']]) -> 'EntityList':
        existing_entities = deepcopy(self._entities)
        for entity in entities:
            if isinstance(entity, dict):
                entity = Entity(entity)

            if not self.has_overlap(entity):
                # validate the text field
                if entity.text is not None and self._source_text:
                    if self._source_text[entity.start:entity.end] == entity.text:
                        existing_entities.append(entity)
        return EntityList(existing_entities, source_text=self._source_text)
    
    # Export Methods
    def to_displacy_format(self, source_text: str, diff: Optional[List[int]] = None, skip_unk: bool = True) -> List[Dict[str, Any]]:
        """
        Convert to displaCy format for visualization.
        
        Args:
            source_text: Source text
            diff: Difference markers for coloring (-1, 0, 1)
            skip_unk: Whether to skip UNK labels
            
        Returns:
            List formatted for displaCy visualization
        """
        color_map = {0: "#ddd", 1: "#00FF00", -1: "#FFC0CB"}
        
        if diff is None:
            diff = [0] * len(self._entities)
        
        formatted = []
        for entity, is_match in zip(self._entities, diff):
            formatted_entity = {
                "start": entity.start,
                "end": entity.end,
                "label": entity.label,
                "score": entity.score,
                "bg": color_map[is_match]
            }
            
            if skip_unk and formatted_entity["label"] == "UNK":
                continue
                
            formatted.append(formatted_entity)
        
        return [{"text": source_text, "ents": formatted, "title": None}]
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Return entities as a list of dictionaries."""
        return [entity.to_dict() for entity in self._entities]
    
    def to_label_map(self, separator: Optional[str]= "|", sort:bool = True, remove_dupes: bool=True) -> Dict[str, str]:
        """
        Convert entities to a dictionary mapping labels to comma-delimited text values.
        
        Returns:
            Dictionary where keys are labels and values are comma-delimited strings of entity texts
            
        Example:
            For entities with labels 'greeting' and texts ['hello', 'hi'], returns:
            {'greeting': 'hello, hi'}
        """
        label_map = {}
        
        for entity in self._entities:
            label = entity.label
            text = entity.text  # Handle cases where text field might be missing
            
            if label in label_map:
                label_map[label].append(text)
            else:
                label_map[label] = [text]

        for label, texts in label_map.items():
            if remove_dupes:
                texts = list(set(texts))  # Remove duplicates
            if sort:
                texts = sorted(texts)  # Sort the texts
            label_map[label] = separator.join(texts)  # Join texts with the separator
            
        return label_map
    
    def to_polars_df(self):
        """
        Convert to Polars DataFrame if polars is available.
        
        Returns:
            Polars DataFrame with entities
        """
        try:
            import polars as pl
            return pl.DataFrame(self._entities)
        except ImportError:
            raise ImportError("Polars is not installed. Install with: pip install polars")
    
    # Utility Methods
    
    def get_labels(self) -> List[str]:
        """Get unique labels in the entity list."""
        return list(set(entity.label for entity in self._entities))
    
    def get_label_counts(self) -> Dict[str, int]:
        """Get count of each label."""
        counts = {}
        for entity in self._entities:
            label = entity.label
            counts[label] = counts.get(label, 0) + 1
        return counts
    
    def get_spans(self) -> List[Tuple[int, int]]:
        """Get list of (start, end) spans."""
        return [(entity.start, entity.end) for entity in self._entities]
    
    def __repr__(self) -> str:
        """String representation of EntityList. same as __str__."""
        return self.__str__()
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [f"{len(self)} entities:"]
        if self._source_text:
            lines.append(f"{self._source_text}")
        
        if self._entities:
            lines.append("Entities:")
            for i, entity in enumerate(self._entities):
                lines.append(f"  {i}: {entity}")
        
        return "\n".join(lines)
