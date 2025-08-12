"""
Architecture analysis and improvement suggestions for all programming languages
"""
import logging
import re
import os
import ast
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ArchitectureIssue:
    """Represents an architecture issue found in code"""
    type: str
    severity: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    impact: Optional[str] = None

@dataclass
class DesignPattern:
    """Represents a design pattern recommendation"""
    pattern_name: str
    applicability: str
    benefit: str
    implementation_hint: str
    languages: List[str]

class ArchitectureAnalyzer:
    """Analyzes code architecture and provides improvement suggestions"""
    
    # Design patterns database for different languages
    DESIGN_PATTERNS = {
        'creational': [
            DesignPattern(
                'Factory Method',
                'When you need to create objects without specifying their exact classes',
                'Promotes loose coupling by eliminating the need to bind application-specific classes',
                'Create an interface for creating objects, but let subclasses decide which class to instantiate',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            ),
            DesignPattern(
                'Singleton',
                'When you need exactly one instance of a class',
                'Ensures a class has only one instance and provides global access to it',
                'Use dependency injection or module-level variables instead of traditional singleton',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript']
            ),
            DesignPattern(
                'Builder',
                'When constructing complex objects with many optional parameters',
                'Separates construction of complex object from its representation',
                'Create a separate builder class that constructs the object step by step',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            )
        ],
        'structural': [
            DesignPattern(
                'Adapter',
                'When you need to use an existing class with an incompatible interface',
                'Allows incompatible interfaces to work together',
                'Create a wrapper class that translates one interface to another',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            ),
            DesignPattern(
                'Facade',
                'When you want to provide a simple interface to a complex subsystem',
                'Provides a unified interface to a set of interfaces in a subsystem',
                'Create a single class that wraps complex subsystem interactions',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            ),
            DesignPattern(
                'Decorator',
                'When you want to add behavior to objects dynamically without altering structure',
                'Allows behavior to be added to objects without altering their structure',
                'Create wrapper classes that add functionality while maintaining the same interface',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript']
            )
        ],
        'behavioral': [
            DesignPattern(
                'Observer',
                'When you need to notify multiple objects about state changes',
                'Defines a one-to-many dependency between objects',
                'Implement event/listener system or pub/sub pattern',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            ),
            DesignPattern(
                'Strategy',
                'When you have multiple ways to perform a task and want to choose at runtime',
                'Defines a family of algorithms and makes them interchangeable',
                'Extract algorithms into separate classes with a common interface',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            ),
            DesignPattern(
                'Command',
                'When you need to parameterize objects with operations or queue operations',
                'Encapsulates a request as an object, allowing you to parameterize and queue operations',
                'Create command objects that encapsulate actions and their parameters',
                ['python', 'java', 'csharp', 'cpp', 'javascript', 'typescript', 'go']
            )
        ]
    }
    
    # Language-specific architecture patterns
    LANGUAGE_PATTERNS = {
        'python': {
            'architecture_smells': [
                r'from\s+.*\s+import\s+\*',  # Wildcard imports
                r'global\s+\w+',             # Global variables
                r'exec\s*\(',                # Dynamic code execution
                r'eval\s*\(',                # Dynamic evaluation
                r'input\s*\(',               # Direct user input (security risk)
            ],
            'best_practices': [
                'Use type hints for better code documentation',
                'Follow PEP 8 style guide',
                'Use dataclasses for data containers',
                'Implement proper exception handling',
                'Use context managers for resource management'
            ]
        },
        'javascript': {
            'architecture_smells': [
                r'var\s+\w+',                # var usage (prefer let/const)
                r'==\s',                     # Loose equality
                r'with\s*\(',                # with statement
                r'eval\s*\(',                # Dynamic evaluation
                r'setTimeout\([^,]+,\s*0\)', # setTimeout with 0 delay
            ],
            'best_practices': [
                'Use ES6+ features (const/let, arrow functions, classes)',
                'Implement proper error handling with try/catch',
                'Use modules for code organization',
                'Follow functional programming principles',
                'Use TypeScript for large applications'
            ]
        },
        'typescript': {
            'architecture_smells': [
                r'any\s+\w+',                # any type usage
                r'@ts-ignore',               # TypeScript ignore comments
                r'as\s+any',                 # Type assertions to any
                r'Function\s*\(',            # Function type instead of specific signature
            ],
            'best_practices': [
                'Use strict TypeScript configuration',
                'Define proper interfaces and types',
                'Use generic types for reusable components',
                'Implement proper error handling',
                'Use decorators for cross-cutting concerns'
            ]
        },
        'java': {
            'architecture_smells': [
                r'public\s+static\s+void\s+main.*System\.out\.print',  # Main with System.out
                r'catch\s*\([^)]*\)\s*\{\s*\}',                        # Empty catch blocks
                r'instanceof\s+',                                      # instanceof usage
                r'System\.exit\s*\(',                                  # System.exit calls
                r'finalize\s*\(\s*\)',                                 # finalize method
            ],
            'best_practices': [
                'Use dependency injection frameworks (Spring)',
                'Follow SOLID principles',
                'Use builder pattern for complex objects',
                'Implement proper logging with SLF4J',
                'Use streams for data processing'
            ]
        },
        'csharp': {
            'architecture_smells': [
                r'public\s+static\s+',       # Excessive static usage
                r'catch\s*\([^)]*\)\s*\{\s*\}',  # Empty catch blocks
                r'throw\s+new\s+Exception\s*\(',  # Generic exception throwing
                r'Console\.Write',           # Console usage in business logic
                r'System\.GC\.Collect',      # Manual garbage collection
            ],
            'best_practices': [
                'Use dependency injection container',
                'Implement async/await for I/O operations',
                'Use LINQ for data queries',
                'Follow Microsoft coding guidelines',
                'Use proper exception handling hierarchy'
            ]
        },
        'cpp': {
            'architecture_smells': [
                r'#include\s+<iostream>.*cout', # iostream in headers
                r'using\s+namespace\s+std',      # using namespace std
                r'malloc\s*\(',                  # malloc usage (prefer new)
                r'printf\s*\(',                  # printf usage (prefer streams)
                r'#define\s+\w+\s+\d+',         # #define for constants
            ],
            'best_practices': [
                'Use RAII for resource management',
                'Prefer smart pointers over raw pointers',
                'Use const correctness',
                'Follow Rule of Three/Five/Zero',
                'Use STL algorithms and containers'
            ]
        },
        'go': {
            'architecture_smells': [
                r'panic\s*\(',               # panic usage
                r'recover\s*\(',             # recover usage
                r'goto\s+\w+',               # goto statements
                r'fmt\.Print.*\n',           # fmt.Print in production code
            ],
            'best_practices': [
                'Use interfaces for abstraction',
                'Handle errors explicitly',
                'Use context for cancellation',
                'Follow Go naming conventions',
                'Use goroutines and channels for concurrency'
            ]
        },
        'rust': {
            'architecture_smells': [
                r'unwrap\s*\(\s*\)',         # unwrap usage
                r'expect\s*\(',              # expect usage
                r'unsafe\s*\{',              # unsafe blocks
                r'panic!\s*\(',              # panic! macro
            ],
            'best_practices': [
                'Use Result and Option types properly',
                'Leverage ownership system for memory safety',
                'Use traits for shared behavior',
                'Implement proper error handling',
                'Use cargo for project management'
            ]
        }
    }
    
    def __init__(self):
        self.issues = []
        self.metrics = defaultdict(int)
        self.suggestions = []
    
    def analyze_architecture(self, file_path: str, language: str, code_content: str) -> Dict[str, Any]:
        """
        Analyze architecture for a single file
        
        Args:
            file_path: Path to the file being analyzed
            language: Programming language
            code_content: Source code content
            
        Returns:
            Architecture analysis results
        """
        logger.info(f"🏗️ Analyzing architecture for {file_path} ({language})")
        
        results = {
            'file_path': file_path,
            'language': language,
            'architecture_score': 100,
            'issues': [],
            'suggestions': [],
            'design_patterns': [],
            'metrics': {},
            'complexity_analysis': {},
            'dependency_analysis': {}
        }
        
        # Analyze code structure
        structure_issues = self._analyze_code_structure(language, code_content, file_path)
        results['issues'].extend(structure_issues)
        
        # Detect architecture smells
        smell_issues = self._detect_architecture_smells(language, code_content, file_path)
        results['issues'].extend(smell_issues)
        
        # Analyze complexity
        complexity = self._analyze_complexity(language, code_content)
        results['complexity_analysis'] = complexity
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies(language, code_content)
        results['dependency_analysis'] = dependencies
        
        # Generate design pattern recommendations
        patterns = self._recommend_design_patterns(language, code_content, results['issues'])
        results['design_patterns'] = patterns
        
        # Calculate architecture score
        results['architecture_score'] = self._calculate_architecture_score(results)
        
        # Generate improvement suggestions
        suggestions = self._generate_architecture_suggestions(language, results)
        results['suggestions'] = suggestions
        
        # Calculate metrics
        results['metrics'] = self._calculate_metrics(code_content, results)
        
        return results
    
    def analyze_project_architecture(self, project_path: str, language_files: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analyze architecture for entire project
        
        Args:
            project_path: Path to project root
            language_files: Dict mapping languages to file lists
            
        Returns:
            Project-wide architecture analysis
        """
        logger.info(f"🏗️ Analyzing project architecture at {project_path}")
        
        project_results = {
            'project_path': project_path,
            'overall_score': 0,
            'language_results': {},
            'cross_language_issues': [],
            'project_patterns': [],
            'architecture_recommendations': [],
            'dependency_graph': {},
            'hotspots': []
        }
        
        all_results = []
        
        # Analyze each language
        for language, files in language_files.items():
            language_results = []
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    file_result = self.analyze_architecture(file_path, language, content)
                    language_results.append(file_result)
                    all_results.append(file_result)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
            
            project_results['language_results'][language] = language_results
        
        # Project-wide analysis
        project_results['cross_language_issues'] = self._analyze_cross_language_issues(all_results)
        project_results['project_patterns'] = self._identify_project_patterns(all_results)
        project_results['dependency_graph'] = self._build_dependency_graph(all_results)
        project_results['hotspots'] = self._identify_architecture_hotspots(all_results)
        project_results['architecture_recommendations'] = self._generate_project_recommendations(project_results)
        
        # Calculate overall score
        if all_results:
            scores = [r['architecture_score'] for r in all_results]
            project_results['overall_score'] = sum(scores) / len(scores)
        
        return project_results
    
    def _analyze_code_structure(self, language: str, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze code structure for architecture issues"""
        issues = []
        lines = code_content.split('\n')
        
        # Common structure analysis
        class_count = 0
        function_count = 0
        long_functions = 0
        large_classes = 0
        
        # Language-specific analysis
        if language == 'python':
            issues.extend(self._analyze_python_structure(code_content, file_path))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._analyze_js_structure(code_content, file_path))
        elif language == 'java':
            issues.extend(self._analyze_java_structure(code_content, file_path))
        elif language == 'csharp':
            issues.extend(self._analyze_csharp_structure(code_content, file_path))
        elif language in ['cpp', 'c']:
            issues.extend(self._analyze_cpp_structure(code_content, file_path))
        elif language == 'go':
            issues.extend(self._analyze_go_structure(code_content, file_path))
        
        return issues
    
    def _analyze_python_structure(self, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze Python-specific structure"""
        issues = []
        
        try:
            tree = ast.parse(code_content)
            
            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check function complexity
                    if len([n for n in ast.walk(node) if isinstance(n, ast.stmt)]) > 20:
                        issues.append(ArchitectureIssue(
                            type='complex_function',
                            severity='medium',
                            description=f'Function "{node.name}" is too complex',
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion='Consider breaking down into smaller functions',
                            impact='Reduced maintainability and testability'
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    # Check class size
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 15:
                        issues.append(ArchitectureIssue(
                            type='large_class',
                            severity='medium',
                            description=f'Class "{node.name}" has too many methods ({len(methods)})',
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion='Consider splitting class responsibilities',
                            impact='Violates Single Responsibility Principle'
                        ))
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return issues
    
    def _analyze_js_structure(self, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze JavaScript/TypeScript structure"""
        issues = []
        lines = code_content.split('\n')
        
        # Check for large functions (simple heuristic)
        function_lines = 0
        in_function = False
        brace_count = 0
        function_start = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if re.match(r'(function|class|\w+\s*\([^)]*\)\s*{|\w+\s*:\s*function)', stripped):
                if not in_function:
                    in_function = True
                    function_start = i + 1
                    function_lines = 0
                    brace_count = 0
            
            if in_function:
                function_lines += 1
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count <= 0 and function_lines > 30:
                    issues.append(ArchitectureIssue(
                        type='large_function',
                        severity='medium',
                        description='Function is too large',
                        file_path=file_path,
                        line_number=function_start,
                        suggestion='Break down into smaller functions',
                        impact='Reduced readability and maintainability'
                    ))
                    in_function = False
        
        return issues
    
    def _analyze_java_structure(self, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze Java structure"""
        issues = []
        
        # Check for multiple public classes in one file
        public_classes = re.findall(r'public\s+class\s+(\w+)', code_content)
        if len(public_classes) > 1:
            issues.append(ArchitectureIssue(
                type='multiple_public_classes',
                severity='high',
                description=f'Multiple public classes found: {", ".join(public_classes)}',
                file_path=file_path,
                suggestion='Each public class should be in its own file',
                impact='Violates Java conventions and reduces code organization'
            ))
        
        # Check for large methods
        methods = re.finditer(r'(public|private|protected).*?\{', code_content, re.DOTALL)
        for method in methods:
            # Simple heuristic: count lines between braces
            start_pos = method.end()
            brace_count = 1
            lines = 1
            
            for i, char in enumerate(code_content[start_pos:], start_pos):
                if char == '\n':
                    lines += 1
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        if lines > 30:
                            line_num = code_content[:method.start()].count('\n') + 1
                            issues.append(ArchitectureIssue(
                                type='large_method',
                                severity='medium',
                                description=f'Method is too large ({lines} lines)',
                                file_path=file_path,
                                line_number=line_num,
                                suggestion='Break down method into smaller ones',
                                impact='Reduced maintainability and testability'
                            ))
                        break
        
        return issues
    
    def _analyze_csharp_structure(self, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze C# structure"""
        issues = []
        
        # Check for large classes
        class_matches = re.finditer(r'(public|internal)\s+class\s+(\w+)', code_content)
        for match in class_matches:
            class_name = match.group(2)
            # Count methods in class (simplified)
            class_start = match.start()
            brace_count = 0
            method_count = 0
            
            for i, char in enumerate(code_content[class_start:], class_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Count methods in this section
                        class_section = code_content[class_start:i+1]
                        method_count = len(re.findall(r'(public|private|protected).*?\w+\s*\([^)]*\)', class_section))
                        
                        if method_count > 15:
                            line_num = code_content[:class_start].count('\n') + 1
                            issues.append(ArchitectureIssue(
                                type='large_class',
                                severity='medium',
                                description=f'Class "{class_name}" has too many methods ({method_count})',
                                file_path=file_path,
                                line_number=line_num,
                                suggestion='Consider splitting class responsibilities',
                                impact='Violates Single Responsibility Principle'
                            ))
                        break
        
        return issues
    
    def _analyze_cpp_structure(self, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze C/C++ structure"""
        issues = []
        
        # Check for header guard issues
        if file_path.endswith(('.h', '.hpp')):
            if not re.search(r'#ifndef\s+\w+|#pragma\s+once', code_content):
                issues.append(ArchitectureIssue(
                    type='missing_header_guard',
                    severity='high',
                    description='Header file missing include guard',
                    file_path=file_path,
                    suggestion='Add #pragma once or #ifndef guard',
                    impact='May cause multiple inclusion problems'
                ))
        
        # Check for large functions
        function_matches = re.finditer(r'\w+\s+\w+\s*\([^)]*\)\s*\{', code_content)
        for match in function_matches:
            start_pos = match.end() - 1  # Position of opening brace
            brace_count = 1
            lines = 1
            
            for i, char in enumerate(code_content[start_pos + 1:], start_pos + 1):
                if char == '\n':
                    lines += 1
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        if lines > 50:
                            line_num = code_content[:match.start()].count('\n') + 1
                            issues.append(ArchitectureIssue(
                                type='large_function',
                                severity='medium',
                                description=f'Function is too large ({lines} lines)',
                                file_path=file_path,
                                line_number=line_num,
                                suggestion='Break down function into smaller ones',
                                impact='Reduced readability and maintainability'
                            ))
                        break
        
        return issues
    
    def _analyze_go_structure(self, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Analyze Go structure"""
        issues = []
        
        # Check for large functions
        func_matches = re.finditer(r'func\s+(\w+)?\s*\([^)]*\).*?\{', code_content)
        for match in func_matches:
            start_pos = match.end() - 1  # Position of opening brace
            brace_count = 1
            lines = 1
            
            for i, char in enumerate(code_content[start_pos + 1:], start_pos + 1):
                if char == '\n':
                    lines += 1
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        if lines > 40:
                            line_num = code_content[:match.start()].count('\n') + 1
                            issues.append(ArchitectureIssue(
                                type='large_function',
                                severity='medium',
                                description=f'Function is too large ({lines} lines)',
                                file_path=file_path,
                                line_number=line_num,
                                suggestion='Break down function into smaller ones',
                                impact='Reduced readability and maintainability'
                            ))
                        break
        
        return issues
    
    def _detect_architecture_smells(self, language: str, code_content: str, file_path: str) -> List[ArchitectureIssue]:
        """Detect language-specific architecture smells"""
        issues = []
        
        if language not in self.LANGUAGE_PATTERNS:
            return issues
        
        patterns = self.LANGUAGE_PATTERNS[language]['architecture_smells']
        lines = code_content.split('\n')
        
        pattern_descriptions = {
            r'from\s+.*\s+import\s+\*': 'Wildcard import detected',
            r'global\s+\w+': 'Global variable usage',
            r'var\s+\w+': 'Use of var instead of let/const',
            r'==\s': 'Loose equality comparison',
            r'any\s+\w+': 'Use of any type',
            r'instanceof\s+': 'instanceof usage detected',
            r'using\s+namespace\s+std': 'Using namespace std in header',
            r'panic\s*\(': 'Panic usage detected',
        }
        
        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.MULTILINE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                description = pattern_descriptions.get(pattern, 'Architecture smell detected')
                
                issues.append(ArchitectureIssue(
                    type='architecture_smell',
                    severity='medium',
                    description=description,
                    file_path=file_path,
                    line_number=line_num,
                    suggestion=self._get_smell_suggestion(pattern, language),
                    impact='May indicate poor design choices'
                ))
        
        return issues
    
    def _analyze_complexity(self, language: str, code_content: str) -> Dict[str, Any]:
        """Analyze code complexity"""
        lines = code_content.split('\n')
        
        complexity = {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '\'\'\'', '"""'))]),
            'comment_lines': len([l for l in lines if l.strip().startswith(('#', '//', '/*'))]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(code_content),
            'nesting_depth': self._calculate_nesting_depth(code_content),
            'function_count': self._count_functions(language, code_content),
            'class_count': self._count_classes(language, code_content)
        }
        
        return complexity
    
    def _analyze_dependencies(self, language: str, code_content: str) -> Dict[str, Any]:
        """Analyze code dependencies"""
        dependencies = {
            'imports': [],
            'external_dependencies': [],
            'internal_dependencies': [],
            'circular_dependencies': [],
            'dependency_count': 0
        }
        
        # Extract imports/includes based on language
        import_patterns = {
            'python': [r'import\s+([^\s,]+)', r'from\s+([^\s]+)\s+import'],
            'javascript': [r'import.*from\s+[\'"]([^\'"]+)[\'"]', r'require\s*\(\s*[\'"]([^\'"]+)[\'"]'],
            'typescript': [r'import.*from\s+[\'"]([^\'"]+)[\'"]', r'import\s+[\'"]([^\'"]+)[\'"]'],
            'java': [r'import\s+([^\s;]+)'],
            'csharp': [r'using\s+([^\s;]+)'],
            'cpp': [r'#include\s+[<"]([^>"]+)[>"]'],
            'go': [r'import\s+["]([^"]+)["]']
        }
        
        if language in import_patterns:
            for pattern in import_patterns[language]:
                matches = re.findall(pattern, code_content)
                dependencies['imports'].extend(matches)
        
        dependencies['dependency_count'] = len(dependencies['imports'])
        
        # Classify dependencies as external vs internal
        for dep in dependencies['imports']:
            if self._is_external_dependency(dep, language):
                dependencies['external_dependencies'].append(dep)
            else:
                dependencies['internal_dependencies'].append(dep)
        
        return dependencies
    
    def _recommend_design_patterns(self, language: str, code_content: str, issues: List[ArchitectureIssue]) -> List[Dict[str, Any]]:
        """Recommend design patterns based on code analysis"""
        recommendations = []
        
        # Analyze code patterns and suggest appropriate design patterns
        for category, patterns in self.DESIGN_PATTERNS.items():
            for pattern in patterns:
                if language in pattern.languages:
                    applicability_score = self._assess_pattern_applicability(pattern, code_content, issues)
                    
                    if applicability_score > 0.3:
                        recommendations.append({
                            'pattern': pattern.pattern_name,
                            'category': category,
                            'applicability': pattern.applicability,
                            'benefit': pattern.benefit,
                            'implementation_hint': pattern.implementation_hint,
                            'score': applicability_score,
                            'reason': self._get_pattern_recommendation_reason(pattern, code_content, issues)
                        })
        
        # Sort by applicability score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]  # Return top 5 recommendations
    
    def _calculate_architecture_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall architecture score"""
        base_score = 100
        
        # Deduct points for issues
        for issue in results['issues']:
            if issue.severity == 'high':
                base_score -= 15
            elif issue.severity == 'medium':
                base_score -= 8
            else:
                base_score -= 3
        
        # Deduct points for high complexity
        complexity = results['complexity_analysis']
        if complexity.get('cyclomatic_complexity', 0) > 15:
            base_score -= 10
        if complexity.get('nesting_depth', 0) > 5:
            base_score -= 8
        
        # Deduct points for too many dependencies
        dep_count = results['dependency_analysis'].get('dependency_count', 0)
        if dep_count > 20:
            base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _generate_architecture_suggestions(self, language: str, results: Dict[str, Any]) -> List[str]:
        """Generate architecture improvement suggestions"""
        suggestions = []
        
        # General suggestions based on score
        score = results['architecture_score']
        if score < 60:
            suggestions.append("🚨 Critical architecture issues detected - immediate refactoring recommended")
            suggestions.append("📊 Consider conducting a thorough architecture review")
        elif score < 80:
            suggestions.append("⚠️ Moderate architecture issues - gradual improvement recommended")
        
        # Language-specific suggestions
        if language in self.LANGUAGE_PATTERNS:
            best_practices = self.LANGUAGE_PATTERNS[language]['best_practices']
            suggestions.extend([f"📋 {practice}" for practice in best_practices[:3]])
        
        # Issue-specific suggestions
        issue_types = [issue.type for issue in results['issues']]
        if 'large_function' in issue_types or 'large_class' in issue_types:
            suggestions.append("🔧 Refactor large functions/classes using Extract Method/Class pattern")
        
        if 'complex_function' in issue_types:
            suggestions.append("🧩 Reduce cyclomatic complexity by extracting conditional logic")
        
        if 'architecture_smell' in issue_types:
            suggestions.append("🧼 Address code smells to improve maintainability")
        
        # Pattern-based suggestions
        if results['design_patterns']:
            top_pattern = results['design_patterns'][0]
            suggestions.append(f"🎯 Consider implementing {top_pattern['pattern']} pattern: {top_pattern['benefit']}")
        
        return suggestions
    
    # Helper methods
    def _calculate_cyclomatic_complexity(self, code_content: str) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        # Count decision points
        decision_keywords = ['if', 'elif', 'else if', 'while', 'for', 'case', 'catch', 'and', 'or', '&&', '||']
        complexity = 1  # Base complexity
        
        for keyword in decision_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', code_content, re.IGNORECASE))
        
        return complexity
    
    def _calculate_nesting_depth(self, code_content: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in code_content:
            if char in '{([':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '})]':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _count_functions(self, language: str, code_content: str) -> int:
        """Count functions in code"""
        patterns = {
            'python': r'def\s+\w+',
            'javascript': r'function\s+\w+',
            'typescript': r'function\s+\w+',
            'java': r'(public|private|protected).*?\s+\w+\s*\([^)]*\)',
            'csharp': r'(public|private|protected).*?\s+\w+\s*\([^)]*\)',
            'cpp': r'\w+\s+\w+\s*\([^)]*\)\s*\{',
            'go': r'func\s+\w+'
        }
        
        pattern = patterns.get(language, r'function\s+\w+')
        return len(re.findall(pattern, code_content))
    
    def _count_classes(self, language: str, code_content: str) -> int:
        """Count classes in code"""
        patterns = {
            'python': r'class\s+\w+',
            'javascript': r'class\s+\w+',
            'typescript': r'class\s+\w+',
            'java': r'(public|private)\s+class\s+\w+',
            'csharp': r'(public|internal)\s+class\s+\w+',
            'cpp': r'class\s+\w+',
        }
        
        pattern = patterns.get(language, r'class\s+\w+')
        return len(re.findall(pattern, code_content))
    
    def _is_external_dependency(self, dep: str, language: str) -> bool:
        """Check if dependency is external (simplified heuristic)"""
        # Language-specific standard libraries and frameworks
        internal_prefixes = {
            'python': ['os', 'sys', 'json', 'http', 'urllib', 'collections', 'itertools'],
            'javascript': ['fs', 'path', 'http', 'https', 'crypto', 'util'],
            'java': ['java.', 'javax.', 'com.sun.'],
            'csharp': ['System.', 'Microsoft.'],
            'go': ['fmt', 'os', 'net', 'encoding', 'database']
        }
        
        prefixes = internal_prefixes.get(language, [])
        return not any(dep.startswith(prefix) for prefix in prefixes)
    
    def _assess_pattern_applicability(self, pattern: DesignPattern, code_content: str, issues: List[ArchitectureIssue]) -> float:
        """Assess how applicable a design pattern is to the code"""
        score = 0.0
        
        # Pattern-specific heuristics
        if pattern.pattern_name == 'Factory Method':
            # Look for object creation patterns
            if re.search(r'new\s+\w+\s*\(', code_content):
                score += 0.3
            if any('large_class' in issue.type for issue in issues):
                score += 0.2
        
        elif pattern.pattern_name == 'Singleton':
            # Look for global state patterns
            if re.search(r'global\s+\w+|static\s+\w+.*=', code_content):
                score += 0.4
        
        elif pattern.pattern_name == 'Observer':
            # Look for event/callback patterns
            if re.search(r'(addEventListener|on\w+|callback|notify)', code_content):
                score += 0.5
        
        elif pattern.pattern_name == 'Strategy':
            # Look for conditional complexity
            if re.search(r'if.*elif.*else|switch.*case', code_content, re.DOTALL):
                score += 0.3
        
        return min(1.0, score)
    
    def _get_pattern_recommendation_reason(self, pattern: DesignPattern, code_content: str, issues: List[ArchitectureIssue]) -> str:
        """Get reason for pattern recommendation"""
        reasons = {
            'Factory Method': 'Multiple object instantiations detected',
            'Singleton': 'Global state usage found',
            'Observer': 'Event handling patterns detected',
            'Strategy': 'Complex conditional logic found'
        }
        
        return reasons.get(pattern.pattern_name, 'Pattern may improve code structure')
    
    def _get_smell_suggestion(self, pattern: str, language: str) -> str:
        """Get suggestion for fixing architecture smell"""
        suggestions = {
            r'from\s+.*\s+import\s+\*': 'Use explicit imports instead of wildcard imports',
            r'var\s+\w+': 'Use let or const instead of var',
            r'==\s': 'Use strict equality (===) instead of loose equality (==)',
            r'any\s+\w+': 'Use specific types instead of any',
            r'using\s+namespace\s+std': 'Avoid using namespace std in headers'
        }
        
        return suggestions.get(pattern, 'Consider refactoring this pattern')
    
    def _analyze_cross_language_issues(self, all_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze issues that span multiple languages"""
        cross_issues = []
        
        # Example: Inconsistent naming conventions across languages
        naming_patterns = defaultdict(set)
        for result in all_results:
            lang = result['language']
            # Extract naming patterns (simplified)
            if lang == 'python':
                pattern = 'snake_case'
            elif lang in ['javascript', 'typescript']:
                pattern = 'camelCase'
            elif lang in ['java', 'csharp']:
                pattern = 'PascalCase'
            else:
                pattern = 'unknown'
            
            naming_patterns[pattern].add(lang)
        
        if len(naming_patterns) > 2:
            cross_issues.append({
                'type': 'inconsistent_naming',
                'severity': 'medium',
                'description': 'Inconsistent naming conventions across languages',
                'languages': list(naming_patterns.keys()),
                'suggestion': 'Establish consistent naming conventions'
            })
        
        return cross_issues
    
    def _identify_project_patterns(self, all_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify architectural patterns used across the project"""
        patterns = []
        
        # Count pattern recommendations across files
        pattern_counts = Counter()
        for result in all_results:
            for pattern in result.get('design_patterns', []):
                pattern_counts[pattern['pattern']] += 1
        
        # Identify commonly recommended patterns
        for pattern, count in pattern_counts.most_common(5):
            if count >= 2:  # Pattern recommended for multiple files
                patterns.append({
                    'pattern': pattern,
                    'frequency': count,
                    'recommendation': f'Consider implementing {pattern} pattern across {count} files'
                })
        
        return patterns
    
    def _build_dependency_graph(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build project dependency graph"""
        graph = {
            'nodes': [],
            'edges': [],
            'external_deps': set(),
            'internal_deps': set()
        }
        
        for result in all_results:
            file_path = result['file_path']
            deps = result.get('dependency_analysis', {})
            
            graph['nodes'].append(file_path)
            graph['external_deps'].update(deps.get('external_dependencies', []))
            graph['internal_deps'].update(deps.get('internal_dependencies', []))
        
        return {
            'total_files': len(graph['nodes']),
            'external_dependencies': len(graph['external_deps']),
            'internal_dependencies': len(graph['internal_deps']),
            'external_deps_list': list(graph['external_deps'])[:10]  # Top 10
        }
    
    def _identify_architecture_hotspots(self, all_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify architectural hotspots that need attention"""
        hotspots = []
        
        # Files with low architecture scores
        low_score_files = [r for r in all_results if r['architecture_score'] < 60]
        if low_score_files:
            hotspots.append({
                'type': 'low_quality_files',
                'count': len(low_score_files),
                'files': [r['file_path'] for r in low_score_files[:5]],
                'priority': 'high',
                'description': f'{len(low_score_files)} files with architecture scores below 60'
            })
        
        # Files with many issues
        high_issue_files = [r for r in all_results if len(r.get('issues', [])) > 10]
        if high_issue_files:
            hotspots.append({
                'type': 'high_issue_files',
                'count': len(high_issue_files),
                'files': [r['file_path'] for r in high_issue_files[:5]],
                'priority': 'medium',
                'description': f'{len(high_issue_files)} files with more than 10 architecture issues'
            })
        
        return hotspots
    
    def _generate_project_recommendations(self, project_results: Dict[str, Any]) -> List[str]:
        """Generate project-wide architecture recommendations"""
        recommendations = []
        
        overall_score = project_results['overall_score']
        
        if overall_score < 60:
            recommendations.append("🚨 Project requires comprehensive architecture refactoring")
            recommendations.append("📋 Create architecture improvement roadmap")
            recommendations.append("👥 Consider bringing in architecture expertise")
        elif overall_score < 80:
            recommendations.append("⚠️ Project has moderate architecture issues")
            recommendations.append("🔄 Implement gradual refactoring strategy")
        
        # Hotspot-based recommendations
        hotspots = project_results.get('hotspots', [])
        if hotspots:
            recommendations.append(f"🎯 Focus on {len(hotspots)} architecture hotspots first")
        
        # Cross-language recommendations
        cross_issues = project_results.get('cross_language_issues', [])
        if cross_issues:
            recommendations.append("🌐 Address cross-language consistency issues")
        
        # Pattern-based recommendations
        project_patterns = project_results.get('project_patterns', [])
        if project_patterns:
            top_pattern = project_patterns[0]
            recommendations.append(f"🎨 Consider project-wide adoption of {top_pattern['pattern']} pattern")
        
        return recommendations
    
    def _calculate_metrics(self, code_content: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various architecture metrics"""
        return {
            'maintainability_index': self._calculate_maintainability_index(results),
            'technical_debt_ratio': self._calculate_technical_debt_ratio(results),
            'code_coverage_estimate': self._estimate_testability(code_content),
            'refactoring_priority': self._assess_refactoring_priority(results)
        }
    
    def _calculate_maintainability_index(self, results: Dict[str, Any]) -> float:
        """Calculate maintainability index (0-100)"""
        base_score = 100.0
        
        # Reduce score based on issues
        issue_penalty = len(results.get('issues', [])) * 2
        complexity_penalty = results.get('complexity_analysis', {}).get('cyclomatic_complexity', 0) * 0.5
        
        return max(0, base_score - issue_penalty - complexity_penalty)
    
    def _calculate_technical_debt_ratio(self, results: Dict[str, Any]) -> float:
        """Calculate technical debt ratio"""
        total_issues = len(results.get('issues', []))
        high_severity = len([i for i in results.get('issues', []) if i.severity == 'high'])
        
        if total_issues == 0:
            return 0.0
        
        return (high_severity * 2 + total_issues) / 100.0
    
    def _estimate_testability(self, code_content: str) -> float:
        """Estimate how testable the code is"""
        lines = len(code_content.split('\n'))
        test_indicators = len(re.findall(r'(test|spec|mock|stub)', code_content, re.IGNORECASE))
        
        return min(100.0, (test_indicators / max(lines / 100, 1)) * 100)
    
    def _assess_refactoring_priority(self, results: Dict[str, Any]) -> str:
        """Assess refactoring priority"""
        score = results['architecture_score']
        
        if score < 50:
            return 'CRITICAL'
        elif score < 70:
            return 'HIGH'
        elif score < 85:
            return 'MEDIUM'
        else:
            return 'LOW'


def analyze_architecture(file_path: str, language: str, code_content: str) -> Dict[str, Any]:
    """
    Analyze architecture for a single file
    
    Args:
        file_path: Path to the file
        language: Programming language
        code_content: Source code content
        
    Returns:
        Architecture analysis results
    """
    analyzer = ArchitectureAnalyzer()
    return analyzer.analyze_architecture(file_path, language, code_content)


def analyze_project_architecture(project_path: str, language_files: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Analyze architecture for entire project
    
    Args:
        project_path: Path to project root
        language_files: Dict mapping languages to file lists
        
    Returns:
        Project-wide architecture analysis
    """
    analyzer = ArchitectureAnalyzer()
    return analyzer.analyze_project_architecture(project_path, language_files)