use std::path::Path;
use std::sync::Once;

use anyhow::Result;
use clap::{Parser, Subcommand, ValueEnum};
use tracing_subscriber::EnvFilter;

use futures::future::try_join_all;
use pysentry::dependency::resolvers::{ResolverRegistry, ResolverType};
use pysentry::parsers::{requirements::RequirementsParser, DependencyStats};
use pysentry::types::Version;
use pysentry::{
    AuditCache, AuditReport, DependencyScanner, MatcherConfig, ReportGenerator,
    VulnerabilityDatabase, VulnerabilityMatcher, VulnerabilitySource,
};
use std::str::FromStr;

#[derive(Debug, Clone, ValueEnum)]
pub enum AuditFormat {
    #[value(name = "human")]
    Human,
    #[value(name = "json")]
    Json,
    #[value(name = "sarif")]
    Sarif,
    #[value(name = "markdown")]
    Markdown,
}

#[derive(Debug, Clone, ValueEnum)]
pub enum SeverityLevel {
    #[value(name = "low")]
    Low,
    #[value(name = "medium")]
    Medium,
    #[value(name = "high")]
    High,
    #[value(name = "critical")]
    Critical,
}

#[derive(Debug, Clone, ValueEnum, PartialEq)]
pub enum VulnerabilitySourceType {
    #[value(name = "pypa")]
    Pypa,
    #[value(name = "pypi")]
    Pypi,
    #[value(name = "osv")]
    Osv,
}

#[derive(Debug, Clone, ValueEnum)]
pub enum ResolverTypeArg {
    #[value(name = "uv")]
    Uv,
    #[value(name = "pip-tools")]
    PipTools,
}

#[derive(Parser)]
#[command(
    name = "pysentry",
    about = "Security vulnerability auditing for Python packages",
    version
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,

    /// Audit arguments (used when no subcommand specified)
    #[command(flatten)]
    pub audit_args: AuditArgs,
}

#[derive(Debug, Subcommand)]
pub enum Commands {
    /// Check available dependency resolvers
    Resolvers(ResolversArgs),
    /// Check if a newer version is available
    CheckVersion(CheckVersionArgs),
}

#[derive(Debug, Parser)]
pub struct AuditArgs {
    /// Path to the project directory to audit
    #[arg(value_name = "PATH", default_value = ".")]
    pub path: std::path::PathBuf,

    /// Output format
    #[arg(long, value_enum, default_value = "human")]
    pub format: AuditFormat,

    /// Minimum severity level to report
    #[arg(long, value_enum, default_value = "low")]
    pub severity: SeverityLevel,

    /// Fail (exit non-zero) if vulnerabilities of this severity or higher are found
    #[arg(long, value_enum, default_value = "medium")]
    pub fail_on: SeverityLevel,

    /// Vulnerability IDs to ignore (can be specified multiple times)
    #[arg(long = "ignore", value_name = "ID")]
    pub ignore_ids: Vec<String>,

    /// Output file path (defaults to stdout)
    #[arg(long, short, value_name = "FILE")]
    pub output: Option<std::path::PathBuf>,

    /// Include ALL dependencies (main + dev, optional, etc) [DEPRECATED: use --all-extras instead]
    #[arg(long, hide = true)]
    pub all: bool,

    /// Include ALL extra dependencies (main + dev, optional, etc)
    #[arg(long)]
    pub all_extras: bool,

    /// Only check direct dependencies (exclude transitive)
    #[arg(long)]
    pub direct_only: bool,

    /// Disable caching
    #[arg(long)]
    pub no_cache: bool,

    /// Custom cache directory
    #[arg(long, value_name = "DIR")]
    pub cache_dir: Option<std::path::PathBuf>,

    /// Vulnerability data source [DEPRECATED: use --sources instead]
    #[arg(long, value_enum, default_value = "pypa", hide = true)]
    pub source: VulnerabilitySourceType,

    /// Vulnerability data sources (can be specified multiple times or comma-separated)
    #[arg(long = "sources", value_name = "SOURCE")]
    pub sources: Vec<String>,

    /// Dependency resolver for requirements.txt files
    #[arg(long, value_enum, default_value = "uv")]
    pub resolver: ResolverTypeArg,

