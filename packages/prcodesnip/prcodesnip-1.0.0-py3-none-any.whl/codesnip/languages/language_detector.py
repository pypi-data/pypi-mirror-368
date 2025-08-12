"""
Multi-language repository detection and configuration
"""
import os
import requests
import logging
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import json
import re

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Detects programming languages used in a repository"""
    
    # Language patterns and their associated file extensions - COMPREHENSIVE SUPPORT
    LANGUAGE_PATTERNS = {
        # ===== MAINSTREAM LANGUAGES =====
        'python': {
            'extensions': ['.py', '.pyw', '.pyi', '.py3'],
            'files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock', 'conda.yml', 'environment.yml'],
            'directories': ['__pycache__', '.pytest_cache', 'venv', 'env', '.venv'],
            'tools': ['pytest', 'pylint', 'black', 'flake8', 'mypy', 'bandit', 'coverage', 'isort', 'autopep8', 'safety'],
            'frameworks': ['django', 'flask', 'fastapi', 'tornado', 'pyramid', 'bottle', 'cherrypy', 'falcon'],
            'package_managers': ['pip', 'poetry', 'pipenv', 'conda', 'pdm']
        },
        'javascript': {
            'extensions': ['.js', '.mjs', '.jsx', '.es6', '.es'],
            'files': ['package.json', 'package-lock.json', 'yarn.lock', '.babelrc', 'webpack.config.js', '.eslintrc', 'rollup.config.js'],
            'directories': ['node_modules', 'dist', 'build', '.next'],
            'tools': ['eslint', 'prettier', 'jest', 'mocha', 'webpack', 'babel', 'jshint', 'flow'],
            'frameworks': ['react', 'vue', 'angular', 'express', 'next.js', 'nuxt.js', 'svelte', 'ember'],
            'package_managers': ['npm', 'yarn', 'pnpm', 'bun']
        },
        'typescript': {
            'extensions': ['.ts', '.tsx', '.d.ts', '.mts', '.cts'],
            'files': ['tsconfig.json', 'tslint.json', 'tsconfig.build.json'],
            'directories': ['dist', 'build', 'lib'],
            'tools': ['tsc', 'tslint', 'eslint', 'prettier', 'jest', 'ts-node', 'ts-jest'],
            'frameworks': ['angular', 'react', 'vue', 'nestjs', 'deno'],
            'package_managers': ['npm', 'yarn', 'pnpm', 'deno']
        },
        'go': {
            'extensions': ['.go'],
            'files': ['go.mod', 'go.sum', 'Gopkg.toml', 'Gopkg.lock', 'glide.yaml'],
            'directories': ['vendor', 'bin'],
            'tools': ['go', 'gofmt', 'golint', 'go vet', 'golangci-lint', 'goimports', 'staticcheck', 'gosec', 'ineffassign'],
            'frameworks': ['gin', 'echo', 'fiber', 'gorilla/mux', 'beego', 'revel', 'iris'],
            'package_managers': ['go mod', 'dep', 'glide', 'govendor']
        },
        'java': {
            'extensions': ['.java', '.class', '.jar', '.war', '.ear'],
            'files': ['pom.xml', 'build.gradle', 'gradle.properties', 'build.xml', 'settings.gradle'],
            'directories': ['target', 'build', 'out', 'classes', '.gradle'],
            'tools': ['maven', 'gradle', 'ant', 'checkstyle', 'spotbugs', 'pmd', 'junit', 'jacoco', 'sonar'],
            'frameworks': ['spring', 'hibernate', 'junit', 'mockito', 'struts', 'jsf', 'wicket'],
            'package_managers': ['maven', 'gradle', 'ant', 'sbt']
        },
        'csharp': {
            'extensions': ['.cs', '.csx', '.csproj', '.sln', '.vb', '.fs'],
            'files': ['*.csproj', '*.sln', 'packages.config', 'nuget.config', 'global.json'],
            'directories': ['bin', 'obj', 'packages', 'TestResults'],
            'tools': ['dotnet', 'msbuild', 'nuget', 'stylecopanalyzers', 'sonaranalyzer', 'resharper'],
            'frameworks': ['.net', 'asp.net', 'entity framework', 'xamarin', 'blazor', 'maui'],
            'package_managers': ['nuget', 'paket', 'dotnet']
        },
        'rust': {
            'extensions': ['.rs', '.rlib'],
            'files': ['Cargo.toml', 'Cargo.lock', 'rust-toolchain', 'rust-toolchain.toml'],
            'directories': ['target', 'src'],
            'tools': ['cargo', 'rustc', 'clippy', 'rustfmt', 'rust-analyzer', 'miri', 'rustdoc'],
            'frameworks': ['tokio', 'actix-web', 'rocket', 'serde', 'diesel', 'warp', 'axum'],
            'package_managers': ['cargo']
        },
        'cpp': {
            'extensions': ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hh', '.hxx', '.h++', '.h'],
            'files': ['CMakeLists.txt', 'Makefile', 'configure.ac', 'meson.build', 'conanfile.txt', 'vcpkg.json'],
            'directories': ['build', 'cmake-build-debug', 'cmake-build-release', 'out'],
            'tools': ['cmake', 'make', 'g++', 'clang++', 'valgrind', 'gdb', 'cppcheck', 'clang-tidy', 'sanitizers'],
            'frameworks': ['boost', 'qt', 'opencv', 'eigen', 'poco', 'catch2', 'gtest'],
            'package_managers': ['vcpkg', 'conan', 'hunter', 'cpm']
        },
        'c': {
            'extensions': ['.c', '.h'],
            'files': ['Makefile', 'configure.ac', 'CMakeLists.txt', 'meson.build'],
            'directories': ['build', 'obj', 'bin'],
            'tools': ['gcc', 'clang', 'make', 'cmake', 'valgrind', 'gdb', 'cppcheck', 'splint'],
            'frameworks': ['glib', 'gtk', 'sdl', 'curl', 'openssl'],
            'package_managers': ['pkg-config', 'vcpkg', 'conan']
        },
        'php': {
            'extensions': ['.php', '.phtml', '.php3', '.php4', '.php5', '.php7', '.php8', '.phar'],
            'files': ['composer.json', 'composer.lock', 'phpunit.xml', 'phpcs.xml', 'psalm.xml'],
            'directories': ['vendor', 'storage', 'cache'],
            'tools': ['composer', 'phpunit', 'phpcs', 'phpstan', 'psalm', 'rector', 'php-cs-fixer'],
            'frameworks': ['laravel', 'symfony', 'codeigniter', 'yii', 'cakephp', 'zend', 'phalcon'],
            'package_managers': ['composer', 'pear', 'pecl']
        },
        'ruby': {
            'extensions': ['.rb', '.rbw', '.rake', '.gemspec'],
            'files': ['Gemfile', 'Gemfile.lock', 'Rakefile', '*.gemspec', '.ruby-version'],
            'directories': ['vendor', '.bundle', 'tmp', 'log'],
            'tools': ['bundle', 'rake', 'rspec', 'rubocop', 'yard', 'brakeman', 'reek'],
            'frameworks': ['rails', 'sinatra', 'rspec', 'minitest', 'hanami', 'dry-rb'],
            'package_managers': ['gem', 'bundler', 'rvm', 'rbenv']
        },
        'swift': {
            'extensions': ['.swift'],
            'files': ['Package.swift', '*.xcodeproj', '*.xcworkspace', 'Podfile', 'Cartfile'],
            'directories': ['.build', 'Pods', 'DerivedData', 'Carthage'],
            'tools': ['swift', 'xcodebuild', 'swiftlint', 'swiftformat', 'sourcery'],
            'frameworks': ['swiftui', 'uikit', 'foundation', 'combine', 'vapor', 'perfect'],
            'package_managers': ['swift package manager', 'cocoapods', 'carthage', 'mint']
        },
        'kotlin': {
            'extensions': ['.kt', '.kts'],
            'files': ['build.gradle.kts', 'settings.gradle.kts', 'build.gradle'],
            'directories': ['build', 'out', '.gradle'],
            'tools': ['gradle', 'maven', 'ktlint', 'detekt', 'kotlinc'],
            'frameworks': ['spring boot', 'ktor', 'android', 'compose', 'exposed'],
            'package_managers': ['gradle', 'maven']
        },
        'scala': {
            'extensions': ['.scala', '.sc', '.sbt'],
            'files': ['build.sbt', 'project/build.properties', 'project/plugins.sbt'],
            'directories': ['target', 'project/target', '.metals'],
            'tools': ['sbt', 'scalac', 'scalafmt', 'scalatest', 'wartremover', 'scalafix'],
            'frameworks': ['akka', 'play', 'spark', 'cats', 'zio', 'http4s'],
            'package_managers': ['sbt', 'maven', 'mill']
        },
        
        # ===== FUNCTIONAL LANGUAGES =====
        'haskell': {
            'extensions': ['.hs', '.lhs', '.cabal'],
            'files': ['*.cabal', 'package.yaml', 'stack.yaml', 'cabal.project'],
            'directories': ['dist', '.stack-work', 'dist-newstyle'],
            'tools': ['ghc', 'cabal', 'stack', 'hlint', 'haddock', 'ghcid'],
            'frameworks': ['yesod', 'snap', 'servant', 'scotty'],
            'package_managers': ['cabal', 'stack', 'nix']
        },
        'ocaml': {
            'extensions': ['.ml', '.mli', '.mll', '.mly'],
            'files': ['dune-project', 'opam', 'Makefile.config.in'],
            'directories': ['_build', '_opam'],
            'tools': ['ocamlc', 'ocamlopt', 'dune', 'ocamlfind', 'merlin'],
            'frameworks': ['lwt', 'async', 'core', 'jane-street'],
            'package_managers': ['opam', 'dune', 'esy']
        },
        'erlang': {
            'extensions': ['.erl', '.hrl', '.xrl', '.yrl'],
            'files': ['rebar.config', 'relx.config', 'sys.config'],
            'directories': ['ebin', '_build', 'deps'],
            'tools': ['erlc', 'rebar3', 'dialyzer', 'xref'],
            'frameworks': ['cowboy', 'phoenix', 'gen_server'],
            'package_managers': ['rebar3', 'hex']
        },
        'elixir': {
            'extensions': ['.ex', '.exs', '.eex', '.heex'],
            'files': ['mix.exs', 'mix.lock', 'config.exs'],
            'directories': ['deps', '_build', 'priv'],
            'tools': ['mix', 'elixir', 'iex', 'credo', 'dialyxir', 'excoveralls'],
            'frameworks': ['phoenix', 'plug', 'ecto', 'genserver'],
            'package_managers': ['hex', 'mix']
        },
        'fsharp': {
            'extensions': ['.fs', '.fsi', '.fsx', '.fsscript'],
            'files': ['*.fsproj', 'paket.dependencies', 'packages.config'],
            'directories': ['bin', 'obj', 'packages'],
            'tools': ['dotnet', 'fsc', 'fsi', 'paket', 'fake'],
            'frameworks': ['.net', 'fable', 'saturn', 'giraffe'],
            'package_managers': ['dotnet', 'paket', 'nuget']
        },
        'clojure': {
            'extensions': ['.clj', '.cljs', '.cljc', '.edn'],
            'files': ['project.clj', 'deps.edn', 'shadow-cljs.edn'],
            'directories': ['target', '.cpcache', 'resources'],
            'tools': ['lein', 'clj', 'clojure', 'eastwood', 'kibit'],
            'frameworks': ['ring', 'compojure', 'luminus', 're-frame'],
            'package_managers': ['leiningen', 'deps.edn', 'boot']
        },
        
        # ===== JVM LANGUAGES =====
        'groovy': {
            'extensions': ['.groovy', '.gvy', '.gy', '.gsh'],
            'files': ['build.gradle', 'gradle.properties'],
            'directories': ['build', '.gradle', 'target'],
            'tools': ['groovyc', 'gradle', 'groovydoc', 'codenarc'],
            'frameworks': ['grails', 'spring boot', 'spock'],
            'package_managers': ['gradle', 'grape', 'maven']
        },
        'jython': {
            'extensions': ['.py'],
            'files': ['setup.py', 'build.xml'],
            'directories': ['build', 'dist'],
            'tools': ['jython', 'ant', 'maven'],
            'frameworks': ['django-jython', 'modjy'],
            'package_managers': ['pip', 'easy_install']
        },
        
        # ===== .NET ECOSYSTEM =====
        'vbnet': {
            'extensions': ['.vb', '.vbproj'],
            'files': ['*.vbproj', '*.sln', 'packages.config'],
            'directories': ['bin', 'obj', 'My Project'],
            'tools': ['vbc', 'msbuild', 'dotnet'],
            'frameworks': ['.net framework', '.net core', 'asp.net'],
            'package_managers': ['nuget', 'dotnet']
        },
        'powershell': {
            'extensions': ['.ps1', '.psm1', '.psd1'],
            'files': ['*.psd1', 'requirements.psd1'],
            'directories': ['Modules', 'Scripts'],
            'tools': ['pwsh', 'powershell', 'pester', 'psscriptanalyzer'],
            'frameworks': ['dsc', 'azure powershell', 'exchange'],
            'package_managers': ['powershellget', 'chocolatey']
        },
        
        # ===== SYSTEMS PROGRAMMING =====
        'assembly': {
            'extensions': ['.asm', '.s', '.S'],
            'files': ['Makefile', 'CMakeLists.txt'],
            'directories': ['obj', 'bin'],
            'tools': ['nasm', 'gas', 'masm', 'yasm'],
            'frameworks': ['kernel', 'embedded'],
            'package_managers': ['make', 'cmake']
        },
        'zig': {
            'extensions': ['.zig'],
            'files': ['build.zig', 'build.zig.zon'],
            'directories': ['zig-cache', 'zig-out'],
            'tools': ['zig'],
            'frameworks': ['std', 'raylib-zig'],
            'package_managers': ['zig']
        },
        
        # ===== WEB LANGUAGES =====
        'html': {
            'extensions': ['.html', '.htm', '.xhtml', '.shtml'],
            'files': ['index.html', 'package.json'],
            'directories': ['assets', 'css', 'js', 'images'],
            'tools': ['htmlhint', 'tidy', 'prettier', 'html-validate'],
            'frameworks': ['bootstrap', 'foundation', 'bulma'],
            'package_managers': ['npm', 'bower']
        },
        'css': {
            'extensions': ['.css', '.scss', '.sass', '.less', '.styl'],
            'files': ['style.css', 'main.scss', 'package.json'],
            'directories': ['css', 'sass', 'styles', 'assets'],
            'tools': ['stylelint', 'sass', 'less', 'postcss', 'autoprefixer'],
            'frameworks': ['bootstrap', 'tailwind', 'foundation', 'bulma'],
            'package_managers': ['npm', 'yarn', 'bower']
        },
        
        # ===== DATABASE LANGUAGES =====
        'sql': {
            'extensions': ['.sql', '.ddl', '.dml'],
            'files': ['schema.sql', 'migrations.sql', '*.sql'],
            'directories': ['migrations', 'seeds', 'schema'],
            'tools': ['sqlfluff', 'sqlfmt', 'sqlcheck'],
            'frameworks': ['postgresql', 'mysql', 'sqlite', 'oracle'],
            'package_managers': ['migrations', 'flyway', 'liquibase']
        },
        'plsql': {
            'extensions': ['.pls', '.plb', '.pck', '.pkb'],
            'files': ['*.pks', '*.pkb'],
            'directories': ['packages', 'procedures', 'functions'],
            'tools': ['sqlplus', 'plsql developer', 'toad'],
            'frameworks': ['oracle apex', 'oracle forms'],
            'package_managers': ['oracle']
        },
        
        # ===== SCIENTIFIC COMPUTING =====
        'r': {
            'extensions': ['.r', '.R', '.Rmd', '.Rnw'],
            'files': ['DESCRIPTION', 'NAMESPACE', '.Rprofile'],
            'directories': ['R', 'man', 'data', 'vignettes'],
            'tools': ['Rscript', 'devtools', 'roxygen2', 'testthat', 'lintr'],
            'frameworks': ['shiny', 'ggplot2', 'dplyr', 'tidyr'],
            'package_managers': ['cran', 'bioconductor', 'devtools']
        },
        'matlab': {
            'extensions': ['.m', '.mlx', '.mat', '.fig'],
            'files': ['Contents.m', 'license.txt'],
            'directories': ['+packages', 'private', 'resources'],
            'tools': ['matlab', 'mcc', 'mlint'],
            'frameworks': ['simulink', 'app designer', 'deep learning'],
            'package_managers': ['add-on explorer', 'file exchange']
        },
        'julia': {
            'extensions': ['.jl'],
            'files': ['Project.toml', 'Manifest.toml', 'Pkg.toml'],
            'directories': ['src', 'test', 'docs', 'deps'],
            'tools': ['julia', 'pkg', 'documenter.jl'],
            'frameworks': ['flux.jl', 'plots.jl', 'dataframes.jl'],
            'package_managers': ['pkg']
        },
        
        # ===== MOBILE DEVELOPMENT =====
        'dart': {
            'extensions': ['.dart'],
            'files': ['pubspec.yaml', 'pubspec.lock', 'analysis_options.yaml'],
            'directories': ['lib', 'test', 'build', '.dart_tool'],
            'tools': ['dart', 'flutter', 'pub', 'dartanalyzer', 'dartfmt'],
            'frameworks': ['flutter', 'angulardart', 'shelf'],
            'package_managers': ['pub', 'flutter']
        },
        'objectivec': {
            'extensions': ['.m', '.mm', '.h'],
            'files': ['*.xcodeproj', '*.xcworkspace', 'Podfile'],
            'directories': ['build', 'DerivedData', 'Pods'],
            'tools': ['xcodebuild', 'clang', 'instruments'],
            'frameworks': ['foundation', 'uikit', 'cocoa', 'core data'],
            'package_managers': ['cocoapods', 'carthage', 'swift package manager']
        },
        
        # ===== SCRIPTING LANGUAGES =====
        'perl': {
            'extensions': ['.pl', '.pm', '.t', '.pod'],
            'files': ['Makefile.PL', 'Build.PL', 'cpanfile', 'META.json'],
            'directories': ['lib', 't', 'blib', 'inc'],
            'tools': ['perl', 'cpan', 'prove', 'perltidy', 'perlcritic'],
            'frameworks': ['catalyst', 'dancer', 'mojolicious', 'cgi'],
            'package_managers': ['cpan', 'cpanm', 'carton']
        },
        'bash': {
            'extensions': ['.sh', '.bash', '.zsh', '.ksh', '.csh'],
            'files': ['.bashrc', '.zshrc', 'Makefile'],
            'directories': ['bin', 'scripts', 'lib'],
            'tools': ['shellcheck', 'shfmt', 'bats'],
            'frameworks': ['oh-my-zsh', 'prezto', 'bash-it'],
            'package_managers': ['brew', 'apt', 'yum', 'pacman']
        },
        'fish': {
            'extensions': ['.fish'],
            'files': ['config.fish', 'functions'],
            'directories': ['functions', 'completions', 'conf.d'],
            'tools': ['fish', 'fish_indent'],
            'frameworks': ['oh-my-fish', 'fisher'],
            'package_managers': ['fisher', 'oh-my-fish']
        },
        'lua': {
            'extensions': ['.lua'],
            'files': ['*.rockspec', 'config.lua'],
            'directories': ['lua', 'src', 'lib'],
            'tools': ['lua', 'luac', 'luacheck', 'busted'],
            'frameworks': ['openresty', 'lapis', 'moonscript'],
            'package_managers': ['luarocks', 'lit']
        },
        
        # ===== EMERGING LANGUAGES =====
        'crystal': {
            'extensions': ['.cr'],
            'files': ['shard.yml', 'shard.lock'],
            'directories': ['src', 'spec', 'lib'],
            'tools': ['crystal', 'shards', 'ameba'],
            'frameworks': ['kemal', 'amber', 'lucky'],
            'package_managers': ['shards']
        },
        'nim': {
            'extensions': ['.nim', '.nims', '.nimble'],
            'files': ['*.nimble', 'nim.cfg', 'config.nims'],
            'directories': ['src', 'tests', 'nimcache'],
            'tools': ['nim', 'nimble', 'nimpretty'],
            'frameworks': ['jester', 'karax', 'prologue'],
            'package_managers': ['nimble']
        },
        'vlang': {
            'extensions': ['.v'],
            'files': ['v.mod', 'v.sum'],
            'directories': ['src', 'modules'],
            'tools': ['v'],
            'frameworks': ['vweb', 'ui', 'json'],
            'package_managers': ['v']
        },
        
        # ===== BLOCKCHAIN & SMART CONTRACTS =====
        'solidity': {
            'extensions': ['.sol'],
            'files': ['truffle-config.js', 'hardhat.config.js', 'foundry.toml'],
            'directories': ['contracts', 'migrations', 'test', 'artifacts'],
            'tools': ['solc', 'truffle', 'hardhat', 'foundry', 'slither'],
            'frameworks': ['openzeppelin', 'web3.js', 'ethers.js'],
            'package_managers': ['npm', 'yarn']
        },
        'vyper': {
            'extensions': ['.vy'],
            'files': ['vyper.json', 'brownie-config.yaml'],
            'directories': ['contracts', 'scripts', 'tests'],
            'tools': ['vyper', 'brownie', 'ape'],
            'frameworks': ['brownie', 'ape', 'ethereum'],
            'package_managers': ['pip', 'brownie']
        },
        
        # ===== GAME DEVELOPMENT =====
        'gdscript': {
            'extensions': ['.gd'],
            'files': ['project.godot', 'export_presets.cfg'],
            'directories': ['scenes', 'scripts', 'assets'],
            'tools': ['godot'],
            'frameworks': ['godot engine'],
            'package_managers': ['godot asset library']
        },
        'actionscript': {
            'extensions': ['.as', '.mxml'],
            'files': ['flex-config.xml', 'build.xml'],
            'directories': ['src', 'bin', 'libs'],
            'tools': ['mxmlc', 'compc', 'adt'],
            'frameworks': ['flex', 'air', 'flash'],
            'package_managers': ['ane', 'swc']
        },
        
        # ===== DOMAIN-SPECIFIC LANGUAGES =====
        'verilog': {
            'extensions': ['.v', '.vh', '.sv'],
            'files': ['Makefile', '*.ucf', '*.xdc'],
            'directories': ['sim', 'syn', 'tb'],
            'tools': ['iverilog', 'verilator', 'yosys'],
            'frameworks': ['vivado', 'quartus', 'icestorm'],
            'package_managers': ['fusesoc', 'verilogs']
        },
        'vhdl': {
            'extensions': ['.vhd', '.vhdl'],
            'files': ['*.prj', '*.ucf', '*.xdc'],
            'directories': ['src', 'sim', 'syn'],
            'tools': ['ghdl', 'modelsim', 'vivado'],
            'frameworks': ['ieee', 'std_logic', 'numeric_std'],
            'package_managers': ['fusesoc']
        },
        'systemverilog': {
            'extensions': ['.sv', '.svh'],
            'files': ['Makefile', '*.f', '*.vc'],
            'directories': ['src', 'tb', 'dv'],
            'tools': ['vcs', 'questa', 'xcelium', 'verilator'],
            'frameworks': ['uvm', 'ovi', 'systemc'],
            'package_managers': ['fusesoc']
        },
        
        # ===== CONFIGURATION & MARKUP =====
        'yaml': {
            'extensions': ['.yaml', '.yml'],
            'files': ['.github/workflows/*.yml', 'docker-compose.yml', 'ansible.yml'],
            'directories': ['.github', 'config', 'deploy'],
            'tools': ['yamllint', 'yq'],
            'frameworks': ['kubernetes', 'docker-compose', 'ansible'],
            'package_managers': ['helm', 'kustomize']
        },
        'toml': {
            'extensions': ['.toml'],
            'files': ['pyproject.toml', 'Cargo.toml', 'config.toml'],
            'directories': ['config', '.cargo'],
            'tools': ['toml-sort', 'taplo'],
            'frameworks': ['rust', 'python', 'hugo'],
            'package_managers': ['cargo', 'pip']
        },
        'json': {
            'extensions': ['.json', '.jsonc', '.json5'],
            'files': ['package.json', 'tsconfig.json', 'composer.json'],
            'directories': ['config', 'data', 'schemas'],
            'tools': ['jq', 'jsonlint', 'prettier'],
            'frameworks': ['json schema', 'rest api', 'nosql'],
            'package_managers': ['npm', 'composer']
        },
        'xml': {
            'extensions': ['.xml', '.xsd', '.xsl', '.xslt'],
            'files': ['pom.xml', 'build.xml', 'web.xml'],
            'directories': ['resources', 'config', 'schemas'],
            'tools': ['xmllint', 'xsltproc', 'tidy'],
            'frameworks': ['spring', 'soap', 'maven'],
            'package_managers': ['maven', 'ivy']
        },
        'markdown': {
            'extensions': ['.md', '.markdown', '.mdown'],
            'files': ['README.md', 'CHANGELOG.md', 'docs/*.md'],
            'directories': ['docs', 'documentation', '.github'],
            'tools': ['markdownlint', 'remark', 'pandoc'],
            'frameworks': ['gitbook', 'mkdocs', 'docusaurus'],
            'package_managers': ['npm', 'gem']
        },
        'dockerfile': {
            'extensions': [],
            'files': ['Dockerfile', 'Dockerfile.*', '.dockerignore'],
            'directories': ['.docker', 'docker'],
            'tools': ['docker', 'hadolint', 'dive'],
            'frameworks': ['docker', 'kubernetes', 'docker-compose'],
            'package_managers': ['docker', 'helm']
        },
        'makefile': {
            'extensions': [],
            'files': ['Makefile', 'makefile', 'GNUmakefile'],
            'directories': ['build', 'scripts'],
            'tools': ['make', 'cmake', 'ninja'],
            'frameworks': ['autotools', 'cmake', 'meson'],
            'package_managers': ['make', 'pkg-config']
        },
        'terraform': {
            'extensions': ['.tf', '.tfvars'],
            'files': ['main.tf', 'variables.tf', 'outputs.tf', 'terraform.tfvars'],
            'directories': ['.terraform', 'modules', 'environments'],
            'tools': ['terraform', 'tflint', 'terragrunt', 'checkov'],
            'frameworks': ['aws', 'azure', 'gcp', 'kubernetes'],
            'package_managers': ['terraform', 'terragrunt']
        }
    }
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeSnip-CLI"
        }
    
    def detect_languages(self, repository: str, pr_number: Optional[int] = None) -> Dict[str, any]:
        """
        Detect languages used in repository and PR
        
        Args:
            repository: GitHub repository (owner/repo)
            pr_number: Optional PR number for PR-specific analysis
        
        Returns:
            Dict with detected languages, confidence scores, and recommendations
        """
        logger.info(f"🔍 Detecting languages for {repository}")
        
        # Get GitHub's language detection
        github_languages = self._get_github_languages(repository)
        
        # Get repository files for deeper analysis
        repo_files = self._get_repository_files(repository)
        
        # Analyze PR-specific changes if provided
        pr_languages = {}
        if pr_number:
            pr_languages = self._analyze_pr_languages(repository, pr_number)
        
        # Combine and analyze all data
        detected_languages = self._analyze_languages(
            github_languages, repo_files, pr_languages
        )
        
        return {
            'primary_language': detected_languages.get('primary'),
            'languages': detected_languages.get('languages', {}),
            'confidence_scores': detected_languages.get('confidence', {}),
            'tools_needed': detected_languages.get('tools', []),
            'package_managers': detected_languages.get('package_managers', []),
            'frameworks': detected_languages.get('frameworks', []),
            'github_languages': github_languages,
            'pr_specific': pr_languages
        }
    
    def _get_github_languages(self, repository: str) -> Dict[str, int]:
        """Get language statistics from GitHub API"""
        try:
            url = f"https://api.github.com/repos/{repository}/languages"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to get GitHub languages: {e}")
            return {}
    
    def _get_repository_files(self, repository: str, path: str = "") -> List[Dict]:
        """Get repository file tree for analysis"""
        try:
            url = f"https://api.github.com/repos/{repository}/contents/{path}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to get repository files: {e}")
            return []
    
    def _analyze_pr_languages(self, repository: str, pr_number: int) -> Dict[str, int]:
        """Analyze languages in PR changes"""
        try:
            # Get PR files
            url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}/files"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            files = response.json()
            language_counts = {}
            
            for file in files:
                filename = file.get('filename', '')
                additions = file.get('additions', 0)
                
                # Detect language by file extension
                detected_lang = self._detect_language_by_extension(filename)
                if detected_lang:
                    language_counts[detected_lang] = language_counts.get(detected_lang, 0) + additions
            
            return language_counts
            
        except Exception as e:
            logger.warning(f"Failed to analyze PR languages: {e}")
            return {}
    
    def _detect_language_by_extension(self, filename: str) -> Optional[str]:
        """Detect language by file extension"""
        ext = Path(filename).suffix.lower()
        
        for lang, config in self.LANGUAGE_PATTERNS.items():
            if ext in config['extensions']:
                return lang
        
        return None
    
    def _analyze_languages(self, github_langs: Dict, repo_files: List, pr_langs: Dict) -> Dict:
        """Combine all language detection methods and provide analysis"""
        
        # Calculate language percentages from GitHub
        total_bytes = sum(github_langs.values()) if github_langs else 1
        github_percentages = {
            lang: (bytes_count / total_bytes) * 100 
            for lang, bytes_count in github_langs.items()
        }
        
        # Map GitHub language names to our internal names
        mapped_languages = self._map_github_languages(github_percentages)
        
        # Analyze repository files for configuration files
        file_based_detection = self._analyze_repo_files(repo_files)
        
        # Combine confidence scores
        combined_languages = {}
        confidence_scores = {}
        
        # Weight GitHub detection heavily (60%)
        for lang, percentage in mapped_languages.items():
            combined_languages[lang] = percentage * 0.6
            confidence_scores[lang] = min(0.8, percentage / 100 * 0.8)
        
        # Add file-based detection (30%)
        for lang, score in file_based_detection.items():
            combined_languages[lang] = combined_languages.get(lang, 0) + score * 30
            confidence_scores[lang] = max(confidence_scores.get(lang, 0), score * 0.3)
        
        # Add PR-specific detection (10%)
        if pr_langs:
            pr_total = sum(pr_langs.values()) or 1
            for lang, count in pr_langs.items():
                pr_percentage = (count / pr_total) * 10
                combined_languages[lang] = combined_languages.get(lang, 0) + pr_percentage
                confidence_scores[lang] = max(confidence_scores.get(lang, 0), pr_percentage / 100)
        
        # Determine primary language
        primary = max(combined_languages.items(), key=lambda x: x[1])[0] if combined_languages else 'unknown'
        
        # Get tools, frameworks, and package managers
        tools_needed = set()
        package_managers = set()
        frameworks = set()
        
        for lang in combined_languages.keys():
            if lang in self.LANGUAGE_PATTERNS:
                tools_needed.update(self.LANGUAGE_PATTERNS[lang]['tools'])
                package_managers.update(self.LANGUAGE_PATTERNS[lang]['package_managers'])
                frameworks.update(self.LANGUAGE_PATTERNS[lang]['frameworks'])
        
        return {
            'primary': primary,
            'languages': combined_languages,
            'confidence': confidence_scores,
            'tools': list(tools_needed),
            'package_managers': list(package_managers),
            'frameworks': list(frameworks)
        }
    
    def _map_github_languages(self, github_langs: Dict[str, float]) -> Dict[str, float]:
        """Map GitHub language names to our internal language names"""
        mapping = {
            'Python': 'python',
            'JavaScript': 'javascript',
            'TypeScript': 'typescript',
            'Go': 'go',
            'Java': 'java',
            'C#': 'csharp',
            'Rust': 'rust',
            'C++': 'cpp',
            'C': 'c',
            'PHP': 'php',
            'Ruby': 'ruby',
            'Swift': 'swift',
            'Kotlin': 'kotlin',
            'Scala': 'scala',
            'HTML': 'html',
            'CSS': 'css',
            'Shell': 'shell',
            'Dockerfile': 'docker'
        }
        
        mapped = {}
        for github_lang, percentage in github_langs.items():
            internal_lang = mapping.get(github_lang, github_lang.lower())
            mapped[internal_lang] = percentage
        
        return mapped
    
    def _analyze_repo_files(self, files: List[Dict]) -> Dict[str, float]:
        """Analyze repository files for language indicators"""
        detection_scores = {}
        
        for file_info in files:
            if file_info.get('type') != 'file':
                continue
                
            filename = file_info.get('name', '')
            
            # Check against known configuration files
            for lang, config in self.LANGUAGE_PATTERNS.items():
                # Check specific files
                for known_file in config['files']:
                    if '*' in known_file:
                        # Handle wildcard patterns
                        pattern = known_file.replace('*', '.*')
                        if re.match(pattern, filename, re.IGNORECASE):
                            detection_scores[lang] = detection_scores.get(lang, 0) + 0.5
                    elif filename.lower() == known_file.lower():
                        detection_scores[lang] = detection_scores.get(lang, 0) + 0.5
                
                # Check file extensions
                for ext in config['extensions']:
                    if filename.lower().endswith(ext):
                        detection_scores[lang] = detection_scores.get(lang, 0) + 0.1
        
        return detection_scores

    def get_language_specific_config(self, language: str) -> Dict[str, any]:
        """Get language-specific configuration"""
        if language not in self.LANGUAGE_PATTERNS:
            return {}
        
        config = self.LANGUAGE_PATTERNS[language].copy()
        
        # Add language-specific quality rules
        config['quality_rules'] = self._get_quality_rules(language)
        config['security_rules'] = self._get_security_rules(language)
        config['performance_rules'] = self._get_performance_rules(language)
        
        return config
    
    def _get_quality_rules(self, language: str) -> List[str]:
        """Get quality rules for specific language"""
        rules = {
            'python': [
                'line_length_limit: 88',
                'complexity_limit: 10',
                'docstring_required: true',
                'type_hints_required: true'
            ],
            'javascript': [
                'line_length_limit: 100',
                'complexity_limit: 10',
                'semicolons_required: true',
                'consistent_quotes: single'
            ],
            'go': [
                'line_length_limit: 120',
                'gofmt_required: true',
                'go_vet_required: true',
                'unused_variables: error'
            ],
            'java': [
                'line_length_limit: 120',
                'checkstyle_required: true',
                'null_safety: warn',
                'javadoc_required: true'
            ]
        }
        return rules.get(language, [])
    
    def _get_security_rules(self, language: str) -> List[str]:
        """Get security rules for specific language"""
        rules = {
            'python': [
                'bandit_scan: true',
                'sql_injection_check: true',
                'hardcoded_secrets: error'
            ],
            'javascript': [
                'npm_audit: true',
                'xss_protection: true',
                'eval_usage: error'
            ],
            'go': [
                'gosec_scan: true',
                'dependency_check: true',
                'tls_verification: required'
            ]
        }
        return rules.get(language, [])
    
    def _get_performance_rules(self, language: str) -> List[str]:
        """Get performance rules for specific language"""
        rules = {
            'python': [
                'memory_profiling: enabled',
                'n_plus_one_queries: detect',
                'large_data_structures: warn'
            ],
            'javascript': [
                'bundle_size_limit: 250kb',
                'memory_leaks: detect',
                'async_optimization: suggest'
            ]
        }
        return rules.get(language, [])