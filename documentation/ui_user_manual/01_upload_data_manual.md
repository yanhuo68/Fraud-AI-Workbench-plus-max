# User Manual: Upload Data

This tab is your starting point. You must upload or load data here before using most other tabs.

## Quick Start (Demo Data)
1.  Look for the **"Quick Start: Load Demo Dataset"** section.
2.  Select a file from the dropdown (e.g., `fraud_data.csv`).
3.  Click the **📥 Load Demo** button (Light Blue).
4.  Wait for the green success message. This will automatically:
    *   Load the data for analysis.
    *   Create a database table.
    *   Detect Primary and Foreign Keys strategies.

## Modifying the Database
To create relationships between tables (Critical for SQL RAG and ERD):
1.  Scroll to **"Load Demo SQL Schema"**.
2.  Select SQL files (like `create_tables.sql` and `insert_data.sql`).
3.  Click **⚙️ Execute Demo SQL** (Light Blue).
4.  This builds a richer database with multiple connected tables.

## Managing Fraud & Risk Guidelines
New in this version, you can manage the text-based knowledge base for RAG:

### 🎯 Load Demo Guidelines
1.  Locate the "**🎯 Load Demo Guidelines**" section.
2.  Select standard fraud frameworks (e.g., `fraud-risk-kri-library.md`) from the list.
3.  Click **📥 Load Selected Guidelines** (Light Blue).
4.  The system will copy these to the `docs/` folder and effectively rebuilding the Knowledge Graph.

### 📂 Upload Risk Guidelines
1.  Scroll to "**📂 Upload Risk Guidelines**".
2.  Drag and drop your own internal policy documents (`.md` format).
3.  The system automatically indexes them into the Vector Store and updates the Graph.

## Uploading Your Own Data
1.  Drag and drop CSV files into the **"Upload Your Own CSV"** area.
2.  Click **Browse files** (Light Blue button) to select from your computer.
3.  The system will validate them and add them to the system.

## Troubleshooting
*   **Graph Visualization not showing?** Click "**Generate/Refresh Graph Visualization**" (Light Blue) at the bottom of the page.
*   **Database clean-up?** Use the **"Clean DB"** button (Red) in the sidebar if you want to start over.