    /// Specific requirements files to audit (disables auto-discovery)
    #[arg(long = "requirements-files", value_name = "FILE", num_args = 1..)]
    pub requirements_files: Vec<std::path::PathBuf>,

    /// Enable verbose output
    #[arg(long, short)]
    pub verbose: bool,

    /// Suppress non-error output
    #[arg(long, short)]
    pub quiet: bool,
}

impl AuditArgs {
    fn include_all_dependencies(&self) -> bool {
        static DEPRECATION_WARNING_SHOWN: Once = Once::new();

        if self.all && self.all_extras {
            DEPRECATION_WARNING_SHOWN.call_once(|| {
                eprintln!("Warning: Both --all and --all-extras flags are specified. Using --all-extras only. The --all flag is deprecated.");
            });
            return true;
        }

        if self.all {
            DEPRECATION_WARNING_SHOWN.call_once(|| {
                eprintln!("Warning: --all flag is deprecated and will be removed in a future version. Use --all-extras instead.");
            });
            return true;
        }

        self.all_extras
    }

    pub fn include_dev(&self) -> bool {
        self.include_all_dependencies()
    }

    pub fn include_optional(&self) -> bool {
        self.include_all_dependencies()
    }

    pub fn scope_description(&self) -> &'static str {
        if self.include_all_dependencies() {
            "all (main + dev,optional,prod,etc)"
        } else {
            "main only"
        }
    }

    pub fn filter_dependencies(
        &self,
        dependencies: Vec<pysentry::parsers::ParsedDependency>,
    ) -> Vec<pysentry::parsers::ParsedDependency> {
        if self.include_all_dependencies() {
            dependencies
        } else {
            dependencies
                .into_iter()
                .filter(|dep| {
                    matches!(dep.dependency_type, pysentry::parsers::DependencyType::Main)
                })
                .collect()
        }
    }

    /// Resolve vulnerability sources from both old and new CLI arguments
    pub fn resolve_sources(&self) -> Result<Vec<VulnerabilitySourceType>, String> {
        use std::sync::Once;
        static DEPRECATION_WARNING_SHOWN: Once = Once::new();

        let mut resolved_sources = Vec::new();

        // Handle new --sources argument
        if !self.sources.is_empty() {
            for source_arg in &self.sources {
                // Handle comma-separated values
                for source_str in source_arg.split(',') {
                    let source_str = source_str.trim();
                    if source_str.is_empty() {
                        continue;
                    }
                    let source_type = match source_str {
                        "pypa" => VulnerabilitySourceType::Pypa,
                        "pypi" => VulnerabilitySourceType::Pypi,
                        "osv" => VulnerabilitySourceType::Osv,
                        _ => {
                            return Err(format!(
                            "Invalid vulnerability source: '{source_str}'. Valid sources: pypa, pypi, osv"
                        ))
                        }
                    };
                    resolved_sources.push(source_type);
                }
            }
        }

        // Handle default when no --sources specified
        if resolved_sources.is_empty() {
            // If --source was explicitly set to something other than default, use it with deprecation warning
            if self.source != VulnerabilitySourceType::Pypa {
                DEPRECATION_WARNING_SHOWN.call_once(|| {
                    eprintln!("Warning: --source flag is deprecated and will be removed in a future version. Use --sources instead.");
                });
                resolved_sources.push(self.source.clone());
            } else {
                // Default to pypa (future-proof for when --source is removed)
                resolved_sources.push(VulnerabilitySourceType::Pypa);
            }
        }

        // Remove duplicates while preserving order
        let mut unique_sources = Vec::new();
        for source in resolved_sources {
            if !unique_sources.contains(&source) {
                unique_sources.push(source);
            }
        }

        Ok(unique_sources)
    }
}

#[derive(Debug, Parser)]
pub struct ResolversArgs {
    /// Enable verbose output
    #[arg(long, short)]
    pub verbose: bool,
}

#[derive(Debug, Parser)]
pub struct CheckVersionArgs {
    /// Enable verbose output
    #[arg(long, short)]
    pub verbose: bool,
}

