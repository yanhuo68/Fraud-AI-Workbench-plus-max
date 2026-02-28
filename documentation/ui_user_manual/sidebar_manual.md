# User Manual: Sidebar

The command center for global settings and tools.

## Key Features
1.  **API Keys (Optional)**: If you need to override the system keys, enter your OpenAI/Anthropic keys here.
2.  **System Tools (Red Buttons)**: Critical system actions are highlighted in **Red** for visibility.
    *   **🔄 Rebuild KB Index**: Click this if KB RAG is not finding new documents you added.
    *   **🕸️ Rebuild Graph**: Click this to refresh the knowledge graph.
    *   **🗑️ Clean DB**: **WARNING**: This deletes all uploaded SQL data. Use this to start a fresh session.
    *   **🧹 Clean KB**: **WARNING**: This deletes the Vector Store and Graph Store. Use this if the AI is getting confused by old data.
3.  **Fraud Guidelines**:
    *   **Category Filter**: Filter guidelines by *Fraud Risk*, *Fraud Detection*, or view *All*.
    *   **View**: Select a document to view it directly in the main application area.
4.  **Help & Documentation**:
    *   Access user manuals and design docs directly from the sidebar.

## Navigation
The sidebar background is a distinct **Dark Gray** to separate control functions from the main workspace. Use the **Bold** tabs at the top of the main screen to switch between features (Upload, ML, RAG, etc.).
