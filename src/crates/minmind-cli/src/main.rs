//! MinMind CLI - Command line interface for the Mind Palace
//!
//! Usage: mm <command> [options]

mod image;

use std::path::PathBuf;
use std::process::Command;

use clap::{Parser, Subcommand, ValueEnum};
use minmind_core::{
    parse_plan_content, update_plan_markers, ActionStatus, Article, ArticleStatus, Note, NoteType,
    Room, Status, SummaryConfig, UserAction, DEFAULT_SUMMARY_PROMPT,
};
use minmind_store::Store;

/// MinMind - Your Mind Palace for execution
#[derive(Parser)]
#[command(name = "mm")]
#[command(author, version, about, long_about = None)]
struct Cli {
    /// Path to the MinMind database
    #[arg(short, long, env = "MINMIND_DB", default_value = "~/.minmind/minmind.db")]
    database: String,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Manage rooms in your Mind Palace
    Room {
        #[command(subcommand)]
        action: RoomCommands,
    },
    /// Manage notes
    Note {
        #[command(subcommand)]
        action: NoteCommands,
    },
    /// Search notes
    Search {
        /// Search query
        query: String,
    },
    /// Manage articles for reading and summarization
    Article {
        #[command(subcommand)]
        action: ArticleCommands,
    },
    /// Manage summary configuration
    Config {
        #[command(subcommand)]
        action: ConfigCommands,
    },
    /// Manage user action todos from plans
    Todo {
        #[command(subcommand)]
        action: TodoCommands,
    },
    /// Image optimization utilities
    Image {
        #[command(subcommand)]
        action: ImageCommands,
    },
}

#[derive(Subcommand)]
enum RoomCommands {
    /// List all rooms
    List,
    /// Create a new room
    Create {
        /// Name of the room
        name: String,
        /// Description of the room
        #[arg(short, long)]
        description: Option<String>,
        /// Parent room ID (for nesting)
        #[arg(short, long)]
        parent: Option<String>,
    },
    /// Delete a room
    Delete {
        /// Room ID or name
        room: String,
    },
}

#[derive(Subcommand)]
enum NoteCommands {
    /// List notes in a room
    List {
        /// Room ID or name
        room: String,
    },
    /// Create a new note
    Create {
        /// Room ID or name
        room: String,
        /// Note title
        title: String,
        /// Note type (idea, task, reference, log)
        #[arg(short = 't', long, default_value = "idea")]
        note_type: String,
        /// Note content
        #[arg(short, long)]
        content: Option<String>,
    },
    /// Show a note
    Show {
        /// Note ID
        id: String,
    },
    /// Delete a note
    Delete {
        /// Note ID
        id: String,
    },
}

#[derive(Clone, Copy, ValueEnum)]
enum ArticleStatusArg {
    Pending,
    Summarized,
    Reviewed,
    Archived,
    All,
}

impl From<ArticleStatusArg> for Option<ArticleStatus> {
    fn from(arg: ArticleStatusArg) -> Self {
        match arg {
            ArticleStatusArg::Pending => Some(ArticleStatus::Pending),
            ArticleStatusArg::Summarized => Some(ArticleStatus::Summarized),
            ArticleStatusArg::Reviewed => Some(ArticleStatus::Reviewed),
            ArticleStatusArg::Archived => Some(ArticleStatus::Archived),
            ArticleStatusArg::All => None,
        }
    }
}

#[derive(Subcommand)]
enum ArticleCommands {
    /// Add an article by URL (fetches and extracts content)
    Add {
        /// URL of the article to add
        url: String,
        /// Room to assign the article to
        #[arg(short, long)]
        room: Option<String>,
    },
    /// List articles
    List {
        /// Filter by status
        #[arg(short, long, value_enum, default_value = "all")]
        status: ArticleStatusArg,
    },
    /// Interactive review dashboard for pending articles
    Review,
    /// Show an article's content and summary
    Show {
        /// Article ID (or partial ID)
        id: String,
    },
    /// Summarize an article using AI
    Summarize {
        /// Article ID (or partial ID)
        id: String,
        /// Provider to use (anthropic, openai)
        #[arg(short, long, default_value = "anthropic")]
        provider: String,
    },
    /// Mark an article as reviewed and optionally convert to a Note
    Approve {
        /// Article ID (or partial ID)
        id: String,
        /// Room to create the Note in
        #[arg(short, long)]
        room: Option<String>,
    },
    /// Archive an article
    Archive {
        /// Article ID (or partial ID)
        id: String,
    },
    /// Delete an article
    Delete {
        /// Article ID (or partial ID)
        id: String,
    },
}