/// Check available dependency resolvers on the system
async fn check_resolvers(verbose: bool) -> Result<()> {
    if !verbose {
        println!("Checking available dependency resolvers...");
        println!();
    }

    let all_resolvers = vec![ResolverType::Uv, ResolverType::PipTools];

    let mut available_resolvers = Vec::new();
    let mut unavailable_resolvers = Vec::new();

    for resolver_type in all_resolvers {
        if verbose {
            println!("Checking {resolver_type}...");
        }

        let resolver = ResolverRegistry::create_resolver(resolver_type);
        let is_available = resolver.is_available().await;

        if is_available {
            available_resolvers.push(resolver_type);
        } else {
            unavailable_resolvers.push(resolver_type);
        }
    }

    if !available_resolvers.is_empty() {
        println!("✓ Available resolvers ({}):", available_resolvers.len());
        for resolver in &available_resolvers {
            println!("  {resolver}");
        }
        println!();
    }

    if !unavailable_resolvers.is_empty() {
        println!("✗ Unavailable resolvers ({}):", unavailable_resolvers.len());
        for resolver in &unavailable_resolvers {
            println!("  {resolver} - not installed or not in PATH");
        }
        println!();
    }

    if available_resolvers.is_empty() {
        println!("⚠️  No dependency resolvers are available!");
        println!("Please install at least one resolver:");
        println!("  • UV (recommended): https://docs.astral.sh/uv/");
        println!("  • pip-tools: pip install pip-tools");
        return Ok(());
    }

    match ResolverRegistry::detect_best_resolver().await {
        Ok(best) => {
            println!("🎯 Auto-detected resolver: {best}");
        }
        Err(_) => {
            println!("⚠️  No resolver can be auto-detected");
        }
    }

    Ok(())
}

/// Check if a newer version is available
async fn check_version(verbose: bool) -> Result<()> {
    const CURRENT_VERSION: &str = env!("CARGO_PKG_VERSION");
    const GITHUB_REPO: &str = "nyudenkov/pysentry";

    if verbose {
        println!("Checking for updates...");
        println!("Current version: {CURRENT_VERSION}");
        println!("Repository: {GITHUB_REPO}");
    } else {
        println!("Checking for updates...");
    }

    // Create HTTP client
    let client = reqwest::Client::new();
    let url = format!("https://api.github.com/repos/{GITHUB_REPO}/releases/latest");

    if verbose {
        println!("Fetching: {url}");
    }

    // Fetch latest release info
    let response = match client
        .get(&url)
        .header("User-Agent", format!("pysentry/{CURRENT_VERSION}"))
        .header("Accept", "application/vnd.github+json")
        .send()
        .await
    {
        Ok(response) => response,
        Err(e) => {
            eprintln!("Failed to check for updates: {e}");
            return Ok(());
        }
    };

    if !response.status().is_success() {
        eprintln!("Failed to check for updates: HTTP {}", response.status());
        return Ok(());
    }

    // Parse response
    let release_info: serde_json::Value = match response.json().await {
        Ok(json) => json,
        Err(e) => {
            eprintln!("Failed to parse release information: {e}");
            return Ok(());
        }
    };

    // Extract tag name (version)
    let latest_tag = match release_info["tag_name"].as_str() {
        Some(tag) => tag,
        None => {
            eprintln!("Failed to get latest version information");
            return Ok(());
        }
    };

    // Remove 'v' prefix if present
    let latest_version_str = latest_tag.strip_prefix('v').unwrap_or(latest_tag);

    if verbose {
        println!("Latest release tag: {latest_tag}");
    }

    // Parse versions for comparison
    let current_version = match Version::from_str(CURRENT_VERSION) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("Failed to parse current version: {e}");
            return Ok(());
        }
    };

    let latest_version = match Version::from_str(latest_version_str) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("Failed to parse latest version '{latest_version_str}': {e}");
            return Ok(());
        }
    };

    // Compare versions
    if latest_version > current_version {
        println!("✨ Update available!");
        println!("Current version: {CURRENT_VERSION}");
        println!("Latest version:  {latest_version_str}");
        println!();
        println!("To update:");
        println!("  • Rust CLI: cargo install pysentry");
        println!("  • Python package: pip install --upgrade pysentry-rs");
        if let Some(release_url) = release_info["html_url"].as_str() {
            println!("  • Release notes: {release_url}");
        }
    } else if latest_version < current_version {
        println!("🚀 You're running a development version!");
        println!("Current version: {CURRENT_VERSION}");
        println!("Latest stable:   {latest_version_str}");
    } else {
        println!("✅ You're running the latest version!");
        println!("Current version: {CURRENT_VERSION}");
    }

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Cli::parse();

    match args.command {
        // No subcommand provided - run audit with flattened args
        None => {
            let audit_args = args.audit_args;

            // Initialize logging
            let log_level = if audit_args.verbose {
                "debug"
            } else if audit_args.quiet {
                "error"
            } else {
                "info"
            };

            tracing_subscriber::fmt()
                .with_env_filter(EnvFilter::from_default_env().add_directive(log_level.parse()?))
                .init();

            // Create cache directory
            let cache_dir = audit_args.cache_dir.clone().unwrap_or_else(|| {
                dirs::cache_dir()
                    .unwrap_or_else(std::env::temp_dir)
                    .join("pysentry")
            });

            let exit_code = audit(&audit_args, &cache_dir).await?;

            std::process::exit(exit_code);
        }
        Some(Commands::Resolvers(resolvers_args)) => {
            let log_level = if resolvers_args.verbose {
                "debug"
            } else {
                "error"
            };

            tracing_subscriber::fmt()
                .with_env_filter(EnvFilter::from_default_env().add_directive(log_level.parse()?))
                .init();

            check_resolvers(resolvers_args.verbose).await?;
            std::process::exit(0);
        }
        Some(Commands::CheckVersion(check_version_args)) => {
            let log_level = if check_version_args.verbose {
                "debug"
            } else {
                "error"
            };

            tracing_subscriber::fmt()
                .with_env_filter(EnvFilter::from_default_env().add_directive(log_level.parse()?))
                .init();

            check_version(check_version_args.verbose).await?;
            std::process::exit(0);
        }
    }
}

