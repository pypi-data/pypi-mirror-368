"""LLM-based validator for security findings to reduce false positives and generate exploitation analysis."""

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..batch import (
    BatchConfig,
    BatchProcessor,
    BatchStrategy,
    FileAnalysisContext,
    Language,
)
from ..cache import CacheKey, CacheManager, CacheType
from ..config import get_app_cache_dir
from ..credentials import CredentialManager
from ..llm import LLMClient, LLMProvider, create_llm_client
from ..logger import get_logger
from ..resilience import ErrorHandler, ResilienceConfig
from .exploit_generator import ExploitGenerator
from .types import Severity, ThreatMatch

logger = get_logger("llm_validator")

## Here is the toggle for the confidence threshold
CONFIDENCE_THRESHOLD = 0.5


class LLMValidationError(Exception):
    """Exception raised when LLM validation fails."""

    pass


@dataclass
class ValidationResult:
    """Result of LLM validation for a security finding."""

    finding_uuid: str
    is_legitimate: bool
    confidence: float  # 0.0 to 1.0
    reasoning: str
    exploitation_vector: str | None = None
    exploit_poc: list[str] | None = None
    remediation_advice: str | None = None
    severity_adjustment: Severity | None = None  # If severity should be adjusted
    validation_error: str | None = None  # If validation failed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "finding_uuid": self.finding_uuid,
            "is_legitimate": self.is_legitimate,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "exploitation_vector": self.exploitation_vector,
            "exploit_poc": self.exploit_poc,
            "remediation_advice": self.remediation_advice,
            "severity_adjustment": (
                self.severity_adjustment.value if self.severity_adjustment else None
            ),
            "validation_error": self.validation_error,
        }


@dataclass
class ValidationPrompt:
    """Represents a prompt for LLM validation."""

    system_prompt: str
    user_prompt: str
    findings: list[ThreatMatch]
    source_code: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "findings_count": len(self.findings),
            "source_code_size": len(self.source_code),
        }


