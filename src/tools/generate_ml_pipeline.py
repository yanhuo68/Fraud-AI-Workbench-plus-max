import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure
fig, ax = plt.subplots(figsize=(12, 20))

# Define nodes
nodes = [
    {"name": "Data Collection", "color": "#4A90E2", "y": 1},
    {"name": "Data Preprocessing", "color": "#17A2B8", "y": 2},
    {"name": "Feature Engineering", "color": "#6F42C1", "y": 3},
    {"name": "Model Selection", "color": "#FD7E14", "y": 4},
    {"name": "Training & Validation", "color": "#28A745", "y": 5},
    {"name": "Evaluation", "color": "#DC3545", "y": 6},
    {"name": "Deployment", "color": "#0066CC", "y": 7},
    {"name": "Monitoring & Maintenance", "color": "#6C757D", "y": 8}
]

# Add nodes
for node in nodes:
    rect = patches.FancyBboxPatch((0.1, node["y"]), 0.8, 0.35, 
                                 boxstyle="round,pad=0.1",
                                 facecolor=node["color"],
                                 edgecolor='black')
    ax.add_patch(rect)
    ax.text(0.5, node["y"]+0.175, node["name"], 
            ha='center', va='center', fontsize=12, 
            fontweight='bold', color='white')

# Add arrows
for i in range(len(nodes)-1):
    ax.arrow(0.5, nodes[i]["y"]+0.35, 0, 0.4,
            head_width=0.05, head_length=0.05, fc='black')

ax.set_xlim(0, 1)
ax.set_ylim(0, 11)
ax.axis('off')
plt.savefig('ml_pipeline.jpg', dpi=300, bbox_inches='tight')
plt.show()