async fn audit(audit_args: &AuditArgs, cache_dir: &Path) -> Result<i32> {
    if !audit_args.quiet {
        eprintln!(
            "Auditing dependencies for vulnerabilities in {}...",
            audit_args.path.display()
        );
    }

    if audit_args.verbose {
        eprintln!(
            "Configuration: format={:?}, severity={:?}, fail_on={:?}, source={:?}, scope='{}', direct_only={}",
            audit_args.format,
            audit_args.severity,
            audit_args.fail_on,
            audit_args.source,
            audit_args.scope_description(),
            audit_args.direct_only
        );
        eprintln!("Cache directory: {}", cache_dir.display());

        if !audit_args.ignore_ids.is_empty() {
            eprintln!(
                "Ignoring vulnerability IDs: {}",
                audit_args.ignore_ids.join(", ")
            );
        }
    }

    let audit_result = perform_audit(audit_args, cache_dir).await;

    let report = match audit_result {
        Ok(report) => report,
        Err(e) => {
            eprintln!("Error: Audit failed: {e}");
            return Ok(1);
        }
    };

    let report_output = ReportGenerator::generate(
        &report,
        audit_args.format.clone().into(),
        Some(&audit_args.path),
    )
    .map_err(|e| anyhow::anyhow!("Failed to generate report: {e}"))?;

    if let Some(output_path) = &audit_args.output {
        fs_err::write(output_path, &report_output)?;
        if !audit_args.quiet {
            eprintln!("Audit results written to: {}", output_path.display());
        }
    } else {
        println!("{report_output}");
    }

    if report.should_fail_on_severity(&audit_args.fail_on.clone().into()) {
        Ok(1)
    } else {
        Ok(0)
    }
}

