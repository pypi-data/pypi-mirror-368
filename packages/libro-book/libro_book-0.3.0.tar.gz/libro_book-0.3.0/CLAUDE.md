# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Libro is a command-line tool for tracking personal reading history. It stores book and review data in a local SQLite database and provides various reporting and display features. The application is built with Python 3.10+ and uses Rich for terminal formatting.

## Commands

### Development Commands
- `just install` - Install dependencies using uv
- `just lint` - Run ruff linting on src/libro/
- `just clean` - Remove build artifacts and Python cache files
- `just build` - Clean, lint, install, and build the package
- `just run <args>` - Run the CLI application with arguments
- `uv run libro <args>` - Alternative way to run the application

### Testing and Quality
- `ruff check src/libro/` - Lint the codebase (configured in pyproject.toml)

### Build and Release
- `just publish` - Build and publish to PyPI as `libro-book`
- `py -m build` - Build the package
- `py -m twine upload dist/*` - Upload to PyPI

## Architecture

### Core Structure
- `src/libro/main.py` - Entry point with CLI argument parsing and command routing
- `src/libro/models.py` - Data classes for Book, Review, BookReview, ReadingList, and ReadingListBook
- `src/libro/config.py` - Configuration and argument parsing
- `src/libro/actions/` - Command implementations:
  - `db.py` - Database initialization and migration
  - `show.py` - Display books and reviews
  - `report.py` - Generate reading reports and statistics
  - `modify.py` - Add and edit books/reviews
  - `importer.py` - Import from external sources (Goodreads, CSV)
  - `lists.py` - Reading list management operations

### Database Schema
- `books` table: id, title, author, pages, pub_year, genre
- `reviews` table: id, book_id (FK), date_read, rating, review
- `reading_lists` table: id, name, description, created_date
- `reading_list_books` table: id, list_id (FK), book_id (FK), added_date, priority

### Key Design Patterns
- Uses dataclasses for clean data modeling
- SQLite with row factory for named column access
- Command pattern for CLI actions
- Rich library for terminal formatting and tables

### Database Location Priority
1. `--db` command-line flag
2. `libro.db` in current directory
3. `LIBRO_DB` environment variable
4. Platform-specific data directory

### Package Management
- Uses `uv` for dependency management and virtual environments
- Built with `hatchling` build system
- Published to PyPI as `libro-book` (not `libro` due to naming conflicts)
- Configured for Python 3.10+ compatibility

## Reading Lists Feature

### Overview
Reading lists allow users to organize books into curated collections (e.g., "To Read", "Sci-Fi Classics", "Summer 2025"). Each list can contain multiple books with progress tracking.

### Key Features
- Create, edit, and delete reading lists with names and descriptions
- Add books to lists (creates book if it doesn't exist)
- Remove books from lists (preserves book in database)
- View list contents with read/unread status and progress indicators
- Import books from CSV files directly into lists
- Track reading statistics and completion percentages
- Priority system for ordering books within lists

### CLI Commands
- `libro list` - Show all reading lists with summary stats
- `libro list create <name> [--description]` - Create new reading list
- `libro list show <id>` - Display specific list contents
- `libro list add <id>` - Add book to list (interactive prompts)
- `libro list remove <id> <book_id>` - Remove book from list
- `libro list edit <id> [--name] [--description]` - Edit list details
- `libro list delete <id>` - Delete entire list (preserves books)
- `libro list stats [id]` - Show statistics (all lists or specific list)
- `libro list import <csv_file> [--id|--name] [--description]` - Import CSV to list

### Database Integration
- Automatic database migration adds reading list tables to existing databases
- Foreign key constraints ensure data integrity
- Cascade deletes remove list associations when lists are deleted
- Junction table design allows books to belong to multiple lists

### Data Sources
The `/data/` directory contains JSON files with book metadata for fiction and nonfiction books, used for testing or seeding data. Ignore the `/data/` directory.