#[derive(Subcommand)]
enum ConfigCommands {
    /// List summary configurations
    List,
    /// Create a new summary configuration
    Create {
        /// Name for this configuration
        name: String,
        /// System prompt for summarization
        #[arg(short, long)]
        prompt: Option<String>,
        /// Room to apply this config to (omit for global)
        #[arg(short, long)]
        room: Option<String>,
    },
    /// Show the default summary prompt
    Default,
    /// Delete a summary configuration
    Delete {
        /// Config ID
        id: String,
    },
}

#[derive(Clone, Copy, ValueEnum)]
enum TodoStatusArg {
    Pending,
    InProgress,
    Completed,
    Skipped,
    All,
}

impl From<TodoStatusArg> for Option<ActionStatus> {
    fn from(arg: TodoStatusArg) -> Self {
        match arg {
            TodoStatusArg::Pending => Some(ActionStatus::Pending),
            TodoStatusArg::InProgress => Some(ActionStatus::InProgress),
            TodoStatusArg::Completed => Some(ActionStatus::Completed),
            TodoStatusArg::Skipped => Some(ActionStatus::Skipped),
            TodoStatusArg::All => None,
        }
    }
}

#[derive(Subcommand)]
enum TodoCommands {
    /// List user action todos
    List {
        /// Filter by status
        #[arg(short, long, value_enum, default_value = "pending")]
        status: TodoStatusArg,
        /// Filter by plan file
        #[arg(short, long)]
        plan: Option<String>,
    },
    /// Sync todos from plan files to database
    Sync {
        /// Directory containing plan files (default: ./plans)
        #[arg(short, long, default_value = "plans")]
        dir: String,
    },
    /// Mark a todo as completed
    Complete {
        /// Todo ID (or partial ID)
        id: String,
    },
    /// Mark a todo as in progress
    Start {
        /// Todo ID (or partial ID)
        id: String,
    },
    /// Mark a todo as skipped
    Skip {
        /// Todo ID (or partial ID)
        id: String,
    },
    /// Add a new todo manually
    Add {
        /// Todo title
        title: String,
        /// Source file to associate with
        #[arg(short, long)]
        plan: Option<String>,
    },
}

#[derive(Subcommand)]
enum ImageCommands {
    /// Optimize an image (compress/convert)
    Optimize {
        /// Input image file path
        input: String,
        /// Output file path (optional, defaults to input_optimized.ext)
        #[arg(short, long)]
        output: Option<String>,
        /// JPEG quality (1-100, default 85)
        #[arg(short, long, default_value = "85")]
        quality: u8,
        /// Output format (jpg, png, defaults to jpg)
        #[arg(short, long)]
        format: Option<String>,
    },
    /// Get information about an image
    Info {
        /// Image file path
        path: String,
    },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    // Expand ~ in database path
    let db_path = expand_path(&cli.database);

    // Ensure parent directory exists
    if let Some(parent) = db_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    let store = Store::open(&db_path)?;

    match cli.command {
        Commands::Room { action } => handle_room_command(&store, action),
        Commands::Note { action } => handle_note_command(&store, action),
        Commands::Search { query } => handle_search(&store, &query),
        Commands::Article { action } => handle_article_command(&store, action, &db_path),
        Commands::Config { action } => handle_config_command(&store, action),
        Commands::Todo { action } => handle_todo_command(&store, action),
        Commands::Image { action } => handle_image_command(action),
    }
}

fn handle_room_command(store: &Store, action: RoomCommands) -> anyhow::Result<()> {
    match action {
        RoomCommands::List => {
            let rooms = store.list_rooms()?;
            if rooms.is_empty() {
                println!("No rooms yet. Create one with: mm room create <name>");
            } else {
                println!("{:<36}  {:<20}  {}", "ID", "NAME", "DESCRIPTION");
                println!("{}", "-".repeat(80));
                for room in rooms {
                    println!(
                        "{:<36}  {:<20}  {}",
                        room.id,
                        room.name,
                        room.description.as_deref().unwrap_or("-")
                    );
                }
            }
        }
        RoomCommands::Create {
            name,
            description,
            parent,
        } => {
            let mut room = Room::new(&name);
            if let Some(desc) = description {
                room = room.with_description(desc);
            }
            if let Some(parent_id) = parent {
                let parent_uuid = uuid::Uuid::parse_str(&parent_id)?;
                room = room.with_parent(parent_uuid);
            }
            store.create_room(&room)?;
            println!("Created room: {} ({})", name, room.id);
        }
        RoomCommands::Delete { room } => {
            let room_id = find_room_id(store, &room)?;
            store.delete_room(room_id)?;
            println!("Deleted room: {}", room_id);
        }
    }
    Ok(())
}