async fn perform_audit(audit_args: &AuditArgs, cache_dir: &Path) -> Result<AuditReport> {
    // Create cache directory if it doesn't exist
    std::fs::create_dir_all(cache_dir)?;
    let audit_cache = AuditCache::new(cache_dir.to_path_buf());

    // Resolve vulnerability sources from CLI arguments
    let source_types = match audit_args.resolve_sources() {
        Ok(sources) => sources,
        Err(e) => {
            return Err(anyhow::anyhow!("Invalid vulnerability sources: {}", e));
        }
    };

    // Create vulnerability sources
    let vuln_sources: Vec<_> = source_types
        .iter()
        .map(|source_type| {
            VulnerabilitySource::new(
                source_type.clone().into(),
                audit_cache.clone(),
                audit_args.no_cache,
            )
        })
        .collect();

    // Get source names for display
    let source_names: Vec<_> = vuln_sources.iter().map(|s| s.name()).collect();
    if !audit_args.quiet {
        if source_names.len() == 1 {
            eprintln!("Fetching vulnerability data from {}...", source_names[0]);
        } else {
            eprintln!(
                "Fetching vulnerability data from {} sources: {}...",
                source_names.len(),
                source_names.join(", ")
            );
        }
    }

    if !audit_args.quiet {
        eprintln!("Scanning project dependencies...");
    }

    let dependencies = if !audit_args.requirements_files.is_empty() {
        // Use explicit requirements files - bypass normal scanner
        if !audit_args.quiet {
            eprintln!(
                "Using explicit requirements files: {}",
                audit_args
                    .requirements_files
                    .iter()
                    .map(|p| p.display().to_string())
                    .collect::<Vec<_>>()
                    .join(", ")
            );
        }
        scan_explicit_requirements(
            &audit_args.requirements_files,
            audit_args.include_dev(),
            audit_args.include_optional(),
            audit_args.direct_only,
            audit_args.resolver.clone(),
        )
        .await?
    } else {
        let resolver_type: ResolverType = audit_args.resolver.clone().into();

        let parse_dev = audit_args.include_dev();
        let parse_optional = audit_args.include_optional();

        // Note: We bypass the scanner and use parser directly for better control over dependency types
        // let scanner = DependencyScanner::new(parse_dev, parse_optional, audit_args.direct_only, Some(resolver_type));

        // Step 2: Convert to ParsedDependency for filtering (we need access to dependency_type)
        // Since we don't have access to the raw ParsedDependency from scanner,
        // we need to use the parser directly

        // Get the raw parsed dependencies with proper types
        use pysentry::parsers::{DependencyType, ParserRegistry};
        let parser_registry = ParserRegistry::new(Some(resolver_type));
        let (raw_parsed_deps, parser_name) = parser_registry
            .parse_project(
                &audit_args.path,
                parse_dev,
                parse_optional,
                audit_args.direct_only,
            )
            .await?;

        if audit_args.verbose {
            eprintln!(
                "Raw parsed dependencies before filtering: {} (from {})",
                raw_parsed_deps.len(),
                parser_name
            );
            let (main_count, optional_count) =
                raw_parsed_deps
                    .iter()
                    .fold((0, 0), |(m, o), dep| match dep.dependency_type {
                        DependencyType::Main => (m + 1, o),
                        DependencyType::Optional => (m, o + 1),
                    });
            eprintln!("  Main: {main_count}, Optional: {optional_count}");
        }

        // Step 3: Apply scope-based filtering
        let filtered_parsed_deps = audit_args.filter_dependencies(raw_parsed_deps);

        if audit_args.verbose {
            eprintln!(
                "Filtered dependencies after scope filtering: {}",
                filtered_parsed_deps.len()
            );
            eprintln!("  Scope: {}", audit_args.scope_description());
        }

        // Step 4: Convert filtered ParsedDependency back to ScannedDependency
        filtered_parsed_deps
            .into_iter()
            .map(|dep| pysentry::dependency::scanner::ScannedDependency {
                name: dep.name,
                version: dep.version,
                is_direct: dep.is_direct,
                source: dep.source.into(),
                path: dep.path,
            })
            .collect()
    };

    let dependency_stats = if !audit_args.requirements_files.is_empty() {
        // Calculate stats directly since we don't have a scanner instance
        calculate_dependency_stats(&dependencies)
    } else {
        let scanner = DependencyScanner::new(
            audit_args.include_dev(),
            audit_args.include_optional(),
            audit_args.direct_only,
            None,
        );
        scanner.get_stats(&dependencies)
    };

    if audit_args.verbose {
        eprintln!("{dependency_stats}");
    }

    let warnings = if !audit_args.requirements_files.is_empty() {
        // For explicit requirements files, provide basic validation
        if dependencies.is_empty() {
            vec!["No dependencies found in specified requirements files.".to_string()]
        } else {
            vec![]
        }
    } else {
        // Use scanner validation for normal project scanning
        let scanner = DependencyScanner::new(
            audit_args.include_dev(),
            audit_args.include_optional(),
            audit_args.direct_only,
            None,
        );
        scanner.validate_dependencies(&dependencies)
    };

    for warning in &warnings {
        if !audit_args.quiet {
            eprintln!("Warning: {warning}");
        }
    }

    // Prepare package list for vulnerability fetching
    let packages: Vec<(String, String)> = dependencies
        .iter()
        .map(|dep| (dep.name.to_string(), dep.version.to_string()))
        .collect();

    // Fetch vulnerabilities concurrently from all sources
    if !audit_args.quiet {
        if source_names.len() == 1 {
            eprintln!(
                "Fetching vulnerabilities for {} packages from {}...",
                packages.len(),
                source_names[0]
            );
        } else {
            eprintln!(
                "Fetching vulnerabilities for {} packages from {} sources concurrently...",
                packages.len(),
                source_names.len()
            );
        }
    }

    // Create concurrent fetch tasks for all sources
    let fetch_tasks = vuln_sources.into_iter().map(|source| {
        let packages = packages.clone();
        async move { source.fetch_vulnerabilities(&packages).await }
    });

    // Execute all fetch tasks concurrently
    let databases = try_join_all(fetch_tasks).await?;

    // Merge all databases into a single database
    let database = if databases.len() == 1 {
        databases.into_iter().next().unwrap()
    } else {
        if !audit_args.quiet {
            eprintln!(
                "Merging vulnerability data from {} sources...",
                databases.len()
            );
        }
        VulnerabilityDatabase::merge(databases)
    };

    if !audit_args.quiet {
        eprintln!("Matching against vulnerability database...");
    }
    let matcher_config = MatcherConfig::new(
        audit_args.severity.clone().into(),
        audit_args.ignore_ids.to_vec(),
        audit_args.direct_only,
    );
    let matcher = VulnerabilityMatcher::new(database, matcher_config);

    let matches = matcher.find_vulnerabilities(&dependencies)?;
    let filtered_matches = matcher.filter_matches(matches);

    let database_stats = matcher.get_database_stats();
    let fix_analysis = matcher.analyze_fixes(&filtered_matches);

    let report = AuditReport::new(
        dependency_stats,
        database_stats,
        filtered_matches,
        fix_analysis,
        warnings,
    );

    let summary = report.summary();
    if !audit_args.quiet {
        eprintln!(
            "Audit complete: {} vulnerabilities found in {} packages",
            summary.total_vulnerabilities, summary.vulnerable_packages
        );
    }

    Ok(report)
}

