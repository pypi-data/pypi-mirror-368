"""
Memory leak detection and analysis for all programming languages
"""
import logging
import subprocess
import tempfile
import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import shlex

logger = logging.getLogger(__name__)

class MemoryLeakDetector:
    """Detects memory leaks and performance issues across all programming languages"""
    
    # Language-specific memory leak patterns and tools
    MEMORY_TOOLS = {
        'python': {
            'static_tools': ['bandit', 'memory-profiler', 'pympler', 'tracemalloc'],
            'runtime_tools': ['memory-profiler', 'psutil', 'objgraph'],
            'leak_patterns': [
                r'global\s+\w+\s*=\s*\[\]',  # Global mutable defaults
                r'def\s+\w+\([^)]*=\s*\[\]',  # Mutable default arguments
                r'while\s+True.*(?!break)',   # Infinite loops without break
                r'\.append\([^)]*\).*while',  # Growing lists in loops
                r'cache\s*=\s*\{\}',          # Unbounded caches
            ],
            'memory_issues': [
                'Large data structures in global scope',
                'Circular references with __del__',
                'Unclosed file handles',
                'Growing caches without limits',
                'Event listener leaks'
            ]
        },
        'javascript': {
            'static_tools': ['eslint-plugin-node', 'clinic.js', 'heapdump'],
            'runtime_tools': ['clinic.js', 'node --inspect', 'heapdump'],
            'leak_patterns': [
                r'setInterval\([^)]*\)(?!.*clearInterval)',  # Uncleaned intervals
                r'addEventListener\([^)]*\)(?!.*removeEventListener)',  # Event leaks
                r'new\s+Array\(\d{4,}\)',     # Large array allocations
                r'while\s*\(.*\).*(?!break)',  # Potential infinite loops
                r'global\.\w+\s*=',           # Global variable assignments
                r'var\s+\w+\s*=\s*\[\].*while',  # Growing arrays in loops
            ],
            'memory_issues': [
                'DOM element references not cleared',
                'Event listeners not removed',
                'Timers not cleared (setTimeout/setInterval)',
                'Closure capturing large objects',
                'WeakMap/WeakSet not used appropriately'
            ]
        },
        'typescript': {
            'static_tools': ['eslint-plugin-node', 'clinic.js', 'typescript'],
            'runtime_tools': ['clinic.js', 'node --inspect'],
            'leak_patterns': [
                r'setInterval\([^)]*\)(?!.*clearInterval)',
                r'addEventListener\([^)]*\)(?!.*removeEventListener)',
                r'new\s+Array<.*>\(\d{4,}\)',
                r'private\s+.*:\s*.*\[\]\s*=\s*\[\]',  # Growing private arrays
            ],
            'memory_issues': [
                'Type definitions with circular references',
                'Large union types causing compilation overhead',
                'Unused imports and dependencies'
            ]
        },
        'java': {
            'static_tools': ['spotbugs', 'pmd', 'checkstyle', 'sonarqube'],
            'runtime_tools': ['jvisualvm', 'jconsole', 'eclipse mat', 'async-profiler'],
            'leak_patterns': [
                r'static\s+.*\s+(List|Map|Set).*=.*new',  # Static collections
                r'\.add\(.*\).*while',        # Growing collections in loops
                r'new\s+.*\[\d{4,}\]',        # Large array allocations
                r'String\s+.*\+=.*while',     # String concatenation in loops
                r'ThreadLocal.*(?!\.remove\(\))', # ThreadLocal without cleanup
            ],
            'memory_issues': [
                'Static collections growing unbounded',
                'String concatenation in loops',
                'Unclosed resources (streams, connections)',
                'ThreadLocal variables not cleaned',
                'Inner class references to outer class',
                'Event listener leaks in Swing/JavaFX'
            ]
        },
        'csharp': {
            'static_tools': ['dotnet-analyzers', 'sonaranalyzer.csharp', 'roslynator'],
            'runtime_tools': ['dotmemory', 'perfview', 'diagnostic-tools'],
            'leak_patterns': [
                r'static.*List<.*>.*=.*new',   # Static collections
                r'event\s+.*\+=.*(?!-=)',      # Event subscriptions without unsubscription
                r'new\s+.*\[\d{4,}\]',         # Large array allocations
                r'while\s*\(.*\).*\.Add\(',    # Growing collections in loops
                r'IDisposable.*(?!using\s)',    # IDisposable not in using block
            ],
            'memory_issues': [
                'Event handler leaks',
                'IDisposable objects not disposed',
                'Static event handlers',
                'Large object heap pressure',
                'Finalizer queue buildup'
            ]
        },
        'cpp': {
            'static_tools': ['valgrind', 'cppcheck', 'clang-static-analyzer', 'address-sanitizer'],
            'runtime_tools': ['valgrind', 'address-sanitizer', 'memory-sanitizer', 'dr-memory'],
            'leak_patterns': [
                r'new\s+.*(?!delete)',         # new without delete
                r'malloc\s*\([^)]*\)(?!.*free)', # malloc without free
                r'new\[\].*(?!delete\[\])',    # new[] without delete[]
                r'std::make_shared.*(?!reset|nullptr)', # shared_ptr leaks
                r'while\s*\(.*\).*new\s+',     # Memory allocation in loops
            ],
            'memory_issues': [
                'Raw pointers without proper cleanup',
                'Memory allocated with new/malloc not freed',
                'Array new/delete mismatch (new[] vs delete)',
                'Double free errors',
                'Use after free errors',
                'Circular references with shared_ptr'
            ]
        },
        'c': {
            'static_tools': ['valgrind', 'cppcheck', 'clang-static-analyzer', 'splint'],
            'runtime_tools': ['valgrind', 'address-sanitizer', 'dr-memory'],
            'leak_patterns': [
                r'malloc\s*\([^)]*\)(?!.*free)',  # malloc without free
                r'calloc\s*\([^)]*\)(?!.*free)',  # calloc without free
                r'realloc\s*\([^)]*\)(?!.*free)', # realloc without free
                r'fopen\s*\([^)]*\)(?!.*fclose)', # fopen without fclose
                r'while\s*\(.*\).*malloc',        # malloc in loops
            ],
            'memory_issues': [
                'Memory allocated not freed',
                'File handles not closed',
                'Buffer overflows',
                'Use after free',
                'Double free errors'
            ]
        },
        'rust': {
            'static_tools': ['clippy', 'miri', 'rust-analyzer'],
            'runtime_tools': ['miri', 'valgrind', 'heaptrack'],
            'leak_patterns': [
                r'std::mem::forget\(',         # Explicit memory leaks
                r'Box::leak\(',                # Box leaks
                r'Rc::new.*clone\(\).*loop',   # Potential Rc cycles
                r'RefCell.*borrow\(\).*loop',  # RefCell borrow leaks
            ],
            'memory_issues': [
                'Reference counted cycles (Rc<RefCell<T>>)',
                'Memory leaks with std::mem::forget',
                'Unsafe code memory issues',
                'Large allocations on stack'
            ]
        },
        'go': {
            'static_tools': ['go vet', 'golangci-lint', 'staticcheck'],
            'runtime_tools': ['go tool pprof', 'go tool trace', 'delve'],
            'leak_patterns': [
                r'make\(.*,\s*\d{4,}\)',       # Large slice/map allocations
                r'for\s+.*\{.*make\(',         # Allocations in loops
                r'go\s+func\(\).*\{.*for.*\}', # Goroutine leaks
                r'defer.*(?!\.Close\(\))',      # Missing defer cleanup
            ],
            'memory_issues': [
                'Goroutine leaks',
                'Channel leaks (not closed)',
                'Large slice growth',
                'Map growth without cleanup',
                'Timer leaks'
            ]
        },
        'swift': {
            'static_tools': ['swiftlint', 'swift-format'],
            'runtime_tools': ['instruments', 'xcode-memory-debugger'],
            'leak_patterns': [
                r'strong\s+.*=.*\{.*self\.',   # Strong reference cycles
                r'@escaping.*\{.*self\.',       # Escaping closures capturing self
                r'NotificationCenter.*addObserver.*(?!removeObserver)', # Observer leaks
            ],
            'memory_issues': [
                'Strong reference cycles',
                'Closure capture cycles',
                'Notification observer leaks',
                'Delegate reference cycles'
            ]
        },
        'kotlin': {
            'static_tools': ['detekt', 'ktlint'],
            'runtime_tools': ['android studio profiler', 'leak-canary'],
            'leak_patterns': [
                r'companion object.*var.*=',    # Companion object leaks
                r'\.addListener\(.*(?!removeListener)', # Listener leaks
                r'GlobalScope\.launch',         # GlobalScope usage
            ],
            'memory_issues': [
                'Activity/Fragment leaks on Android',
                'Listener registration without cleanup',
                'Coroutine scope leaks',
                'Singleton holding context references'
            ]
        }
    }
    
    def __init__(self):
        self.temp_dir = None
        self.analysis_results = {}
    
    def analyze_memory_usage(self, language: str, code_content: str, 
                           file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive memory leak and performance analysis
        
        Args:
            language: Programming language
            code_content: Source code content
            file_path: Optional file path for context
            
        Returns:
            Memory analysis results
        """
        logger.info(f"🧠 Analyzing memory usage for {language}")
        
        if language not in self.MEMORY_TOOLS:
            return self._generic_memory_analysis(language, code_content)
        
        results = {
            'language': language,
            'memory_score': 100,  # Start with perfect score
            'leak_risks': [],
            'performance_issues': [],
            'memory_patterns': [],
            'recommendations': [],
            'tools_used': [],
            'static_analysis': {},
            'runtime_suggestions': []
        }
        
        # Static analysis for memory patterns
        static_results = self._static_memory_analysis(language, code_content)
        results.update(static_results)
        
        # Dynamic analysis recommendations
        dynamic_suggestions = self._get_dynamic_analysis_suggestions(language, file_path)
        results['runtime_suggestions'].extend(dynamic_suggestions)
        
        # Calculate memory score
        results['memory_score'] = self._calculate_memory_score(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_memory_recommendations(language, results)
        
        return results
    
    def _static_memory_analysis(self, language: str, code_content: str) -> Dict[str, Any]:
        """Run static analysis for memory leak patterns"""
        
        language_config = self.MEMORY_TOOLS[language]
        results = {
            'leak_risks': [],
            'performance_issues': [],
            'memory_patterns': [],
            'tools_used': []
        }
        
        # Check for language-specific leak patterns
        for pattern in language_config['leak_patterns']:
            matches = re.finditer(pattern, code_content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                results['leak_risks'].append({
                    'type': 'pattern_match',
                    'pattern': pattern,
                    'line': line_num,
                    'code': match.group().strip(),
                    'severity': self._assess_pattern_severity(pattern, language),
                    'description': self._get_pattern_description(pattern, language)
                })
        
        # Analyze code structure for memory issues
        structure_analysis = self._analyze_code_structure(language, code_content)
        results['performance_issues'].extend(structure_analysis)
        
        # Check for common memory anti-patterns
        anti_patterns = self._detect_memory_antipatterns(language, code_content)
        results['memory_patterns'].extend(anti_patterns)
        
        return results
    
    def _analyze_code_structure(self, language: str, code_content: str) -> List[Dict[str, Any]]:
        """Analyze code structure for memory-related issues"""
        issues = []
        
        # Common patterns across languages
        patterns = {
            'large_loops': r'for\s*\([^)]*\d{3,}[^)]*\)|while\s*\([^)]*\d{3,}',
            'nested_loops': r'for\s*\([^{]*\{[^}]*for\s*\(',
            'recursive_calls': r'def\s+(\w+).*\1\s*\(',
            'global_variables': r'(global|static|var)\s+\w+.*=.*(\[|\{)',
            'large_allocations': r'(new|malloc|Array|List).*\d{4,}'
        }
        
        for issue_type, pattern in patterns.items():
            matches = re.finditer(pattern, code_content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                issues.append({
                    'type': issue_type,
                    'line': line_num,
                    'code': match.group().strip()[:100],  # Limit length
                    'severity': 'medium',
                    'impact': self._get_performance_impact(issue_type)
                })
        
        return issues
    
    def _detect_memory_antipatterns(self, language: str, code_content: str) -> List[Dict[str, Any]]:
        """Detect memory anti-patterns specific to language"""
        
        antipatterns = []
        language_issues = self.MEMORY_TOOLS[language]['memory_issues']
        
        # Language-specific anti-pattern detection
        if language == 'python':
            # Check for mutable default arguments
            mutable_defaults = re.finditer(r'def\s+\w+\([^=]*=\s*(\[\]|\{\})', code_content)
            for match in mutable_defaults:
                line_num = code_content[:match.start()].count('\n') + 1
                antipatterns.append({
                    'type': 'mutable_default_argument',
                    'line': line_num,
                    'severity': 'high',
                    'description': 'Mutable default arguments can cause memory leaks',
                    'solution': 'Use None as default and create mutable inside function'
                })
        
        elif language == 'javascript':
            # Check for potential closure memory leaks
            closures = re.finditer(r'function.*\{.*var\s+\w+.*=.*function', code_content, re.DOTALL)
            for match in closures:
                line_num = code_content[:match.start()].count('\n') + 1
                antipatterns.append({
                    'type': 'closure_memory_leak',
                    'line': line_num,
                    'severity': 'medium',
                    'description': 'Potential closure memory leak',
                    'solution': 'Ensure closures do not capture unnecessary variables'
                })
        
        elif language in ['java', 'csharp']:
            # Check for static collections
            static_collections = re.finditer(r'static.*?(List|Map|Set|Dictionary|Array).*=.*new', code_content)
            for match in static_collections:
                line_num = code_content[:match.start()].count('\n') + 1
                antipatterns.append({
                    'type': 'static_collection_leak',
                    'line': line_num,
                    'severity': 'high',
                    'description': 'Static collections can grow unbounded',
                    'solution': 'Use bounded caches or periodic cleanup'
                })
        
        elif language in ['cpp', 'c']:
            # Check for potential memory leaks
            allocations = re.finditer(r'(malloc|new|calloc)\s*\([^)]*\)', code_content)
            frees = re.finditer(r'(free|delete)\s*\([^)]*\)', code_content)
            
            alloc_count = len(list(allocations))
            free_count = len(list(frees))
            
            if alloc_count > free_count:
                antipatterns.append({
                    'type': 'potential_memory_leak',
                    'severity': 'critical',
                    'description': f'Found {alloc_count} allocations but only {free_count} frees',
                    'solution': 'Ensure every malloc/new has corresponding free/delete'
                })
        
        return antipatterns
    
    def _get_dynamic_analysis_suggestions(self, language: str, file_path: Optional[str]) -> List[str]:
        """Get suggestions for dynamic memory analysis"""
        
        suggestions = []
        language_config = self.MEMORY_TOOLS[language]
        
        for tool in language_config['runtime_tools']:
            if language == 'python':
                if 'memory-profiler' in tool:
                    suggestions.append("Run: @profile decorator + kernprof -l -v script.py")
                elif 'psutil' in tool:
                    suggestions.append("Monitor memory: psutil.Process().memory_info()")
                elif 'objgraph' in tool:
                    suggestions.append("Track object growth: objgraph.show_growth()")
                    
            elif language == 'javascript':
                if 'clinic.js' in tool:
                    suggestions.append("Run: clinic doctor -- node script.js")
                elif 'heapdump' in tool:
                    suggestions.append("Generate heap dump: process.kill(process.pid, 'SIGUSR2')")
                    
            elif language == 'java':
                if 'jvisualvm' in tool:
                    suggestions.append("Profile with: jvisualvm --jdkhome $JAVA_HOME")
                elif 'eclipse mat' in tool:
                    suggestions.append("Analyze heap dump with Eclipse Memory Analyzer")
                    
            elif language == 'cpp':
                if 'valgrind' in tool:
                    suggestions.append("Run: valgrind --leak-check=full ./program")
                elif 'address-sanitizer' in tool:
                    suggestions.append("Compile with: -fsanitize=address -g")
                    
            elif language == 'go':
                if 'pprof' in tool:
                    suggestions.append("Profile with: go tool pprof http://localhost:6060/debug/pprof/heap")
                    
        return suggestions
    
    def _calculate_memory_score(self, results: Dict[str, Any]) -> int:
        """Calculate memory safety score"""
        
        score = 100
        
        # Deduct points for issues
        for risk in results['leak_risks']:
            if risk['severity'] == 'critical':
                score -= 20
            elif risk['severity'] == 'high':
                score -= 10
            elif risk['severity'] == 'medium':
                score -= 5
            else:
                score -= 2
        
        for issue in results['performance_issues']:
            if issue['severity'] == 'high':
                score -= 8
            elif issue['severity'] == 'medium':
                score -= 4
            else:
                score -= 2
        
        for pattern in results['memory_patterns']:
            if pattern['severity'] == 'critical':
                score -= 15
            elif pattern['severity'] == 'high':
                score -= 8
            elif pattern['severity'] == 'medium':
                score -= 4
        
        return max(0, min(100, score))
    
    def _generate_memory_recommendations(self, language: str, results: Dict[str, Any]) -> List[str]:
        """Generate memory improvement recommendations"""
        
        recommendations = []
        
        # General recommendations based on score
        score = results['memory_score']
        if score < 60:
            recommendations.append("🚨 Critical: Immediate memory audit required")
            recommendations.append("📊 Run comprehensive memory profiling")
            recommendations.append("🔍 Review all dynamic allocations")
        elif score < 80:
            recommendations.append("⚠️ Moderate memory issues detected")
            recommendations.append("🧹 Implement regular memory cleanup routines")
        
        # Language-specific recommendations
        if language == 'python':
            recommendations.extend([
                "🐍 Use __slots__ for memory-efficient classes",
                "📦 Consider using generators instead of lists for large datasets",
                "🗑️ Implement proper cleanup in __del__ methods",
                "📈 Use memory-profiler to identify hotspots"
            ])
            
        elif language == 'javascript':
            recommendations.extend([
                "🌐 Remove event listeners when components unmount",
                "⏰ Clear intervals and timeouts properly",
                "💾 Use WeakMap/WeakSet for temporary object references",
                "🔧 Avoid global variables and closures capturing large objects"
            ])
            
        elif language in ['java', 'csharp']:
            recommendations.extend([
                "🏭 Use object pools for frequently allocated objects",
                "📚 Implement bounded caches with LRU eviction",
                "🧵 Clean up ThreadLocal variables",
                "🔧 Use try-with-resources for resource management"
            ])
            
        elif language in ['cpp', 'c']:
            recommendations.extend([
                "🎯 Use smart pointers (shared_ptr, unique_ptr) instead of raw pointers",
                "🛡️ Implement RAII pattern for resource management",
                "🔍 Run static analysis tools regularly",
                "⚡ Consider using sanitizers during development"
            ])
            
        elif language == 'go':
            recommendations.extend([
                "🏃 Monitor goroutine counts in production",
                "📊 Use sync.Pool for frequently allocated objects",
                "🔧 Properly close channels and context cancellation",
                "📈 Profile with pprof regularly"
            ])
        
        return recommendations
    
    def _generic_memory_analysis(self, language: str, code_content: str) -> Dict[str, Any]:
        """Generic memory analysis for unsupported languages"""
        
        return {
            'language': language,
            'memory_score': 75,  # Neutral score
            'leak_risks': [],
            'performance_issues': [],
            'memory_patterns': [],
            'recommendations': [
                f"Memory analysis for {language} not yet fully supported",
                "Consider using language-specific profiling tools",
                "Implement regular memory monitoring",
                "Follow language best practices for memory management"
            ],
            'tools_used': ['generic_analysis'],
            'runtime_suggestions': [
                f"Research memory profiling tools for {language}",
                "Implement custom memory monitoring"
            ]
        }
    
    def _assess_pattern_severity(self, pattern: str, language: str) -> str:
        """Assess severity of detected pattern"""
        
        critical_patterns = ['malloc.*(?!free)', 'new.*(?!delete)', 'static.*List.*=.*new']
        high_patterns = ['while.*True.*(?!break)', r'global.*=.*\[\]', 'setInterval.*(?!clear)']
        
        if any(p in pattern for p in critical_patterns):
            return 'critical'
        elif any(p in pattern for p in high_patterns):
            return 'high'
        else:
            return 'medium'
    
    def _get_pattern_description(self, pattern: str, language: str) -> str:
        """Get human-readable description of pattern"""
        
        descriptions = {
            'malloc.*(?!free)': 'Memory allocation without corresponding free()',
            'new.*(?!delete)': 'Object allocation without corresponding delete',
            'while.*True.*(?!break)': 'Potential infinite loop',
            r'global.*=.*\[\]': 'Global mutable container that can grow unbounded',
            'setInterval.*(?!clear)': 'Timer created without cleanup mechanism'
        }
        
        for desc_pattern, description in descriptions.items():
            if desc_pattern in pattern:
                return description
        
        return 'Potential memory issue detected'
    
    def _get_performance_impact(self, issue_type: str) -> str:
        """Get performance impact description"""
        
        impacts = {
            'large_loops': 'High CPU usage and potential memory growth',
            'nested_loops': 'Exponential complexity, poor performance',
            'recursive_calls': 'Stack overflow risk and performance degradation',
            'global_variables': 'Memory bloat and reduced garbage collection efficiency',
            'large_allocations': 'Memory pressure and potential out-of-memory errors'
        }
        
        return impacts.get(issue_type, 'Performance impact needs assessment')

def analyze_memory_leaks(language: str, code_content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze code for memory leaks and performance issues
    
    Args:
        language: Programming language
        code_content: Source code to analyze
        file_path: Optional file path for context
        
    Returns:
        Memory analysis results
    """
    detector = MemoryLeakDetector()
    return detector.analyze_memory_usage(language, code_content, file_path)