fn handle_note_command(store: &Store, action: NoteCommands) -> anyhow::Result<()> {
    match action {
        NoteCommands::List { room } => {
            let room_id = find_room_id(store, &room)?;
            let notes = store.list_notes_in_room(room_id)?;
            if notes.is_empty() {
                println!("No notes in this room. Create one with: mm note create <room> <title>");
            } else {
                println!("{:<36}  {:<8}  {:<20}", "ID", "TYPE", "TITLE");
                println!("{}", "-".repeat(70));
                for note in notes {
                    println!("{:<36}  {:<8}  {}", note.id, note.note_type, note.title);
                }
            }
        }
        NoteCommands::Create {
            room,
            title,
            note_type,
            content,
        } => {
            let room_id = find_room_id(store, &room)?;
            let nt: NoteType = note_type.parse().map_err(|e: String| anyhow::anyhow!(e))?;
            let mut note = Note::new(room_id, &title, nt);
            if let Some(c) = content {
                note = note.with_content(c);
            }
            if nt == NoteType::Task {
                note = note.with_status(Status::Active);
            }
            store.create_note(&note)?;
            println!("Created note: {} ({})", title, note.id);
        }
        NoteCommands::Show { id } => {
            let note_id = uuid::Uuid::parse_str(&id)?;
            match store.get_note(note_id)? {
                Some(note) => {
                    println!("Title: {}", note.title);
                    println!("Type: {}", note.note_type);
                    if let Some(status) = note.status {
                        println!("Status: {}", status);
                    }
                    println!("Room: {}", note.room_id);
                    println!("Created: {}", note.created_at);
                    println!("Updated: {}", note.updated_at);
                    println!("\n{}", note.content);
                }
                None => {
                    println!("Note not found: {}", id);
                }
            }
        }
        NoteCommands::Delete { id } => {
            let note_id = uuid::Uuid::parse_str(&id)?;
            store.delete_note(note_id)?;
            println!("Deleted note: {}", note_id);
        }
    }
    Ok(())
}

fn handle_search(store: &Store, query: &str) -> anyhow::Result<()> {
    let notes = store.search_notes(query)?;
    if notes.is_empty() {
        println!("No notes found matching: {}", query);
    } else {
        println!("Found {} note(s):", notes.len());
        println!("{:<36}  {:<8}  {:<20}", "ID", "TYPE", "TITLE");
        println!("{}", "-".repeat(70));
        for note in notes {
            println!("{:<36}  {:<8}  {}", note.id, note.note_type, note.title);
        }
    }
    Ok(())
}