/// Scan explicit requirements files using specified resolver
async fn scan_explicit_requirements(
    requirements_files: &[std::path::PathBuf],
    _dev: bool,
    _optional: bool,
    direct_only: bool,
    resolver: ResolverTypeArg,
) -> Result<Vec<pysentry::dependency::scanner::ScannedDependency>> {
    let resolver_type: ResolverType = resolver.into();

    let parser = RequirementsParser::new(Some(resolver_type));

    let parsed_deps = parser
        .parse_explicit_files(requirements_files, direct_only)
        .await
        .map_err(|e| anyhow::anyhow!("Failed to parse requirements files: {}", e))?;

    let scanned_dependencies: Vec<pysentry::dependency::scanner::ScannedDependency> = parsed_deps
        .into_iter()
        .map(|dep| pysentry::dependency::scanner::ScannedDependency {
            name: dep.name,
            version: dep.version,
            is_direct: dep.is_direct,
            source: dep.source.into(),
            path: dep.path,
        })
        .collect();

    Ok(scanned_dependencies)
}

/// Calculate dependency stats from ScannedDependencies
fn calculate_dependency_stats(
    dependencies: &[pysentry::dependency::scanner::ScannedDependency],
) -> DependencyStats {
    // Convert ScannedDependency to ParsedDependency for stats calculation
    let parsed_deps: Vec<pysentry::parsers::ParsedDependency> = dependencies
        .iter()
        .map(|dep| pysentry::parsers::ParsedDependency {
            name: dep.name.clone(),
            version: dep.version.clone(),
            is_direct: dep.is_direct,
            source: dep.source.clone().into(),
            path: dep.path.clone(),
            dependency_type: pysentry::parsers::DependencyType::Main,
        })
        .collect();

    DependencyStats::from_dependencies(&parsed_deps)
}