class LLMValidator:
    """LLM-based validator for security findings."""

    def __init__(
        self,
        credential_manager: CredentialManager,
        cache_manager: CacheManager | None = None,
        metrics_collector=None,
    ):
        """Initialize the LLM validator.

        Args:
            credential_manager: Credential manager for configuration
            cache_manager: Optional cache manager for validation results
            metrics_collector: Optional metrics collector for validation analytics
        """
        logger.info("Initializing LLMValidator")
        self.credential_manager = credential_manager
        self.config = credential_manager.load_config()
        self.exploit_generator = ExploitGenerator(credential_manager)
        self.llm_client: LLMClient | None = None
        self.metrics_collector = metrics_collector
        self.cache_manager = cache_manager

        # Initialize cache manager if not provided (robust to mocked configs)
        try:
            enable_caching_flag = bool(getattr(self.config, "enable_caching", True))
        except Exception:
            enable_caching_flag = True

        if cache_manager is None and enable_caching_flag:
            cache_dir = get_app_cache_dir()
            try:
                max_size_mb_val = getattr(self.config, "cache_max_size_mb", 100)
                max_size_mb_num = (
                    int(max_size_mb_val) if max_size_mb_val is not None else 100
                )
            except Exception:
                max_size_mb_num = 100
            try:
                max_age_hours_val = getattr(self.config, "cache_max_age_hours", 24)
                max_age_hours_num = (
                    int(max_age_hours_val) if max_age_hours_val is not None else 24
                )
            except Exception:
                max_age_hours_num = 24
            self.cache_manager = CacheManager(
                cache_dir=cache_dir,
                max_size_mb=max_size_mb_num,
                max_age_hours=max_age_hours_num,
            )
            logger.info(f"Initialized cache manager for validator at {cache_dir}")

        # Initialize intelligent batch processor for validation
        # Safely coerce config values that may be mocked
        try:
            llm_batch_size_val = getattr(self.config, "llm_batch_size", 5)
            llm_batch_size_num = (
                int(llm_batch_size_val) if llm_batch_size_val is not None else 5
            )
        except Exception:
            llm_batch_size_num = 5

        batch_config = BatchConfig(
            strategy=BatchStrategy.TOKEN_BASED,  # Token-based is best for validation
            min_batch_size=1,
            max_batch_size=min(
                10, llm_batch_size_num
            ),  # Smaller batches for validation
            target_tokens_per_batch=50000,  # Smaller token limit for validation
            max_tokens_per_batch=80000,
            batch_timeout_seconds=180,  # 3 minutes for validation
            max_concurrent_batches=2,  # Conservative concurrency for validation
            group_by_language=False,  # Don't group by language for validation
            group_by_complexity=True,  # Group by complexity for better analysis
        )
        self.batch_processor = BatchProcessor(batch_config, self.metrics_collector)
        logger.info(
            "Initialized BatchProcessor for validation with token-based strategy"
        )

        # Initialize ErrorHandler for validation resilience
        resilience_config = ResilienceConfig(
            enable_circuit_breaker=True,
            failure_threshold=2,  # Lower threshold for validation
            recovery_timeout_seconds=90,  # Faster recovery for validation
            enable_retry=True,
            max_retry_attempts=2,  # Fewer retries for validation
            base_delay_seconds=2.0,  # Longer base delay
            enable_graceful_degradation=True,
        )
        self.error_handler = ErrorHandler(resilience_config, self.metrics_collector)
        logger.info("Initialized ErrorHandler for validation resilience")

        # Initialize LLM client if configured (robust to mocked configs)
        provider_val = getattr(self.config, "llm_provider", None)
        api_key_val = getattr(self.config, "llm_api_key", None)
        if (
            isinstance(provider_val, str)
            and provider_val in {"openai", "anthropic"}
            and isinstance(api_key_val, str)
            and api_key_val
        ):
            logger.info(f"Initializing LLM client for validator: {provider_val}")
            self.llm_client = create_llm_client(
                provider=LLMProvider(provider_val),
                api_key=api_key_val,
                model=getattr(self.config, "llm_model", None),
            )
            logger.info("LLM client initialized successfully for validator")
        else:
            logger.warning(
                "LLM provider not configured, validator will not be functional"
            )

        logger.debug("LLMValidator initialized successfully")

    def validate_findings(
        self,
        findings: list[ThreatMatch],
        source_code: str,
        file_path: str,
        generate_exploits: bool = True,
    ) -> dict[str, ValidationResult]:
        """Validate a list of security findings.

        Args:
            findings: List of threat matches to validate
            source_code: Source code containing the vulnerabilities
            file_path: Path to the source file
            generate_exploits: Whether to generate exploit POCs

        Returns:
            Dictionary mapping finding UUID to validation result
        """
        validation_start_time = time.time()
        logger.info(f"Starting validation of {len(findings)} findings for {file_path}")
        logger.debug(
            f"Generate exploits: {generate_exploits}, Source code length: {len(source_code)} chars"
        )

        if not findings:
            logger.debug("No findings to validate, returning empty result")
            return {}

        if not self.llm_client:
            logger.warning("LLM client not initialized, returning unvalidated results")
            # Return default results when LLM not available
            return self._create_default_results(
                findings, generate_exploits, source_code
            )

        # Run async validation in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self._validate_findings_async(
                findings, source_code, file_path, generate_exploits
            )
        )

    async def _validate_findings_async(
        self,
        findings: list[ThreatMatch],
        source_code: str,
        file_path: str,
        generate_exploits: bool = True,
    ) -> dict[str, ValidationResult]:
        """Enhanced async implementation of findings validation with intelligent batching and caching.

        Args:
            findings: List of threat matches to validate
            source_code: Source code containing the vulnerabilities
            file_path: Path to the source file
            generate_exploits: Whether to generate exploit POCs

        Returns:
            Dictionary mapping finding UUID to validation result
        """
        validation_results = {}

        validation_start_time = time.time()

        # Check cache first if enabled
        cached_results = await self._get_cached_validation_results(
            findings, source_code, file_path
        )
        if cached_results:
            logger.info(f"Found {len(cached_results)} cached validation results")
            validation_results.update(cached_results)

            # Remove cached findings from the list to process
            uncached_findings = [f for f in findings if f.uuid not in cached_results]
            if not uncached_findings:
                logger.info("All validation results found in cache")

                # Record cache hit metrics
                if self.metrics_collector:
                    validation_duration = time.time() - validation_start_time
                    self.metrics_collector.record_histogram(
                        "llm_validation_duration_seconds",
                        validation_duration,
                        labels={"status": "cached"},
                    )
                    self.metrics_collector.record_metric(
                        "llm_validation_requests_total", 1, labels={"status": "cached"}
                    )

                return validation_results
            findings = uncached_findings

        logger.info(
            f"Starting intelligent batch validation for {len(findings)} findings"
        )

        # Create validation contexts for intelligent batching
        validation_contexts = []
        for finding in findings:
            # Create a pseudo file context for batch processing
            # We'll use the finding's complexity and severity to guide batching
            complexity_score = self._calculate_finding_complexity(finding)

            context = FileAnalysisContext(
                file_path=Path(file_path),
                content=finding.code_snippet,  # Use code snippet as content
                language=Language.GENERIC,  # Validation doesn't need language-specific batching
                file_size_bytes=len(finding.code_snippet),
                estimated_tokens=len(finding.code_snippet) // 4,  # Rough estimate
                complexity_score=complexity_score,
                priority=self._get_finding_priority(finding),
                metadata={"finding": finding, "source_code": source_code},
            )
            validation_contexts.append(context)

        # Create intelligent batches using the batch processor
        batches = self.batch_processor.create_batches(
            validation_contexts, model=self.config.llm_model
        )
        logger.info(f"Created {len(batches)} intelligent validation batches")

        # Define batch processing function
        async def process_validation_batch(
            batch_contexts: list[FileAnalysisContext],
        ) -> dict[str, ValidationResult]:
            """Process a batch of validation contexts with resilience."""
            batch_findings = [ctx.metadata["finding"] for ctx in batch_contexts]
            batch_source_code = batch_contexts[0].metadata[
                "source_code"
            ]  # Same for all

            # Check if we should use resilience for this batch
            async def validation_call():
                return await self._validate_single_batch(
                    batch_findings, batch_source_code, file_path, generate_exploits
                )

            # Create fallback function for graceful degradation
            async def validation_fallback(*args, **kwargs):
                logger.warning(
                    f"Validation service degraded, using fallback for {len(batch_findings)} findings"
                )
                fallback_results = {}
                for finding in batch_findings:
                    fallback_results[finding.uuid] = ValidationResult(
                        finding_uuid=finding.uuid,
                        is_legitimate=True,  # Fail open - keep finding as precaution
                        confidence=0.6,  # Medium confidence for fallback
                        reasoning="Validation service degraded, keeping finding as precaution",
                    )
                return fallback_results

            # Execute with comprehensive error recovery
            recovery_result = await self.error_handler.execute_with_recovery(
                validation_call,
                operation_name=f"validation_batch_{len(batch_findings)}_findings",
                circuit_breaker_name="validation_service",
                fallback_func=validation_fallback,
            )

            if recovery_result.success:
                return recovery_result.result
            else:
                # Use fallback results if recovery completely failed
                return await validation_fallback()

        def progress_callback(completed: int, total: int):
            """Progress callback for batch processing."""
            logger.info(f"Validation progress: {completed}/{total} batches completed")

        # Process all batches with intelligent concurrency control
        batch_results = await self.batch_processor.process_batches(
            batches, process_validation_batch, progress_callback
        )

        # Flatten and merge results
        for batch_result in batch_results:
            if batch_result:  # Filter out None results from failed batches
                validation_results.update(batch_result)

        # Cache the new validation results
        await self._cache_validation_results(validation_results, source_code, file_path)

        # Log batch processing metrics
        metrics = self.batch_processor.get_metrics()
        logger.info(f"Validation batch processing completed: {metrics.to_dict()}")

        logger.info(f"Validation completed: {len(validation_results)} total results")

        # Record validation completion metrics
        if self.metrics_collector:
            validation_duration = time.time() - validation_start_time

            # Count legitimate vs false positive findings
            legitimate_count = sum(
                1 for result in validation_results.values() if result.is_legitimate
            )
            false_positive_count = len(validation_results) - legitimate_count

            # Calculate average confidence
            avg_confidence = (
                sum(result.confidence for result in validation_results.values())
                / len(validation_results)
                if validation_results
                else 0
            )

            self.metrics_collector.record_histogram(
                "llm_validation_duration_seconds",
                validation_duration,
                labels={"status": "completed"},
            )
            self.metrics_collector.record_metric(
                "llm_validation_requests_total", 1, labels={"status": "completed"}
            )
            self.metrics_collector.record_metric(
                "llm_validation_findings_total", len(validation_results)
            )
            self.metrics_collector.record_metric(
                "llm_validation_legitimate_total", legitimate_count
            )
            self.metrics_collector.record_metric(
                "llm_validation_false_positives_total", false_positive_count
            )
            self.metrics_collector.record_histogram(
                "llm_validation_confidence_score", avg_confidence
            )

        return validation_results

    async def _get_cached_validation_results(
        self, findings: list[ThreatMatch], source_code: str, file_path: str
    ) -> dict[str, ValidationResult]:
        """Get cached validation results for findings."""
        if not self.cache_manager or not self.config.cache_llm_responses:
            return {}

        cached_results = {}
        try:
            hasher = self.cache_manager.get_hasher()
            for finding in findings:
                # Create cache key for this specific finding validation
                validation_hash = hasher.hash_validation_context(
                    findings=[finding],
                    validator_model=self.config.llm_model or "default",
                    confidence_threshold=CONFIDENCE_THRESHOLD,
                    additional_context={"file_path": file_path},
                )

                cache_key = CacheKey(
                    cache_type=CacheType.VALIDATION_RESULT,
                    content_hash=hasher.hash_content(source_code),
                    metadata_hash=validation_hash,
                )

                cached_result = self.cache_manager.get(cache_key)
                if cached_result and isinstance(cached_result, dict):
                    validation_result = ValidationResult(**cached_result)
                    cached_results[finding.uuid] = validation_result

        except Exception as e:
            logger.warning(f"Failed to retrieve cached validation results: {e}")

        return cached_results

    async def _cache_validation_results(
        self,
        validation_results: dict[str, ValidationResult],
        source_code: str,
        file_path: str,
    ) -> None:
        """Cache validation results."""
        if not self.cache_manager or not self.config.cache_llm_responses:
            return

        try:
            hasher = self.cache_manager.get_hasher()
            content_hash = hasher.hash_content(source_code)

            for uuid, result in validation_results.items():
                # Create a dummy finding for hashing (we'd need the original finding for proper caching)
                validation_hash = hasher.hash_validation_context(
                    findings=[],  # Empty for now - could be improved with original finding
                    validator_model=self.config.llm_model or "default",
                    confidence_threshold=CONFIDENCE_THRESHOLD,
                    additional_context={"file_path": file_path, "uuid": uuid},
                )

                cache_key = CacheKey(
                    cache_type=CacheType.VALIDATION_RESULT,
                    content_hash=content_hash,
                    metadata_hash=validation_hash,
                )

                # Cache for shorter duration than LLM responses (validation can change more often)
                cache_expiry_seconds = (
                    self.config.cache_max_age_hours * 1800
                )  # Half the normal duration
                self.cache_manager.put(
                    cache_key, result.to_dict(), cache_expiry_seconds
                )

        except Exception as e:
            logger.warning(f"Failed to cache validation results: {e}")

    def _calculate_finding_complexity(self, finding: ThreatMatch) -> float:
        """Calculate complexity score for a finding to guide batching."""
        complexity = 0.0

        # Base complexity on severity
        severity_weights = {
            Severity.LOW: 0.2,
            Severity.MEDIUM: 0.4,
            Severity.HIGH: 0.7,
            Severity.CRITICAL: 1.0,
        }
        complexity += severity_weights.get(finding.severity, 0.5)

        # Add complexity based on code snippet length
        snippet_length = len(finding.code_snippet)
        if snippet_length > 500:
            complexity += 0.3
        elif snippet_length > 200:
            complexity += 0.2
        elif snippet_length > 100:
            complexity += 0.1

        # Add complexity based on description length (more complex findings have longer descriptions)
        desc_length = len(finding.description)
        if desc_length > 200:
            complexity += 0.2
        elif desc_length > 100:
            complexity += 0.1

        return min(1.0, complexity)

    def _get_finding_priority(self, finding: ThreatMatch) -> int:
        """Get priority for a finding to guide batching order."""
        # Higher severity = higher priority
        severity_priorities = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
        }
        return severity_priorities.get(finding.severity, 2)

    async def _validate_single_batch(
        self,
        batch_findings: list[ThreatMatch],
        source_code: str,
        file_path: str,
        generate_exploits: bool = True,
    ) -> dict[str, ValidationResult]:
        """Validate a single batch of findings (replacement for the old batch processing logic)."""
        try:
            # Create validation prompt for batch
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(
                batch_findings, source_code, file_path
            )

            logger.debug(
                f"Validating batch of {len(batch_findings)} findings - "
                f"system prompt: {len(system_prompt)} chars, "
                f"user prompt: {len(user_prompt)} chars"
            )

            # Make LLM request
            response = await self.llm_client.complete_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,  # Low temperature for consistent validation
                max_tokens=self.config.llm_max_tokens,
                response_format="json",
            )

            logger.info(
                f"Validation response received for batch, "
                f"content length: {len(response.content)} chars"
            )

            # Parse response
            batch_results = self.parse_validation_response(
                response.content, batch_findings
            )

            # Generate exploit POCs for validated findings if requested
            if generate_exploits:
                await self._generate_exploits_for_batch(
                    batch_results, batch_findings, source_code
                )

            logger.info(f"Validated {len(batch_results)} findings in batch")
            return batch_results

        except Exception as e:
            logger.error(f"Batch validation failed: {e}")
            # Create default results for failed batch
            default_results = {}
            for finding in batch_findings:
                default_results[finding.uuid] = ValidationResult(
                    finding_uuid=finding.uuid,
                    is_legitimate=True,  # Fail open - keep finding if validation fails
                    confidence=0.5,
                    reasoning="Validation failed, keeping finding as precaution",
                    validation_error=str(e),
                )
            return default_results

    async def _generate_exploits_for_batch(
        self,
        validation_results: dict[str, ValidationResult],
        batch_findings: list[ThreatMatch],
        source_code: str,
    ) -> None:
        """Generate exploits for validated findings in a batch."""
        eligible_findings = [
            (uuid, val)
            for uuid, val in validation_results.items()
            if val.is_legitimate and val.confidence >= CONFIDENCE_THRESHOLD
        ]

        logger.info(
            f"Generating exploits for {len(eligible_findings)} validated findings in batch"
        )

        for finding_uuid, validation in eligible_findings:
            finding = next((f for f in batch_findings if f.uuid == finding_uuid), None)
            if finding:
                try:
                    logger.debug(
                        f"Generating exploit POC for validated finding {finding_uuid} "
                        f"(confidence: {validation.confidence:.2f})"
                    )
                    exploit_poc = self.exploit_generator.generate_exploits(
                        finding,
                        source_code,
                        use_llm=self.exploit_generator.is_llm_available(),
                    )
                    if exploit_poc:
                        validation.exploit_poc = exploit_poc
                        logger.debug(
                            f"Generated {len(exploit_poc)} exploit POCs for {finding_uuid}"
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to generate exploit POC for {finding_uuid}: {e}"
                    )

    def _create_default_results(
        self, findings: list[ThreatMatch], generate_exploits: bool, source_code: str
    ) -> dict[str, ValidationResult]:
        """Create default validation results when LLM is not available.

        Args:
            findings: List of findings
            generate_exploits: Whether to generate exploits
            source_code: Source code

        Returns:
            Dictionary of default validation results
        """
        validation_results = {}

        for finding in findings:
            validation_results[finding.uuid] = ValidationResult(
                finding_uuid=finding.uuid,
                is_legitimate=True,  # Default to legitimate when no validation available
                confidence=0.7,  # Medium-high confidence as default
                reasoning="LLM validation not available, finding kept as precaution",
                validation_error="LLM client not initialized",
            )

            # Still try to generate exploit POC if available
            if generate_exploits and self.exploit_generator.is_llm_available():
                try:
                    exploit_poc = self.exploit_generator.generate_exploits(
                        finding, source_code, use_llm=False  # Use template-based
                    )
                    if exploit_poc:
                        validation_results[finding.uuid].exploit_poc = exploit_poc
                except Exception as e:
                    logger.warning(f"Failed to generate exploit POC: {e}")

        return validation_results

    def create_validation_prompt(
        self, findings: list[ThreatMatch], source_code: str, file_path: str
    ) -> ValidationPrompt:
        """Create validation prompt for LLM.

        Args:
            findings: List of findings to validate
            source_code: Source code to analyze
            file_path: Path to the source file

        Returns:
            ValidationPrompt object
        """
        logger.debug(f"Creating validation prompt for {len(findings)} findings")

        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(findings, source_code, file_path)

        prompt = ValidationPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            findings=findings,
            source_code=source_code,
        )

        logger.debug("Validation prompt created successfully")
        return prompt

    def parse_validation_response(
        self, response_text: str, findings: list[ThreatMatch]
    ) -> dict[str, ValidationResult]:
        """Parse LLM validation response.

        Args:
            response_text: Raw response from LLM
            findings: Original findings being validated

        Returns:
            Dictionary mapping finding UUID to validation result
        """
        logger.debug(f"Parsing validation response for {len(findings)} findings")

        if not response_text or not response_text.strip():
            logger.warning("Empty validation response")
            return {}

        try:
            # Parse JSON response
            data = json.loads(response_text)
            validations = data.get("validations", [])

            results = {}
            finding_map = {f.uuid: f for f in findings}

            for validation_data in validations:
                finding_uuid = validation_data.get("finding_uuid")
                if not finding_uuid or finding_uuid not in finding_map:
                    logger.warning(
                        f"Unknown finding UUID in validation: {finding_uuid}"
                    )
                    continue

                # Parse severity adjustment if present
                severity_adjustment = None
                if "severity_adjustment" in validation_data:
                    try:
                        severity_adjustment = Severity(
                            validation_data["severity_adjustment"]
                        )
                    except ValueError:
                        logger.warning(
                            f"Invalid severity adjustment: {validation_data['severity_adjustment']}"
                        )

                result = ValidationResult(
                    finding_uuid=finding_uuid,
                    is_legitimate=validation_data.get("is_legitimate", True),
                    confidence=float(validation_data.get("confidence", 0.5)),
                    reasoning=validation_data.get("reasoning", ""),
                    exploitation_vector=validation_data.get("exploitation_vector"),
                    exploit_poc=validation_data.get("exploit_poc", []),
                    remediation_advice=validation_data.get("remediation_advice"),
                    severity_adjustment=severity_adjustment,
                    validation_error=None,
                )

                results[finding_uuid] = result
                logger.debug(
                    f"Parsed validation for {finding_uuid}: legitimate={result.is_legitimate}"
                )

            logger.info(f"Successfully parsed {len(results)} validation results")
            return results

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation response as JSON: {e}")
            raise LLMValidationError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Error parsing validation response: {e}")
            raise LLMValidationError(f"Error parsing response: {e}")

    def _create_system_prompt(self) -> str:
        """Create system prompt for validation.

        Returns:
            System prompt string
        """
        return """You are a senior security engineer performing vulnerability validation.
Your task is to analyze security findings and determine if they are legitimate vulnerabilities or false positives.

For each finding, you should:
1. Analyze the code context to understand the vulnerability
2. Determine if the finding is a legitimate security issue
3. Assess the exploitability and real-world impact
4. Provide confidence in your assessment (0.0 to 1.0)
5. Explain your reasoning clearly
6. If legitimate, describe the exploitation vector
7. Suggest remediation if the finding is valid
8. Recommend severity adjustment if the current severity is incorrect

Consider factors like:
- Input validation and sanitization
- Authentication and authorization checks
- Framework-provided protections
- Environmental context (is this test code, example code, etc.)
- Actual exploitability vs theoretical vulnerability
- Business logic and application context

Be thorough but practical - focus on real security impact."""

    def _create_user_prompt(
        self, findings: list[ThreatMatch], source_code: str, file_path: str
    ) -> str:
        """Create user prompt for validation.

        Args:
            findings: Findings to validate
            source_code: Source code context
            file_path: File path

        Returns:
            User prompt string
        """
        # Truncate very long code
        max_code_length = 10000
        if len(source_code) > max_code_length:
            source_code = (
                source_code[:max_code_length] + "\n... [truncated for analysis]"
            )

        findings_json = []
        for finding in findings:
            findings_json.append(
                {
                    "uuid": finding.uuid,
                    "rule_name": finding.rule_name,
                    "description": finding.description,
                    "category": finding.category.value,
                    "severity": finding.severity.value,
                    "line_number": finding.line_number,
                    "code_snippet": finding.code_snippet,
                    "confidence": finding.confidence,
                }
            )

        prompt = f"""Validate the following security findings for the file {file_path}:

**Source Code:**
```
{source_code}
```

**Security Findings to Validate:**
{json.dumps(findings_json, indent=2)}

For each finding, determine if it's a legitimate vulnerability or a false positive.

Response format (valid JSON only):
{{
  "validations": [
    {{
      "finding_uuid": "uuid-here",
      "is_legitimate": true,
      "confidence": 0.9,
      "reasoning": "Detailed explanation of why this is/isn't a real vulnerability",
      "exploitation_vector": "How an attacker could exploit this (if legitimate)",
      "remediation_advice": "How to fix this vulnerability (if legitimate)",
      "severity_adjustment": "high"
    }}
  ]
}}

Important:
- is_legitimate must be a boolean (true/false)
- confidence must be a number between 0.0 and 1.0
- severity_adjustment is optional and should only be provided if the current severity is incorrect
- Consider the full context when making determinations
- Be specific about why something is or isn't a vulnerability"""

        return prompt

    def filter_false_positives(
        self,
        findings: list[ThreatMatch],
        validation_results: dict[str, ValidationResult],
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ) -> list[ThreatMatch]:
        """Filter out false positives based on validation results.

        Args:
            findings: Original findings
            validation_results: Validation results
            confidence_threshold: Minimum confidence to consider a finding legitimate

        Returns:
            Filtered list of legitimate findings
        """
        logger.debug(
            f"Filtering {len(findings)} findings with confidence threshold {confidence_threshold}"
        )

        legitimate_findings = []

        for finding in findings:
            validation = validation_results.get(finding.uuid)

            # If no validation result, keep the finding (fail-open)
            if not validation:
                logger.debug(f"No validation for {finding.uuid}, keeping finding")
                legitimate_findings.append(finding)
                continue

            # Check if legitimate with sufficient confidence
            if (
                validation.is_legitimate
                and validation.confidence >= confidence_threshold
            ):
                # Apply severity adjustment if recommended
                if validation.severity_adjustment:
                    logger.info(
                        f"Adjusting severity for {finding.uuid} from {finding.severity} to {validation.severity_adjustment}"
                    )
                    finding.severity = validation.severity_adjustment

                # Add validation metadata to finding
                finding.remediation = (
                    validation.remediation_advice or finding.remediation
                )
                if validation.exploit_poc:
                    finding.exploit_examples.extend(validation.exploit_poc)

                legitimate_findings.append(finding)
                logger.debug(f"Finding {finding.uuid} validated as legitimate")
            else:
                logger.info(
                    f"Filtering out finding {finding.uuid} as false positive (legitimate={validation.is_legitimate}, confidence={validation.confidence})"
                )

        logger.info(
            f"Filtered {len(findings)} findings to {len(legitimate_findings)} legitimate findings"
        )
        return legitimate_findings

    def get_validation_stats(
        self, validation_results: dict[str, ValidationResult]
    ) -> dict[str, Any]:
        """Get statistics about validation results.

        Args:
            validation_results: Validation results

        Returns:
            Dictionary with validation statistics
        """
        total = len(validation_results)
        legitimate = sum(1 for v in validation_results.values() if v.is_legitimate)
        false_positives = total - legitimate
        avg_confidence = (
            sum(v.confidence for v in validation_results.values()) / total
            if total > 0
            else 0
        )

        stats = {
            "total_validated": total,
            "legitimate_findings": legitimate,
            "false_positives": false_positives,
            "false_positive_rate": false_positives / total if total > 0 else 0,
            "average_confidence": avg_confidence,
            "validation_errors": sum(
                1 for v in validation_results.values() if v.validation_error
            ),
        }

        logger.debug(f"Validation stats: {stats}")
        return stats