fn handle_article_command(store: &Store, action: ArticleCommands, db_path: &PathBuf) -> anyhow::Result<()> {
    match action {
        ArticleCommands::Review => {
            handle_review_dashboard(store, db_path)?;
        }
        ArticleCommands::Add { url, room } => {
            // Check if article already exists
            if store.get_article_by_url(&url)?.is_some() {
                anyhow::bail!("Article already exists: {}", url);
            }

            // Call Python to extract article content
            println!("Fetching article from {}...", url);
            let output = Command::new("python")
                .args(["-m", "minmind.cli", "extract", &url])
                .current_dir(find_python_dir()?)
                .output()?;

            if !output.status.success() {
                let stderr = String::from_utf8_lossy(&output.stderr);
                anyhow::bail!("Failed to extract article: {}", stderr);
            }

            // Parse the JSON output
            let json: serde_json::Value = serde_json::from_slice(&output.stdout)?;
            
            let title = json["title"].as_str().unwrap_or("Untitled");
            let content = json["content"].as_str().unwrap_or("");
            
            let mut article = Article::new(&url, title, content);
            
            // Set room if provided
            if let Some(room_name) = room {
                let room_id = find_room_id(store, &room_name)?;
                article = article.with_room(room_id);
            }

            // Parse metadata if available
            if let Some(metadata) = json.get("metadata") {
                let mut source_metadata = minmind_core::SourceMetadata::default();
                if let Some(author) = metadata["author"].as_str() {
                    source_metadata.author = Some(author.to_string());
                }
                if let Some(site) = metadata["site_name"].as_str() {
                    source_metadata.site_name = Some(site.to_string());
                }
                if let Some(desc) = metadata["description"].as_str() {
                    source_metadata.description = Some(desc.to_string());
                }
                article = article.with_metadata(source_metadata);
            }

            store.create_article(&article)?;
            println!("Added article: {} ({})", title, article.id);
        }
        ArticleCommands::List { status } => {
            let articles = match Option::<ArticleStatus>::from(status) {
                Some(s) => store.list_articles_by_status(s)?,
                None => store.list_articles()?,
            };

            if articles.is_empty() {
                println!("No articles found. Add one with: mm article add <url>");
            } else {
                println!("{:<12}  {:<12}  {}", "ID", "STATUS", "TITLE");
                println!("{}", "-".repeat(80));
                for article in articles {
                    // Show short ID for easier typing
                    let short_id = &article.id.to_string()[..8];
                    let title = if article.title.len() > 50 {
                        format!("{}...", &article.title[..47])
                    } else {
                        article.title.clone()
                    };
                    println!("{:<12}  {:<12}  {}", short_id, article.status, title);
                }
            }
        }
        ArticleCommands::Show { id } => {
            let article = find_article(store, &id)?;
            println!("Title: {}", article.title);
            println!("URL: {}", article.url);
            println!("Status: {}", article.status);
            println!("ID: {}", article.id);
            if let Some(room_id) = article.room_id {
                if let Some(room) = store.get_room(room_id)? {
                    println!("Room: {}", room.name);
                }
            }
            println!("Created: {}", article.created_at);
            
            if let Some(summary) = &article.summary {
                println!("\n--- Summary ---\n");
                println!("{}", summary);
            }
            
            println!("\n--- Content (first 500 chars) ---\n");
            let preview = if article.raw_content.len() > 500 {
                format!("{}...", &article.raw_content[..500])
            } else {
                article.raw_content.clone()
            };
            println!("{}", preview);
        }
        ArticleCommands::Summarize { id, provider } => {
            let mut article = find_article(store, &id)?;
            
            if article.summary.is_some() {
                println!("Article already has a summary. Regenerating...");
            }

            // Get the active summary config
            let config = store.get_active_summary_config(article.room_id)?;
            let prompt = config.map(|c| c.system_prompt).unwrap_or_else(|| DEFAULT_SUMMARY_PROMPT.to_string());

            println!("Summarizing with {}...", provider);
            
            // Call Python to summarize
            let output = Command::new("python")
                .args([
                    "-m", "minmind.cli", 
                    "summarize",
                    "--provider", &provider,
                    "--prompt", &prompt,
                    &article.id.to_string(),
                ])
                .current_dir(find_python_dir()?)
                .env("MINMIND_DB", db_path)
                .output()?;

            if !output.status.success() {
                let stderr = String::from_utf8_lossy(&output.stderr);
                anyhow::bail!("Failed to summarize article: {}", stderr);
            }

            let result: serde_json::Value = serde_json::from_slice(&output.stdout)?;
            let summary = result["summary"].as_str().unwrap_or("");
            
            article.set_summary(summary);
            store.update_article(&article)?;

            println!("\n--- Summary ---\n");
            println!("{}", summary);
        }
        ArticleCommands::Approve { id, room } => {
            let mut article = find_article(store, &id)?;
            
            // Determine target room
            let target_room_id = if let Some(room_name) = room {
                find_room_id(store, &room_name)?
            } else if let Some(rid) = article.room_id {
                rid
            } else {
                anyhow::bail!("No room specified. Use --room or assign article to a room first.");
            };

            // Create a note from the article
            let content = if let Some(summary) = &article.summary {
                format!(
                    "## Summary\n\n{}\n\n## Source\n\n{}\n\n## Full Content\n\n{}",
                    summary, article.url, article.raw_content
                )
            } else {
                format!(
                    "## Source\n\n{}\n\n## Content\n\n{}",
                    article.url, article.raw_content
                )
            };

            let note = Note::new(target_room_id, &article.title, NoteType::Reference)
                .with_content(content);
            store.create_note(&note)?;

            article.mark_reviewed();
            store.update_article(&article)?;

            println!("Approved article and created note: {}", note.id);
        }
        ArticleCommands::Archive { id } => {
            let mut article = find_article(store, &id)?;
            article.archive();
            store.update_article(&article)?;
            println!("Archived article: {}", article.title);
        }
        ArticleCommands::Delete { id } => {
            let article = find_article(store, &id)?;
            store.delete_article(article.id)?;
            println!("Deleted article: {}", article.title);
        }
    }
    Ok(())
}

