"""Advanced intent classification system for gateway routing optimization.

This module implements enhanced intent classification with:
- Context-aware disambiguation
- Advanced pattern matching with semantic understanding
- Performance optimization for <50ms classification
- Confidence scoring with multiple algorithms
- Fallback handling and error recovery
"""

import asyncio
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, cast

logger = logging.getLogger(__name__)


class ClassificationAlgorithm(Enum):
    """Available classification algorithms."""

    PATTERN_MATCHING = "pattern_matching"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CONTEXT_AWARE = "context_aware"
    HYBRID = "hybrid"


@dataclass
class ClassificationContext:
    """Context information for intent classification."""

    gateway_type: str
    previous_intents: List[str]
    user_preferences: Dict[str, Any]
    session_context: Dict[str, Any]
    project_context: Optional[str] = None
    task_context: Optional[str] = None


@dataclass
class IntentCandidate:
    """A candidate intent with confidence and metadata."""

    intent: str
    confidence: float
    algorithm: ClassificationAlgorithm
    matched_patterns: List[str]
    context_boost: float
    tool_name: str
    gateway_type: str


class AdvancedIntentClassifier:
    """Advanced intent classification with context awareness and optimization."""

    def __init__(self) -> None:
        """Initialize the advanced intent classifier."""
        self.pattern_cache: Dict[str, Any] = {}
        self.context_weights = self._load_context_weights()
        self.semantic_keywords = self._load_semantic_keywords()
        self.disambiguation_rules = self._load_disambiguation_rules()
        self.performance_stats: Dict[str, List[float]] = defaultdict(list)

    def _load_context_weights(self) -> Dict[str, float]:
        """Load context weighting factors for different scenarios."""
        return {
            "project_context_match": 0.2,
            "task_context_match": 0.15,
            "previous_intent_similarity": 0.1,
            "user_preference_match": 0.1,
            "session_consistency": 0.05,
            "temporal_proximity": 0.05,
        }

    def _load_semantic_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Load semantic keyword mappings for enhanced pattern matching."""
        return {
            "lackey_get": {
                "retrieval_verbs": [
                    "get",
                    "show",
                    "display",
                    "fetch",
                    "retrieve",
                    "find",
                    "search",
                    "list",
                ],
                "query_objects": [
                    "project",
                    "task",
                    "note",
                    "dependency",
                    "status",
                    "progress",
                ],
                "filter_terms": [
                    "all",
                    "active",
                    "done",
                    "blocked",
                    "ready",
                    "assigned",
                ],
                "scope_terms": ["in", "for", "from", "within", "under", "belonging"],
            },
            "lackey_do": {
                "action_verbs": [
                    "create",
                    "make",
                    "add",
                    "update",
                    "change",
                    "modify",
                    "assign",
                    "complete",
                ],
                "target_objects": [
                    "project",
                    "task",
                    "note",
                    "dependency",
                    "status",
                    "assignment",
                ],
                "modification_terms": ["to", "as", "with", "using", "by", "from"],
                "bulk_terms": ["all", "multiple", "batch", "bulk", "mass", "several"],
            },
            "lackey_analyze": {
                "analysis_verbs": [
                    "analyze",
                    "check",
                    "validate",
                    "assess",
                    "evaluate",
                    "examine",
                ],
                "analysis_objects": [
                    "dependencies",
                    "health",
                    "performance",
                    "bottlenecks",
                    "risks",
                ],
                "scope_terms": ["project", "task", "workflow", "system", "overall"],
                "insight_terms": [
                    "insights",
                    "recommendations",
                    "suggestions",
                    "metrics",
                    "stats",
                ],
            },
        }

    def _load_disambiguation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load rules for disambiguating between similar intents."""
        return {
            "get_vs_list": {
                "get_indicators": [
                    "specific",
                    "details",
                    "info",
                    "about",
                    "particular",
                ],
                "list_indicators": ["all", "multiple", "every", "show all", "list all"],
                "confidence_boost": 0.3,
            },
            "create_vs_update": {
                "create_indicators": ["new", "add", "make", "build", "initialize"],
                "update_indicators": ["change", "modify", "edit", "alter", "revise"],
                "confidence_boost": 0.25,
            },
            "status_update_disambiguation": {
                "status_keywords": [
                    "todo",
                    "in_progress",
                    "in-progress",
                    "blocked",
                    "done",
                    "status",
                ],
                "status_phrases": [
                    "status to",
                    "mark as",
                    "set status",
                    "change status",
                    "update status",
                ],
                "target_intent": "update_task_status",
                "confidence_boost": 0.4,  # Strong boost for status operations
            },
            "assign_vs_reassign": {
                "assign_indicators": ["assign", "give", "allocate", "delegate"],
                "reassign_indicators": [
                    "reassign",
                    "move",
                    "transfer",
                    "change assignee",
                ],
                "confidence_boost": 0.2,
            },
            "list_vs_search": {
                "list_indicators": ["list all", "show all", "get all", "simple list"],
                "search_indicators": [
                    "mention",
                    "mentioning",
                    "contain",
                    "containing",
                    "with",
                    "that",
                    "where",
                    "having",
                    "about",
                    "find",
                    "search",
                    "filter",
                    "filtered",
                    "assigned to",
                    "tagged",
                    "complexity",
                    "status",
                    "criteria",
                ],
                "confidence_boost": 0.4,
            },
            "create_task_vs_add_dependencies": {
                "create_task_indicators": [
                    "create task",
                    "new task",
                    "make task",
                    "build task",
                ],
                "add_dependencies_indicators": [
                    "dependencies",
                    "depends on",
                    "requires",
                    "dependency",
                ],
                "confidence_boost": 0.5,
            },
            "ready_tasks_vs_list_tasks": {
                "ready_tasks_indicators": [
                    "ready",
                    "available",
                    "ready to work",
                    "ready to work on",
                    "can work on",
                    "unblocked",
                    "can do",
                    "work on now",
                ],
                "list_tasks_indicators": [
                    "all tasks",
                    "list all",
                    "show all",
                    "get all",
                    "task list",
                    "tasks in project",
                    "project tasks",
                ],
                "confidence_boost": 0.6,
            },
        }

    async def classify_intent(
        self,
        query_text: str,
        intent_patterns: Dict[str, List[str]],
        context: Optional[ClassificationContext] = None,
        algorithm: ClassificationAlgorithm = ClassificationAlgorithm.HYBRID,
    ) -> List[IntentCandidate]:
        """Classify intent with advanced algorithms and context awareness.

        Args:
            query_text: The query text to classify
            intent_patterns: Available intent patterns for this gateway
            context: Optional context information
            algorithm: Classification algorithm to use

        Returns:
            List of intent candidates sorted by confidence (highest first)
        """
        start_time = asyncio.get_event_loop().time()

        try:
            candidates = []

            if algorithm in [
                ClassificationAlgorithm.PATTERN_MATCHING,
                ClassificationAlgorithm.HYBRID,
            ]:
                pattern_candidates = await self._pattern_matching_classification(
                    query_text, intent_patterns, context
                )
                candidates.extend(pattern_candidates)

            if algorithm in [
                ClassificationAlgorithm.SEMANTIC_SIMILARITY,
                ClassificationAlgorithm.HYBRID,
            ]:
                semantic_candidates = await self._semantic_similarity_classification(
                    query_text, intent_patterns, context
                )
                candidates.extend(semantic_candidates)

            if algorithm in [
                ClassificationAlgorithm.CONTEXT_AWARE,
                ClassificationAlgorithm.HYBRID,
            ]:
                context_candidates = await self._context_aware_classification(
                    query_text, intent_patterns, context
                )
                candidates.extend(context_candidates)

            # Merge and deduplicate candidates
            merged_candidates = self._merge_candidates(candidates)

            # Apply disambiguation rules
            disambiguated_candidates = await self._apply_disambiguation_rules(
                merged_candidates, query_text, context
            )

            # Sort by confidence
            final_candidates = sorted(
                disambiguated_candidates, key=lambda c: c.confidence, reverse=True
            )

            # Record performance metrics
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self.performance_stats["classification_time"].append(execution_time)

            logger.debug(f"Intent classification completed in {execution_time:.2f}ms")

            return final_candidates

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return []

    async def _pattern_matching_classification(
        self,
        query_text: str,
        intent_patterns: Dict[str, List[str]],
        context: Optional[ClassificationContext],
    ) -> List[IntentCandidate]:
        """Enhanced pattern matching with caching and optimization."""
        candidates = []
        query_lower = query_text.lower()

        # Check cache first
        cache_key = f"pattern_{hash(query_lower)}"
        if cache_key in self.pattern_cache:
            return cast(List[IntentCandidate], self.pattern_cache[cache_key])

        for intent, patterns in intent_patterns.items():
            confidence = self._calculate_enhanced_pattern_confidence(
                query_lower, patterns
            )

            # Apply plural/singular disambiguation boost
            if self._has_plural_indicators(query_lower):
                if intent in ["list_project_tasks", "list_projects", "get_all_tasks"]:
                    confidence = min(
                        1.0, confidence + 0.2
                    )  # Boost list operations for plural queries
                elif intent in ["get_task", "get_project"]:
                    confidence = max(
                        0.0, confidence - 0.1
                    )  # Reduce singular operations for plural queries

            # Apply filtering criteria boost for search-related intents
            if self._has_filtering_criteria(query_lower):
                if intent in ["search_tasks", "advanced_search"]:
                    confidence = min(1.0, confidence + 0.3)  # Boost search intents
                elif intent == "list_project_tasks":
                    confidence = max(0.0, confidence - 0.2)  # Reduce simple list intent

            if confidence > 0.1:  # Minimum threshold
                matched_patterns = [
                    p for p in patterns if self._pattern_matches(query_lower, p)
                ]

                candidate = IntentCandidate(
                    intent=intent,
                    confidence=confidence,
                    algorithm=ClassificationAlgorithm.PATTERN_MATCHING,
                    matched_patterns=matched_patterns,
                    context_boost=0.0,
                    tool_name=intent,  # Direct mapping for now
                    gateway_type=context.gateway_type if context else "unknown",
                )
                candidates.append(candidate)

        # Cache results for performance
        self.pattern_cache[cache_key] = candidates

        return candidates

    async def _semantic_similarity_classification(
        self,
        query_text: str,
        intent_patterns: Dict[str, List[str]],
        context: Optional[ClassificationContext],
    ) -> List[IntentCandidate]:
        """Semantic similarity classification using keyword analysis."""
        candidates = []
        query_words = set(query_text.lower().split())

        gateway_type = context.gateway_type if context else "unknown"
        semantic_keywords = self.semantic_keywords.get(gateway_type, {})

        for intent, patterns in intent_patterns.items():
            semantic_score = self._calculate_semantic_similarity(
                query_words, patterns, semantic_keywords
            )

            if semantic_score > 0.2:  # Semantic threshold
                candidate = IntentCandidate(
                    intent=intent,
                    confidence=semantic_score,
                    algorithm=ClassificationAlgorithm.SEMANTIC_SIMILARITY,
                    matched_patterns=[],
                    context_boost=0.0,
                    tool_name=intent,
                    gateway_type=gateway_type,
                )
                candidates.append(candidate)

        return candidates

    async def _context_aware_classification(
        self,
        query_text: str,
        intent_patterns: Dict[str, List[str]],
        context: Optional[ClassificationContext],
    ) -> List[IntentCandidate]:
        """Context-aware classification with user preferences and history."""
        if not context:
            return []

        candidates = []

        # Analyze context factors
        context_factors = self._analyze_context_factors(query_text, context)

        for intent, patterns in intent_patterns.items():
            base_confidence = self._calculate_enhanced_pattern_confidence(
                query_text.lower(), patterns
            )

            if base_confidence > 0.05:  # Lower threshold for context-aware
                context_boost = self._calculate_context_boost(intent, context_factors)
                final_confidence = min(1.0, base_confidence + context_boost)

                candidate = IntentCandidate(
                    intent=intent,
                    confidence=final_confidence,
                    algorithm=ClassificationAlgorithm.CONTEXT_AWARE,
                    matched_patterns=[],
                    context_boost=context_boost,
                    tool_name=intent,
                    gateway_type=context.gateway_type,
                )
                candidates.append(candidate)

        return candidates

    def _has_filtering_criteria(self, query_text: str) -> bool:
        """Detect if query contains filtering criteria that require search_tasks."""
        query_lower = query_text.lower()

        # Text search indicators (new category)
        text_search_indicators = [
            "mention",
            "mentioning",
            "contain",
            "containing",
            "about",
            "that mention",
            "that contain",
            "with text",
            "with word",
            "tasks about",
            "find tasks that",
            "search for tasks that",
        ]

        # Filtering keywords that indicate complex queries
        filtering_indicators = [
            # Complexity filters
            "high complexity",
            "low complexity",
            "medium complexity",
            "complexity",
            "difficult",
            "easy",
            "simple",
            "complex",
            # Assignment filters
            "assigned to",
            "assigned",
            "for",
            "by",
            "owner",
            # Tag filters
            "tagged",
            "tag",
            "with tag",
            "frontend",
            "backend",
            "database",
            "ui",
            "api",
            "testing",
            # Status filters with qualifiers
            "in progress",
            "blocked",
            "done",
            "done",
            # Combination indicators
            "with",
            "having",
            "that have",
            "that are",
            "where",
            "filter",
            "filtered",
            "matching",
            "criteria",
        ]

        # Check for text search indicators first (these are definitive)
        has_text_search = any(
            indicator in query_lower for indicator in text_search_indicators
        )
        if has_text_search:
            return True

        # Count filtering indicators
        filter_count = sum(
            1 for indicator in filtering_indicators if indicator in query_lower
        )

        # Also check for specific patterns
        has_assignment_pattern = bool(
            re.search(r"\b(assigned to|for|by)\s+\w+", query_lower)
        )
        has_complexity_pattern = bool(
            re.search(r"\b(high|low|medium)\s+(complexity|difficult)", query_lower)
        )
        has_tag_pattern = bool(re.search(r"\b(with|tagged|tag)\s+\w+", query_lower))

        # If we have multiple indicators or specific patterns, it's likely a
        # filtered query
        return (
            filter_count >= 2
            or has_assignment_pattern
            or has_complexity_pattern
            or has_tag_pattern
        )

    def _has_plural_indicators(self, query_text: str) -> bool:
        """Detect if query contains plural indicators suggesting list operations."""
        plural_words = ["tasks", "projects", "notes", "items", "all"]
        return any(word in query_text for word in plural_words)

    def _calculate_enhanced_pattern_confidence(
        self, query_text: str, patterns: List[str]
    ) -> float:
        """Enhanced pattern confidence calculation with multiple factors."""
        max_score = 0.0

        for pattern in patterns:
            pattern_lower = pattern.lower()

            # Exact match (highest score)
            if pattern_lower == query_text:
                score = 1.0
            # Exact phrase match
            elif pattern_lower in query_text:
                score = 0.9
            # Word boundary match with flexibility for word order and insertions
            elif self._flexible_word_boundary_match(query_text, pattern_lower):
                score = 0.85
            # Word boundary match (strict)
            elif re.search(r"\b" + re.escape(pattern_lower) + r"\b", query_text):
                score = 0.8
            # Partial word match with enhanced scoring
            elif any(word in query_text for word in pattern_lower.split()):
                words_matched = sum(
                    1 for word in pattern_lower.split() if word in query_text
                )
                total_words = len(pattern_lower.split())
                word_ratio = words_matched / total_words

                # Boost score if all key words are present
                if word_ratio == 1.0:
                    score = 0.8  # Increased from 0.6
                else:
                    score = word_ratio * 0.6
            # Fuzzy match (simple edit distance)
            else:
                score = self._calculate_fuzzy_match(query_text, pattern_lower)

            max_score = max(max_score, score)

        return max_score

    def _flexible_word_boundary_match(self, query_text: str, pattern: str) -> bool:
        """Check if pattern words appear in query with flexible word boundaries."""
        pattern_words = pattern.split()

        # Check if all pattern words appear in order (allowing insertions)
        query_words = query_text.split()
        pattern_idx = 0

        for query_word in query_words:
            if (
                pattern_idx < len(pattern_words)
                and query_word == pattern_words[pattern_idx]
            ):
                pattern_idx += 1

        # Return True if all pattern words were found in order
        return pattern_idx == len(pattern_words)

    def _calculate_semantic_similarity(
        self,
        query_words: Set[str],
        patterns: List[str],
        semantic_keywords: Dict[str, List[str]],
    ) -> float:
        """Calculate semantic similarity using keyword categories."""
        max_similarity = 0.0

        for pattern in patterns:
            pattern_words = set(pattern.lower().split())

            # Direct word overlap
            direct_overlap = len(query_words.intersection(pattern_words))
            direct_score = direct_overlap / len(pattern_words) if pattern_words else 0

            # Semantic category overlap
            semantic_score = 0.0
            for category, keywords in semantic_keywords.items():
                query_category_words = query_words.intersection(set(keywords))
                pattern_category_words = pattern_words.intersection(set(keywords))

                if query_category_words and pattern_category_words:
                    semantic_score += 0.3  # Boost for semantic category match

            total_score = direct_score + semantic_score
            max_similarity = max(max_similarity, total_score)

        return min(1.0, max_similarity)

    def _calculate_fuzzy_match(self, text1: str, text2: str) -> float:
        """Calculate fuzzy matching score based on character overlap."""
        if not text1 or not text2:
            return 0.0

        # Simple character-based similarity
        common_chars = set(text1).intersection(set(text2))
        total_chars = set(text1).union(set(text2))

        if not total_chars:
            return 0.0

        similarity = len(common_chars) / len(total_chars)
        return similarity * 0.3  # Lower weight for fuzzy matches

    def _analyze_context_factors(
        self, query_text: str, context: ClassificationContext
    ) -> Dict[str, Any]:
        """Analyze various context factors for classification."""
        factors: Dict[str, Any] = {}

        # Project context
        if context.project_context:
            factors["project_mentioned"] = (
                context.project_context.lower() in query_text.lower()
            )

        # Task context
        if context.task_context:
            factors["task_mentioned"] = (
                context.task_context.lower() in query_text.lower()
            )

        # Previous intents
        factors["previous_intents"] = (
            context.previous_intents[-3:] if context.previous_intents else []
        )

        # User preferences
        factors["user_preferences"] = context.user_preferences or {}

        # Session context
        factors["session_context"] = context.session_context or {}

        return factors

    def _calculate_context_boost(
        self, intent: str, context_factors: Dict[str, Any]
    ) -> float:
        """Calculate confidence boost based on context factors."""
        boost = 0.0

        # Project context boost
        if context_factors.get("project_mentioned", False):
            boost += self.context_weights["project_context_match"]

        # Task context boost
        if context_factors.get("task_mentioned", False):
            boost += self.context_weights["task_context_match"]

        # Previous intent similarity boost
        previous_intents = context_factors.get("previous_intents", [])
        if intent in previous_intents:
            boost += self.context_weights["previous_intent_similarity"]

        # User preference boost
        user_prefs = context_factors.get("user_preferences", {})
        preferred_tools = user_prefs.get("preferred_tools", [])
        if intent in preferred_tools:
            boost += self.context_weights["user_preference_match"]

        return boost

    def _merge_candidates(
        self, candidates: List[IntentCandidate]
    ) -> List[IntentCandidate]:
        """Merge candidates from different algorithms, combining scores."""
        merged: Dict[str, IntentCandidate] = {}

        for candidate in candidates:
            key = candidate.intent

            if key in merged:
                # Combine scores using weighted average
                existing = merged[key]
                combined_confidence = (existing.confidence + candidate.confidence) / 2
                combined_context_boost = max(
                    existing.context_boost, candidate.context_boost
                )

                merged[key] = IntentCandidate(
                    intent=candidate.intent,
                    confidence=combined_confidence,
                    algorithm=ClassificationAlgorithm.HYBRID,
                    matched_patterns=list(
                        set(existing.matched_patterns + candidate.matched_patterns)
                    ),
                    context_boost=combined_context_boost,
                    tool_name=candidate.tool_name,
                    gateway_type=candidate.gateway_type,
                )
            else:
                merged[key] = candidate

        return list(merged.values())

    async def _apply_disambiguation_rules(
        self,
        candidates: List[IntentCandidate],
        query_text: str,
        context: Optional[ClassificationContext],
    ) -> List[IntentCandidate]:
        """Apply disambiguation rules to resolve conflicts between similar intents."""
        if len(candidates) <= 1:
            return candidates

        query_lower = query_text.lower()

        for rule_name, rule_config in self.disambiguation_rules.items():
            # Find candidates that might need disambiguation
            relevant_candidates = [
                c for c in candidates if self._rule_applies(c.intent, rule_name)
            ]

            if len(relevant_candidates) > 1:
                # Apply disambiguation logic
                for candidate in relevant_candidates:
                    boost = self._calculate_disambiguation_boost(
                        candidate.intent, query_lower, rule_config
                    )
                    candidate.confidence = min(1.0, candidate.confidence + boost)

        return candidates

    def _rule_applies(self, intent: str, rule_name: str) -> bool:
        """Check if a disambiguation rule applies to an intent."""
        rule_mappings = {
            "get_vs_list": ["get_", "list_"],
            "create_vs_update": ["create_", "update_"],
            "status_update_disambiguation": [
                "update_task_status",
                "create_task",
                "assign_task",
                "add_task_note",
            ],
            "assign_vs_reassign": ["assign_", "reassign_"],
            "list_vs_search": ["list_project_tasks", "search_tasks", "advanced_search"],
            "create_task_vs_add_dependencies": ["create_task", "add_task_dependencies"],
            "ready_tasks_vs_list_tasks": ["get_ready_tasks", "list_project_tasks"],
        }

        applicable_patterns = rule_mappings.get(rule_name, [])

        # Handle both prefixes and exact matches
        if rule_name in [
            "list_vs_search",
            "create_task_vs_add_dependencies",
            "status_update_disambiguation",
        ]:
            return intent in applicable_patterns
        else:
            return any(intent.startswith(prefix) for prefix in applicable_patterns)

    def _calculate_disambiguation_boost(
        self, intent: str, query_text: str, rule_config: Dict[str, Any]
    ) -> float:
        """Calculate confidence boost based on disambiguation rules."""
        boost = 0.0

        for indicator_type, indicators in rule_config.items():
            if indicator_type == "confidence_boost":
                continue

            if any(indicator in query_text for indicator in indicators):
                # Handle status_update_disambiguation rule
                if (
                    rule_config.get("target_intent") == "update_task_status"
                    and intent == "update_task_status"
                    and indicator_type in ["status_keywords", "status_phrases"]
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                # Handle list_vs_search rule
                if (
                    intent == "list_project_tasks"
                    and indicator_type == "list_indicators"
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                elif (
                    intent in ["search_tasks", "advanced_search"]
                    and indicator_type == "search_indicators"
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                # Handle create_task_vs_add_dependencies rule
                elif (
                    intent == "create_task"
                    and indicator_type == "create_task_indicators"
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                elif (
                    intent == "add_task_dependencies"
                    and indicator_type == "add_dependencies_indicators"
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                # Handle ready_tasks_vs_list_tasks rule
                elif (
                    intent == "get_ready_tasks"
                    and indicator_type == "ready_tasks_indicators"
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                elif (
                    intent == "list_project_tasks"
                    and indicator_type == "list_tasks_indicators"
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break
                # Handle existing rules
                elif (
                    (
                        intent.startswith("get_")
                        and indicator_type.endswith("get_indicators")
                    )
                    or (
                        intent.startswith("list_")
                        and indicator_type.endswith("list_indicators")
                    )
                    or (
                        intent.startswith("create_")
                        and indicator_type.endswith("create_indicators")
                    )
                    or (
                        intent.startswith("update_")
                        and indicator_type.endswith("update_indicators")
                    )
                    or (
                        intent.startswith("assign_")
                        and indicator_type.endswith("assign_indicators")
                    )
                    or (
                        intent.startswith("reassign_")
                        and indicator_type.endswith("reassign_indicators")
                    )
                ):
                    boost += rule_config.get("confidence_boost", 0.0)
                    break

        # Apply negative boost for conflicting indicators
        for indicator_type, indicators in rule_config.items():
            if indicator_type == "confidence_boost":
                continue

            if any(indicator in query_text for indicator in indicators):
                # Reduce confidence for list_project_tasks when search
                # indicators are present
                if (
                    intent == "list_project_tasks"
                    and indicator_type == "search_indicators"
                ):
                    boost -= rule_config.get("confidence_boost", 0.0)
                    break
                # Reduce confidence for create_task when dependency
                # indicators are present
                elif (
                    intent == "create_task"
                    and indicator_type == "add_dependencies_indicators"
                ):
                    boost -= rule_config.get("confidence_boost", 0.0)
                    break
                # Reduce confidence for search_tasks when pure list
                # indicators are present
                elif (
                    intent in ["search_tasks", "advanced_search"]
                    and indicator_type == "list_indicators"
                ):
                    # Only reduce if no search indicators are also present
                    search_indicators = rule_config.get("search_indicators", [])
                    if not any(
                        search_ind in query_text for search_ind in search_indicators
                    ):
                        boost -= (
                            rule_config.get("confidence_boost", 0.0) * 0.5
                        )  # Smaller reduction
                        break
                # Handle ready_tasks_vs_list_tasks negative boost
                elif (
                    intent == "list_project_tasks"
                    and indicator_type == "ready_tasks_indicators"
                ):
                    boost -= rule_config.get("confidence_boost", 0.0)
                    break
                elif (
                    intent == "get_ready_tasks"
                    and indicator_type == "list_tasks_indicators"
                ):
                    boost -= rule_config.get("confidence_boost", 0.0)
                    break

        return boost

    def _pattern_matches(self, text: str, pattern: str) -> bool:
        """Check if a pattern matches the text."""
        pattern_lower = pattern.lower()

        # Exact match
        if pattern_lower == text:
            return True

        # Phrase match
        if pattern_lower in text:
            return True

        # Word boundary match
        if re.search(r"\b" + re.escape(pattern_lower) + r"\b", text):
            return True

        return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        stats = {}

        for metric, values in self.performance_stats.items():
            if values:
                stats[metric] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p95": (
                        sorted(values)[int(len(values) * 0.95)]
                        if len(values) > 20
                        else max(values)
                    ),
                }

        return stats

    def clear_cache(self) -> None:
        """Clear the pattern cache for memory management."""
        self.pattern_cache.clear()
        logger.debug("Intent classification cache cleared")