impl From<AuditFormat> for pysentry::AuditFormat {
    fn from(format: AuditFormat) -> Self {
        match format {
            AuditFormat::Human => pysentry::AuditFormat::Human,
            AuditFormat::Json => pysentry::AuditFormat::Json,
            AuditFormat::Sarif => pysentry::AuditFormat::Sarif,
            AuditFormat::Markdown => pysentry::AuditFormat::Markdown,
        }
    }
}

impl From<SeverityLevel> for pysentry::SeverityLevel {
    fn from(severity: SeverityLevel) -> Self {
        match severity {
            SeverityLevel::Low => pysentry::SeverityLevel::Low,
            SeverityLevel::Medium => pysentry::SeverityLevel::Medium,
            SeverityLevel::High => pysentry::SeverityLevel::High,
            SeverityLevel::Critical => pysentry::SeverityLevel::Critical,
        }
    }
}

impl From<VulnerabilitySourceType> for pysentry::VulnerabilitySourceType {
    fn from(source: VulnerabilitySourceType) -> Self {
        match source {
            VulnerabilitySourceType::Pypa => pysentry::VulnerabilitySourceType::Pypa,
            VulnerabilitySourceType::Pypi => pysentry::VulnerabilitySourceType::Pypi,
            VulnerabilitySourceType::Osv => pysentry::VulnerabilitySourceType::Osv,
        }
    }
}

impl From<ResolverTypeArg> for ResolverType {
    fn from(resolver: ResolverTypeArg) -> Self {
        match resolver {
            ResolverTypeArg::Uv => ResolverType::Uv,
            ResolverTypeArg::PipTools => ResolverType::PipTools,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_sources_default() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Pypa,
            sources: vec![], // Empty, should use deprecated source
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let resolved = args.resolve_sources().unwrap();
        assert_eq!(resolved, vec![VulnerabilitySourceType::Pypa]);
    }

    #[test]
    fn test_resolve_sources_multiple() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Pypa,
            sources: vec!["pypi".to_string(), "osv".to_string()],
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let resolved = args.resolve_sources().unwrap();
        assert_eq!(
            resolved,
            vec![VulnerabilitySourceType::Pypi, VulnerabilitySourceType::Osv]
        );
    }

    #[test]
    fn test_resolve_sources_comma_separated() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Pypa,
            sources: vec!["pypa,osv,pypi".to_string()],
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let resolved = args.resolve_sources().unwrap();
        assert_eq!(
            resolved,
            vec![
                VulnerabilitySourceType::Pypa,
                VulnerabilitySourceType::Osv,
                VulnerabilitySourceType::Pypi
            ]
        );
    }

    #[test]
    fn test_resolve_sources_deduplication() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Pypa,
            sources: vec!["pypa".to_string(), "osv".to_string(), "pypa".to_string()],
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let resolved = args.resolve_sources().unwrap();
        assert_eq!(
            resolved,
            vec![VulnerabilitySourceType::Pypa, VulnerabilitySourceType::Osv]
        );
    }

    #[test]
    fn test_resolve_sources_invalid() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Pypa,
            sources: vec!["invalid".to_string()],
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let result = args.resolve_sources();
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .contains("Invalid vulnerability source: 'invalid'"));
    }

    #[test]
    fn test_resolve_sources_no_args_defaults_to_pypa() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Pypa, // Default value
            sources: vec![],                       // Empty - no --sources specified
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let resolved = args.resolve_sources().unwrap();
        assert_eq!(resolved, vec![VulnerabilitySourceType::Pypa]);
    }

    #[test]
    fn test_resolve_sources_explicit_source_shows_warning() {
        let args = AuditArgs {
            path: std::path::PathBuf::from("."),
            format: AuditFormat::Human,
            severity: SeverityLevel::Low,
            fail_on: SeverityLevel::Medium,
            ignore_ids: vec![],
            output: None,
            all: false,
            all_extras: false,
            direct_only: false,
            no_cache: false,
            cache_dir: None,
            source: VulnerabilitySourceType::Osv, // Explicitly set to non-default
            sources: vec![],                      // Empty - no --sources specified
            resolver: ResolverTypeArg::Uv,
            requirements_files: vec![],
            verbose: false,
            quiet: false,
        };

        let resolved = args.resolve_sources().unwrap();
        assert_eq!(resolved, vec![VulnerabilitySourceType::Osv]);
        // Note: Can't easily test the warning message in unit test, but the logic is there
    }
}