fn handle_review_dashboard(store: &Store, db_path: &PathBuf) -> anyhow::Result<()> {
    use std::io::{self, Write};

    println!("\n╔══════════════════════════════════════════════════════════════╗");
    println!("║           MinMind Article Review Dashboard                    ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");

    loop {
        // Get articles ready for review (summarized or pending)
        let mut articles: Vec<_> = store.list_articles_by_status(ArticleStatus::Summarized)?;
        let pending = store.list_articles_by_status(ArticleStatus::Pending)?;
        
        let summarized_count = articles.len();
        let pending_count = pending.len();
        
        articles.extend(pending);
        
        if articles.is_empty() {
            println!("No articles to review. Add some with: mm article add <url>");
            break;
        }

        println!("┌────────────────────────────────────────────────────────────────┐");
        println!("│ {} summarized, {} pending review                              │", 
            summarized_count, pending_count);
        println!("└────────────────────────────────────────────────────────────────┘\n");

        // Show article list
        for (i, article) in articles.iter().enumerate() {
            let status_icon = match article.status {
                ArticleStatus::Pending => "⏳",
                ArticleStatus::Summarized => "📝",
                _ => "  ",
            };
            let title = if article.title.len() > 50 {
                format!("{}...", &article.title[..47])
            } else {
                article.title.clone()
            };
            println!("  {} [{}] {}", status_icon, i + 1, title);
        }

        println!("\n  Commands:");
        println!("    [n]    - View article n (e.g., '1' for first article)");
        println!("    [s n]  - Summarize article n");
        println!("    [a n]  - Approve article n (creates Note)");
        println!("    [x n]  - Archive article n");
        println!("    [q]    - Quit dashboard\n");

        print!("  > ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim().to_lowercase();

        if input == "q" || input == "quit" {
            println!("\nGoodbye!\n");
            break;
        }

        // Parse command
        let parts: Vec<&str> = input.split_whitespace().collect();
        
        match parts.as_slice() {
            // View article by number
            [num] if num.parse::<usize>().is_ok() => {
                let idx = num.parse::<usize>().unwrap();
                if idx == 0 || idx > articles.len() {
                    println!("\n  ⚠ Invalid article number\n");
                    continue;
                }
                let article = &articles[idx - 1];
                show_article_detail(article, store)?;
            }
            // Summarize
            ["s", num] | ["summarize", num] => {
                let idx = num.parse::<usize>().unwrap_or(0);
                if idx == 0 || idx > articles.len() {
                    println!("\n  ⚠ Invalid article number\n");
                    continue;
                }
                let article = &articles[idx - 1];
                println!("\n  Summarizing '{}'...", article.title);
                
                // Get summary config
                let config = store.get_active_summary_config(article.room_id)?;
                let prompt = config.map(|c| c.system_prompt).unwrap_or_else(|| DEFAULT_SUMMARY_PROMPT.to_string());

                let output = Command::new("python")
                    .args([
                        "-m", "minmind.cli",
                        "summarize",
                        "--provider", "anthropic",
                        "--prompt", &prompt,
                        &article.id.to_string(),
                    ])
                    .current_dir(find_python_dir()?)
                    .env("MINMIND_DB", db_path)
                    .output()?;

                if output.status.success() {
                    let result: serde_json::Value = serde_json::from_slice(&output.stdout)?;
                    let summary = result["summary"].as_str().unwrap_or("");
                    
                    let mut updated_article = article.clone();
                    updated_article.set_summary(summary);
                    store.update_article(&updated_article)?;
                    
                    println!("\n  ✓ Summary generated!\n");
                    println!("  ─────────────────────────────────────────────");
                    for line in summary.lines().take(10) {
                        println!("  {}", line);
                    }
                    if summary.lines().count() > 10 {
                        println!("  ...(truncated)");
                    }
                    println!("  ─────────────────────────────────────────────\n");
                } else {
                    let stderr = String::from_utf8_lossy(&output.stderr);
                    println!("\n  ✗ Failed to summarize: {}\n", stderr);
                }
            }
            // Approve
            ["a", num] | ["approve", num] => {
                let idx = num.parse::<usize>().unwrap_or(0);
                if idx == 0 || idx > articles.len() {
                    println!("\n  ⚠ Invalid article number\n");
                    continue;
                }
                let article = &articles[idx - 1];
                
                // Check if article has a room
                let room_id = if let Some(rid) = article.room_id {
                    rid
                } else {
                    // Ask for room
                    let rooms = store.list_rooms()?;
                    if rooms.is_empty() {
                        println!("\n  ⚠ No rooms available. Create one first: mm room create <name>\n");
                        continue;
                    }
                    println!("\n  Select a room for this note:");
                    for (i, room) in rooms.iter().enumerate() {
                        println!("    [{}] {}", i + 1, room.name);
                    }
                    print!("  Room number: ");
                    io::stdout().flush()?;
                    
                    let mut room_input = String::new();
                    io::stdin().read_line(&mut room_input)?;
                    let room_idx = room_input.trim().parse::<usize>().unwrap_or(0);
                    
                    if room_idx == 0 || room_idx > rooms.len() {
                        println!("\n  ⚠ Invalid room number\n");
                        continue;
                    }
                    rooms[room_idx - 1].id
                };

                // Create note from article
                let content = if let Some(summary) = &article.summary {
                    format!(
                        "## Summary\n\n{}\n\n## Source\n\n{}\n\n## Full Content\n\n{}",
                        summary, article.url, article.raw_content
                    )
                } else {
                    format!(
                        "## Source\n\n{}\n\n## Content\n\n{}",
                        article.url, article.raw_content
                    )
                };

                let note = Note::new(room_id, &article.title, NoteType::Reference)
                    .with_content(content);
                store.create_note(&note)?;

                let mut updated_article = article.clone();
                updated_article.mark_reviewed();
                store.update_article(&updated_article)?;

                println!("\n  ✓ Approved! Created note: {}\n", &note.id.to_string()[..8]);
            }
            // Archive
            ["x", num] | ["archive", num] => {
                let idx = num.parse::<usize>().unwrap_or(0);
                if idx == 0 || idx > articles.len() {
                    println!("\n  ⚠ Invalid article number\n");
                    continue;
                }
                let article = &articles[idx - 1];
                
                let mut updated_article = article.clone();
                updated_article.archive();
                store.update_article(&updated_article)?;
                
                println!("\n  ✓ Archived: {}\n", article.title);
            }
            _ => {
                println!("\n  ⚠ Unknown command. Try 'q' to quit.\n");
            }
        }
    }

    Ok(())
}

fn show_article_detail(article: &Article, store: &Store) -> anyhow::Result<()> {
    println!("\n┌────────────────────────────────────────────────────────────────┐");
    println!("│ {}", truncate_string(&article.title, 60));
    println!("├────────────────────────────────────────────────────────────────┤");
    println!("│ URL: {}", truncate_string(&article.url, 55));
    println!("│ Status: {:?}", article.status);
    if let Some(room_id) = article.room_id {
        if let Some(room) = store.get_room(room_id)? {
            println!("│ Room: {}", room.name);
        }
    }
    println!("└────────────────────────────────────────────────────────────────┘");
    
    if let Some(summary) = &article.summary {
        println!("\n  📝 Summary:");
        println!("  ─────────────────────────────────────────────");
        for line in summary.lines() {
            println!("  {}", line);
        }
        println!("  ─────────────────────────────────────────────");
    } else {
        println!("\n  ⏳ No summary yet. Use 's <n>' to summarize.");
    }
    
    println!("\n  📄 Content Preview (first 500 chars):");
    println!("  ─────────────────────────────────────────────");
    let preview = if article.raw_content.len() > 500 {
        format!("{}...", &article.raw_content[..500])
    } else {
        article.raw_content.clone()
    };
    for line in preview.lines().take(15) {
        println!("  {}", line);
    }
    println!("  ─────────────────────────────────────────────\n");
    
    Ok(())
}

fn truncate_string(s: &str, max_len: usize) -> String {
    if s.len() > max_len {
        format!("{}...", &s[..max_len - 3])
    } else {
        s.to_string()
    }
}

fn handle_todo_command(store: &Store, action: TodoCommands) -> anyhow::Result<()> {
    match action {
        TodoCommands::List { status, plan } => {
            let actions = match (Option::<ActionStatus>::from(status), plan) {
                (Some(s), Some(p)) => {
                    // Filter by both status and plan
                    store
                        .list_user_actions_by_source(&p)?
                        .into_iter()
                        .filter(|a| a.status == s)
                        .collect()
                }
                (Some(s), None) => store.list_user_actions_by_status(s)?,
                (None, Some(p)) => store.list_user_actions_by_source(&p)?,
                (None, None) => store.list_user_actions()?,
            };

            if actions.is_empty() {
                println!("No todos found. Sync from plans with: mm todo sync");
            } else {
                println!(
                    "{:<12}  {:<12}  {:<30}  {}",
                    "ID", "STATUS", "SOURCE", "TITLE"
                );
                println!("{}", "-".repeat(90));
                for action in actions {
                    let short_id = &action.id.to_string()[..8];
                    let source = action
                        .source_file
                        .as_deref()
                        .unwrap_or("-")
                        .trim_start_matches("plans/");
                    let source = if source.len() > 28 {
                        format!("{}...", &source[..25])
                    } else {
                        source.to_string()
                    };
                    let title = if action.title.len() > 40 {
                        format!("{}...", &action.title[..37])
                    } else {
                        action.title.clone()
                    };
                    println!(
                        "{:<12}  {:<12}  {:<30}  {}",
                        short_id, action.status, source, title
                    );
                }
            }
        }
        TodoCommands::Sync { dir } => {
            let plans_dir = expand_path(&dir);

            if !plans_dir.exists() {
                anyhow::bail!("Plans directory not found: {}", plans_dir.display());
            }

            println!("Scanning {} for [USER] markers...", plans_dir.display());

            let mut total_found = 0;
            let mut total_new = 0;
            let mut total_updated = 0;

            for entry in std::fs::read_dir(&plans_dir)? {
                let entry = entry?;
                let path = entry.path();

                if !path.is_file() || path.extension().map_or(true, |ext| ext != "md") {
                    continue;
                }

                let content = std::fs::read_to_string(&path)?;
                let source_file = path.to_string_lossy().to_string();
                let result = parse_plan_content(&content, &source_file);

                if result.actions.is_empty() {
                    continue;
                }

                println!(
                    "  {} - {} action(s)",
                    path.file_name().unwrap_or_default().to_string_lossy(),
                    result.actions.len()
                );
                total_found += result.actions.len();

                // Get existing actions for this file
                let existing = store.list_user_actions_by_source(&source_file)?;
                let existing_map: std::collections::HashMap<u32, UserAction> = existing
                    .into_iter()
                    .filter_map(|a| a.line_number.map(|ln| (ln, a)))
                    .collect();

                for parsed in result.actions {
                    if let Some(existing_action) = existing_map.get(&parsed.line_number) {
                        // Update if title or status changed (but don't override completed status)
                        if existing_action.title != parsed.title
                            || (existing_action.status != parsed.status
                                && !existing_action.is_done())
                        {
                            let mut updated = existing_action.clone();
                            updated.title = parsed.title;
                            if !updated.is_done() {
                                updated.status = parsed.status;
                            }
                            store.update_user_action(&updated)?;
                            total_updated += 1;
                        }
                    } else {
                        // Create new action
                        let mut action = UserAction::from_plan(
                            parsed.title,
                            source_file.clone(),
                            parsed.line_number,
                        );
                        action.status = parsed.status;
                        store.create_user_action(&action)?;
                        total_new += 1;
                    }
                }
            }

            println!("\nSync complete:");
            println!("  Found: {} action(s)", total_found);
            println!("  New: {} action(s)", total_new);
            println!("  Updated: {} action(s)", total_updated);
        }
        TodoCommands::Complete { id } => {
            let mut action = find_user_action(store, &id)?;
            action.complete();
            store.update_user_action(&action)?;

            // Update the source file if it exists
            if let (Some(source_file), Some(line_number)) =
                (&action.source_file, action.line_number)
            {
                update_plan_file(source_file, line_number, ActionStatus::Completed)?;
            }

            println!("Completed: {}", action.title);
        }
        TodoCommands::Start { id } => {
            let mut action = find_user_action(store, &id)?;
            action.start();
            store.update_user_action(&action)?;

            // Update the source file if it exists
            if let (Some(source_file), Some(line_number)) =
                (&action.source_file, action.line_number)
            {
                update_plan_file(source_file, line_number, ActionStatus::InProgress)?;
            }

            println!("Started: {}", action.title);
        }
        TodoCommands::Skip { id } => {
            let mut action = find_user_action(store, &id)?;
            action.skip();
            store.update_user_action(&action)?;

            // Update the source file if it exists
            if let (Some(source_file), Some(line_number)) =
                (&action.source_file, action.line_number)
            {
                update_plan_file(source_file, line_number, ActionStatus::Skipped)?;
            }

            println!("Skipped: {}", action.title);
        }
        TodoCommands::Add { title, plan } => {
            let action = if let Some(plan_file) = plan {
                // Associate with a plan file but don't add to the file itself
                let mut a = UserAction::new(&title);
                a.source_file = Some(plan_file);
                a
            } else {
                UserAction::new(&title)
            };
            store.create_user_action(&action)?;
            println!("Added todo: {} ({})", title, &action.id.to_string()[..8]);
        }
    }
    Ok(())
}

/// Find a user action by ID or short ID
fn find_user_action(store: &Store, id: &str) -> anyhow::Result<UserAction> {
    // Try full UUID first
    if let Ok(uuid) = uuid::Uuid::parse_str(id) {
        if let Some(action) = store.get_user_action(uuid)? {
            return Ok(action);
        }
    }

    // Try short ID match
    let actions = store.list_user_actions()?;
    for action in actions {
        if action.id.to_string().starts_with(id) {
            return Ok(action);
        }
    }

    anyhow::bail!("Todo not found: {}", id)
}

/// Update a plan file's marker on a specific line
fn update_plan_file(source_file: &str, line_number: u32, new_status: ActionStatus) -> anyhow::Result<()> {
    let path = std::path::Path::new(source_file);
    if !path.exists() {
        // File doesn't exist, skip update
        return Ok(());
    }

    let content = std::fs::read_to_string(path)?;
    let updated = update_plan_markers(&content, &[(line_number, new_status)]);
    std::fs::write(path, updated)?;
    Ok(())
}

fn handle_config_command(store: &Store, action: ConfigCommands) -> anyhow::Result<()> {
    match action {
        ConfigCommands::List => {
            let configs = store.list_summary_configs()?;
            if configs.is_empty() {
                println!("No summary configurations. Using default prompt.");
                println!("Create one with: mm config create <name>");
            } else {
                println!("{:<12}  {:<15}  {:<10}  {}", "ID", "NAME", "SCOPE", "ACTIVE");
                println!("{}", "-".repeat(60));
                for config in configs {
                    let short_id = &config.id.to_string()[..8];
                    let scope = if config.is_global() {
                        "global".to_string()
                    } else if let Some(room_id) = config.room_id {
                        if let Ok(Some(room)) = store.get_room(room_id) {
                            room.name
                        } else {
                            "unknown".to_string()
                        }
                    } else {
                        "unknown".to_string()
                    };
                    let active = if config.active { "yes" } else { "no" };
                    println!("{:<12}  {:<15}  {:<10}  {}", short_id, config.name, scope, active);
                }
            }
        }
        ConfigCommands::Create { name, prompt, room } => {
            let prompt = prompt.unwrap_or_else(|| DEFAULT_SUMMARY_PROMPT.to_string());
            
            let config = if let Some(room_name) = room {
                let room_id = find_room_id(store, &room_name)?;
                SummaryConfig::new_for_room(&name, &prompt, room_id)
            } else {
                SummaryConfig::new_global(&name, &prompt)
            };

            store.create_summary_config(&config)?;
            println!("Created summary config: {} ({})", name, &config.id.to_string()[..8]);
        }
        ConfigCommands::Default => {
            println!("Default summary prompt:\n");
            println!("{}", DEFAULT_SUMMARY_PROMPT);
        }
        ConfigCommands::Delete { id } => {
            let config_id = uuid::Uuid::parse_str(&id)
                .or_else(|_| find_config_by_short_id(store, &id))?;
            store.delete_summary_config(config_id)?;
            println!("Deleted summary config: {}", id);
        }
    }
    Ok(())
}

fn handle_image_command(action: ImageCommands) -> anyhow::Result<()> {
    match action {
        ImageCommands::Optimize {
            input,
            output,
            quality,
            format,
        } => {
            let input_path = PathBuf::from(&input);
            if !input_path.exists() {
                anyhow::bail!("Input file does not exist: {}", input);
            }

            // Generate output path if not provided
            let output_path = if let Some(out) = output {
                PathBuf::from(out)
            } else {
                // Default to input_optimized.jpg or input_optimized.png
                let stem = input_path.file_stem().unwrap_or_default();
                let ext = format.as_deref().unwrap_or("jpg");
                let new_name = format!("{}_optimized.{}", stem.to_string_lossy(), ext);
                input_path.with_file_name(new_name)
            };

            crate::image::optimize_image(&input_path, &output_path, quality, format)?;
        }
        ImageCommands::Info { path } => {
            let path = PathBuf::from(&path);
            if !path.exists() {
                anyhow::bail!("File does not exist: {}", path.display());
            }
            crate::image::get_image_info(&path)?;
        }
    }
    Ok(())
}

/// Find a room by ID or name
fn find_room_id(store: &Store, room: &str) -> anyhow::Result<uuid::Uuid> {
    // Try to parse as UUID first
    if let Ok(id) = uuid::Uuid::parse_str(room) {
        return Ok(id);
    }

    // Otherwise, search by name
    let rooms = store.list_rooms()?;
    for r in rooms {
        if r.name.eq_ignore_ascii_case(room) {
            return Ok(r.id);
        }
    }

    anyhow::bail!("Room not found: {}", room)
}

/// Find an article by ID or short ID
fn find_article(store: &Store, id: &str) -> anyhow::Result<Article> {
    // Try full UUID first
    if let Ok(uuid) = uuid::Uuid::parse_str(id) {
        if let Some(article) = store.get_article(uuid)? {
            return Ok(article);
        }
    }

    // Try short ID match
    let articles = store.list_articles()?;
    for article in articles {
        if article.id.to_string().starts_with(id) {
            return Ok(article);
        }
    }

    anyhow::bail!("Article not found: {}", id)
}

/// Find a config by short ID
fn find_config_by_short_id(store: &Store, id: &str) -> anyhow::Result<uuid::Uuid> {
    let configs = store.list_summary_configs()?;
    for config in configs {
        if config.id.to_string().starts_with(id) {
            return Ok(config.id);
        }
    }
    anyhow::bail!("Config not found: {}", id)
}

/// Find the Python package directory
fn find_python_dir() -> anyhow::Result<PathBuf> {
    // Try relative to executable
    if let Ok(exe) = std::env::current_exe() {
        let project_root = exe
            .parent()
            .and_then(|p| p.parent())
            .and_then(|p| p.parent())
            .and_then(|p| p.parent());
        
        if let Some(root) = project_root {
            let python_dir = root.join("python");
            if python_dir.exists() {
                return Ok(python_dir);
            }
        }
    }

    // Try current directory
    let cwd = std::env::current_dir()?;
    let python_dir = cwd.join("python");
    if python_dir.exists() {
        return Ok(python_dir);
    }

    // Try MINMIND_PYTHON_DIR env var
    if let Ok(dir) = std::env::var("MINMIND_PYTHON_DIR") {
        let path = PathBuf::from(dir);
        if path.exists() {
            return Ok(path);
        }
    }

    anyhow::bail!("Could not find Python directory. Set MINMIND_PYTHON_DIR environment variable.")
}

/// Expand ~ in paths
fn expand_path(path: &str) -> PathBuf {
    if path.starts_with("~/") {
        if let Some(home) = dirs::home_dir() {
            return home.join(&path[2..]);
        }
    }
    PathBuf::from(path)
}
