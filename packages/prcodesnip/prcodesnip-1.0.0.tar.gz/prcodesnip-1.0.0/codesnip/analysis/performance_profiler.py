"""
Performance profiling and monitoring for all programming languages
"""
import logging
import time
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    io_operations: int
    network_operations: int

class PerformanceProfiler:
    """Simple performance profiler for code analysis"""
    
    # Language-specific performance tools
    PROFILING_TOOLS = {
        'python': {
            'cpu': ['cProfile', 'py-spy'],
            'memory': ['memory-profiler', 'tracemalloc'],
            'async': ['aiomonitor'],
            'commands': {
                'profile': 'python -m cProfile -o profile.stats',
                'memory': 'mprof run'
            }
        },
        'javascript': {
            'cpu': ['clinic.js', 'node --prof'],
            'memory': ['heapdump', 'node --inspect'],
            'commands': {
                'profile': 'clinic doctor --',
                'memory': 'node --inspect'
            }
        },
        'java': {
            'cpu': ['jvisualvm', 'async-profiler'],
            'memory': ['eclipse-mat', 'jconsole'],
            'commands': {
                'profile': 'java -XX:+FlightRecorder',
                'memory': 'jcmd <pid> GC.run_finalization'
            }
        },
        'go': {
            'cpu': ['go tool pprof'],
            'memory': ['go tool pprof'],
            'commands': {
                'profile': 'go test -cpuprofile cpu.prof',
                'memory': 'go test -memprofile mem.prof'
            }
        },
        'rust': {
            'cpu': ['perf', 'cargo-profiler'],
            'memory': ['valgrind', 'heaptrack'],
            'commands': {
                'profile': 'cargo build --release && perf record',
                'memory': 'valgrind --tool=massif'
            }
        },
        'cpp': {
            'cpu': ['gprof', 'perf'],
            'memory': ['valgrind', 'address-sanitizer'],
            'commands': {
                'profile': 'g++ -pg && gprof',
                'memory': 'valgrind --tool=memcheck'
            }
        }
    }
    
    def __init__(self):
        self.start_time = None
        self.process = None
    
    def start_profiling(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
    
    def stop_profiling(self) -> PerformanceMetrics:
        """Stop profiling and return metrics"""
        if not self.start_time:
            return PerformanceMetrics(0, 0, 0, 0, 0)
        
        execution_time = time.time() - self.start_time
        
        if PSUTIL_AVAILABLE and self.process:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            io_counters = self.process.io_counters()
            
            return PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_info.rss / 1024 / 1024,  # MB
                cpu_usage=cpu_percent,
                io_operations=io_counters.read_count + io_counters.write_count,
                network_operations=0  # Simplified
            )
        else:
            # Fallback when psutil is not available
            return PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=0,  # Not available
                cpu_usage=0,    # Not available
                io_operations=0, # Not available
                network_operations=0
            )
    
    def analyze_performance(self, language: str, code_content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze performance characteristics of code
        
        Args:
            language: Programming language
            code_content: Source code content
            file_path: Optional file path
            
        Returns:
            Performance analysis results
        """
        logger.info(f"⚡ Analyzing performance for {language}")
        
        results = {
            'language': language,
            'performance_score': 100,
            'bottlenecks': [],
            'optimization_suggestions': [],
            'profiling_tools': [],
            'estimated_metrics': {},
            'hotspots': []
        }
        
        # Static performance analysis
        bottlenecks = self._detect_performance_bottlenecks(language, code_content)
        results['bottlenecks'] = bottlenecks
        
        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(language, bottlenecks, code_content)
        results['optimization_suggestions'] = suggestions
        
        # Recommend profiling tools
        tools = self._get_profiling_tools(language)
        results['profiling_tools'] = tools
        
        # Estimate performance metrics
        metrics = self._estimate_performance_metrics(language, code_content)
        results['estimated_metrics'] = metrics
        
        # Identify hotspots
        hotspots = self._identify_performance_hotspots(language, code_content)
        results['hotspots'] = hotspots
        
        # Calculate performance score
        results['performance_score'] = self._calculate_performance_score(results)
        
        return results
    
    def _detect_performance_bottlenecks(self, language: str, code_content: str) -> List[Dict[str, Any]]:
        """Detect potential performance bottlenecks"""
        bottlenecks = []
        
        # Common performance anti-patterns
        patterns = {
            'nested_loops': {
                'pattern': r'for.*for.*{',
                'severity': 'high',
                'description': 'Nested loops can cause O(n²) complexity'
            },
            'string_concat_loop': {
                'pattern': r'(for|while).*\+=.*[\'"]',
                'severity': 'medium', 
                'description': 'String concatenation in loops is inefficient'
            },
            'database_loop': {
                'pattern': r'(for|while).*(select|query|find)',
                'severity': 'high',
                'description': 'Database queries in loops (N+1 problem)'
            },
            'file_io_loop': {
                'pattern': r'(for|while).*(open|read|write)',
                'severity': 'medium',
                'description': 'File I/O operations in loops'
            }
        }
        
        # Language-specific patterns
        if language == 'python':
            patterns.update({
                'list_comprehension_nested': {
                    'pattern': r'\[.*for.*for.*\]',
                    'severity': 'medium',
                    'description': 'Nested list comprehensions can be slow'
                },
                'global_lookup': {
                    'pattern': r'global\s+\w+.*\w+\(',
                    'severity': 'low',
                    'description': 'Global variable lookups are slower than local'
                }
            })
        elif language == 'javascript':
            patterns.update({
                'dom_query_loop': {
                    'pattern': r'(for|while).*querySelector',
                    'severity': 'high',
                    'description': 'DOM queries in loops are expensive'
                },
                'closure_in_loop': {
                    'pattern': r'(for|while).*function\s*\(',
                    'severity': 'medium',
                    'description': 'Creating functions in loops wastes memory'
                }
            })
        elif language == 'java':
            patterns.update({
                'string_concat': {
                    'pattern': r'String.*\+=',
                    'severity': 'medium',
                    'description': 'Use StringBuilder for string concatenation'
                },
                'exception_control': {
                    'pattern': r'try.*catch.*for',
                    'severity': 'high',
                    'description': 'Exceptions for control flow are expensive'
                }
            })
        
        # Search for patterns
        lines = code_content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for name, pattern_info in patterns.items():
                import re
                if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                    bottlenecks.append({
                        'type': name,
                        'line': line_num,
                        'code': line.strip(),
                        'severity': pattern_info['severity'],
                        'description': pattern_info['description'],
                        'suggestion': self._get_bottleneck_suggestion(name, language)
                    })
        
        return bottlenecks
    
    def _generate_optimization_suggestions(self, language: str, bottlenecks: List[Dict], code_content: str) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Bottleneck-specific suggestions
        bottleneck_types = [b['type'] for b in bottlenecks]
        
        if 'nested_loops' in bottleneck_types:
            suggestions.append("🔄 Optimize nested loops - consider using hash maps or more efficient algorithms")
        
        if 'database_loop' in bottleneck_types:
            suggestions.append("🗃️ Avoid N+1 queries - use batch operations or joins instead")
        
        if 'string_concat_loop' in bottleneck_types:
            suggestions.append("📝 Use efficient string building methods (StringBuilder, join, etc.)")
        
        # Language-specific suggestions
        if language == 'python':
            suggestions.extend([
                "🐍 Use list comprehensions and generator expressions",
                "⚡ Consider using NumPy for numerical computations",
                "🔧 Use cProfile to identify actual bottlenecks"
            ])
        elif language == 'javascript':
            suggestions.extend([
                "🌐 Use requestAnimationFrame for DOM updates",
                "📦 Bundle and minify code for production",
                "🚀 Consider Web Workers for CPU-intensive tasks"
            ])
        elif language == 'java':
            suggestions.extend([
                "☕ Use ArrayList instead of Vector for single-threaded code",
                "🏭 Implement object pooling for frequently created objects",
                "📊 Use JVM profiling tools for accurate measurement"
            ])
        elif language == 'go':
            suggestions.extend([
                "🚀 Use goroutines for concurrent processing",
                "📊 Profile with pprof to find actual bottlenecks",
                "🔧 Use sync.Pool for object reuse"
            ])
        elif language == 'rust':
            suggestions.extend([
                "⚡ Use iterators instead of manual loops",
                "🔧 Enable compiler optimizations with --release",
                "📊 Use cargo flamegraph for performance profiling"
            ])
        
        return suggestions
    
    def _get_profiling_tools(self, language: str) -> List[Dict[str, str]]:
        """Get recommended profiling tools for language"""
        if language not in self.PROFILING_TOOLS:
            return []
        
        tools_info = self.PROFILING_TOOLS[language]
        tools = []
        
        for category, tool_list in tools_info.items():
            if category != 'commands':
                for tool in tool_list:
                    tools.append({
                        'name': tool,
                        'category': category,
                        'command': tools_info.get('commands', {}).get(category, f"Use {tool} for {category} profiling")
                    })
        
        return tools
    
    def _estimate_performance_metrics(self, language: str, code_content: str) -> Dict[str, Any]:
        """Estimate performance metrics from static analysis"""
        lines = code_content.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*'))]
        
        # Simple heuristics
        loop_count = len([l for l in code_lines if any(keyword in l.lower() for keyword in ['for', 'while', 'foreach'])])
        function_count = self._count_functions(language, code_content)
        complexity_estimate = max(1, loop_count * 2 + function_count)
        
        return {
            'estimated_complexity': complexity_estimate,
            'loop_count': loop_count,
            'function_count': function_count,
            'code_lines': len(code_lines),
            'estimated_execution_time': f"{complexity_estimate * 0.1:.2f}ms (rough estimate)",
            'memory_estimate': f"{len(code_lines) * 0.5:.1f}KB (very rough estimate)"
        }
    
    def _identify_performance_hotspots(self, language: str, code_content: str) -> List[Dict[str, Any]]:
        """Identify potential performance hotspots"""
        hotspots = []
        lines = code_content.split('\n')
        
        # Look for computationally expensive patterns
        expensive_patterns = [
            (r'sort\s*\(', 'Sorting operation - O(n log n)'),
            (r'recursive.*function|def.*recursive', 'Recursive function - stack overflow risk'),
            (r'regexp?|regex', 'Regular expression - can be expensive'),
            (r'json\.(parse|stringify)', 'JSON parsing/serialization'),
            (r'Math\.(sin|cos|tan|sqrt|pow)', 'Mathematical computations'),
        ]
        
        import re
        for line_num, line in enumerate(lines, 1):
            for pattern, description in expensive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    hotspots.append({
                        'line': line_num,
                        'code': line.strip(),
                        'type': 'computational',
                        'description': description,
                        'severity': 'medium'
                    })
        
        return hotspots
    
    def _calculate_performance_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall performance score"""
        base_score = 100
        
        # Deduct points for bottlenecks
        for bottleneck in results['bottlenecks']:
            if bottleneck['severity'] == 'high':
                base_score -= 20
            elif bottleneck['severity'] == 'medium':
                base_score -= 10
            else:
                base_score -= 5
        
        # Deduct points for hotspots
        hotspot_count = len(results['hotspots'])
        base_score -= min(30, hotspot_count * 3)
        
        # Complexity penalty
        complexity = results['estimated_metrics'].get('estimated_complexity', 1)
        if complexity > 20:
            base_score -= 15
        elif complexity > 10:
            base_score -= 8
        
        return max(0, min(100, base_score))
    
    def _get_bottleneck_suggestion(self, bottleneck_type: str, language: str) -> str:
        """Get specific suggestion for bottleneck type"""
        suggestions = {
            'nested_loops': 'Consider using hash maps or more efficient algorithms',
            'string_concat_loop': 'Use StringBuilder/join operations instead',
            'database_loop': 'Use batch queries or eager loading',
            'file_io_loop': 'Read/write in batches or use buffered I/O',
            'dom_query_loop': 'Cache DOM queries or use event delegation',
            'closure_in_loop': 'Define functions outside loops'
        }
        
        return suggestions.get(bottleneck_type, 'Consider optimizing this pattern')
    
    def _count_functions(self, language: str, code_content: str) -> int:
        """Count functions in code (simple implementation)"""
        import re
        patterns = {
            'python': r'def\s+\w+',
            'javascript': r'function\s+\w+',
            'typescript': r'function\s+\w+',
            'java': r'(public|private|protected).*?\s+\w+\s*\([^)]*\)',
            'go': r'func\s+\w+',
            'rust': r'fn\s+\w+'
        }
        
        pattern = patterns.get(language, r'function\s+\w+')
        return len(re.findall(pattern, code_content))


def analyze_performance(language: str, code_content: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze performance characteristics of code
    
    Args:
        language: Programming language
        code_content: Source code content
        file_path: Optional file path
        
    Returns:
        Performance analysis results
    """
    profiler = PerformanceProfiler()
    return profiler.analyze_performance(language, code_content, file_path)