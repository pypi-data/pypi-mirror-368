"""Export functionality for graph visualizations."""

import json
from pathlib import Path
from typing import Dict, Optional

from gira.models import Ticket


class GraphExporter:
    """Export graph data to various formats."""

    @staticmethod
    def to_mermaid(
        graph: Dict,
        title: Optional[str] = None,
        include_status: bool = True
    ) -> str:
        """Export graph to Mermaid diagram format."""
        lines = ["graph TD"]

        if title:
            lines.append(f"    %% {title}")

        # Track all nodes to avoid duplicates
        nodes = set()

        def add_ticket_node(ticket: Ticket):
            """Add a ticket node to the graph."""
            if ticket.id not in nodes:
                nodes.add(ticket.id)
                status = f"[{ticket.status}]" if include_status else ""
                # Escape special characters in title
                title = ticket.title.replace('"', '\\"')
                lines.append(f'    {ticket.id}["{ticket.id}: {title}{status}"]')

        # Add main ticket
        if "ticket" in graph:
            add_ticket_node(graph["ticket"])

            # Add relationships
            if graph.get("blocks"):
                for blocked in graph["blocks"]:
                    add_ticket_node(blocked)
                    lines.append(f"    {graph['ticket'].id} -->|blocks| {blocked.id}")

            if graph.get("blocked_by"):
                for blocker in graph["blocked_by"]:
                    add_ticket_node(blocker)
                    lines.append(f"    {blocker.id} -->|blocks| {graph['ticket'].id}")

            if graph.get("parent"):
                add_ticket_node(graph["parent"])
                lines.append(f"    {graph['parent'].id} -->|parent| {graph['ticket'].id}")

            if graph.get("children"):
                for child in graph["children"]:
                    add_ticket_node(child)
                    lines.append(f"    {graph['ticket'].id} -->|parent| {child.id}")

        return "\n".join(lines)

    @staticmethod
    def to_dot(
        graph: Dict,
        title: Optional[str] = None,
        rankdir: str = "TB"
    ) -> str:
        """Export graph to Graphviz DOT format."""
        lines = ["digraph G {"]
        lines.append(f'    rankdir="{rankdir}";')
        lines.append('    node [shape=box, style="rounded,filled", fillcolor=lightblue];')

        if title:
            lines.append(f'    label="{title}";')
            lines.append('    labelloc="t";')

        # Track nodes
        nodes = set()

        def add_ticket_node(ticket: Ticket):
            """Add a ticket node with styling based on status."""
            if ticket.id not in nodes:
                nodes.add(ticket.id)
                # Status-based colors
                colors = {
                    "done": "#90EE90",      # Light green
                    "in_progress": "#87CEEB",  # Sky blue
                    "review": "#DDA0DD",    # Plum
                    "todo": "#FFD700",      # Gold
                    "backlog": "#D3D3D3"    # Light gray
                }
                color = colors.get(ticket.status.lower(), "#ADD8E6")

                # Escape quotes in title
                title = ticket.title.replace('"', '\\"')[:40]
                if len(ticket.title) > 40:
                    title += "..."

                lines.append(f'    "{ticket.id}" [label="{ticket.id}\\n{title}", fillcolor="{color}"];')

        # Add main ticket
        if "ticket" in graph:
            add_ticket_node(graph["ticket"])

            # Add relationships
            if graph.get("blocks"):
                for blocked in graph["blocks"]:
                    add_ticket_node(blocked)
                    lines.append(f'    "{graph["ticket"].id}" -> "{blocked.id}" [label="blocks", color=orange];')

            if graph.get("blocked_by"):
                for blocker in graph["blocked_by"]:
                    add_ticket_node(blocker)
                    lines.append(f'    "{blocker.id}" -> "{graph["ticket"].id}" [label="blocks", color=red];')

            if graph.get("parent"):
                add_ticket_node(graph["parent"])
                lines.append(f'    "{graph["parent"].id}" -> "{graph["ticket"].id}" [label="parent", color=green];')

            if graph.get("children"):
                for child in graph["children"]:
                    add_ticket_node(child)
                    lines.append(f'    "{graph["ticket"].id}" -> "{child.id}" [label="parent", color=blue];')

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def to_html(
        graph: Dict,
        title: Optional[str] = None,
        include_vis_js: bool = True
    ) -> str:
        """Export graph to interactive HTML using vis.js."""
        # Convert graph to vis.js format
        nodes = []
        edges = []
        node_ids = set()

        def add_node(ticket: Ticket, is_main: bool = False):
            """Add a node to the visualization."""
            if ticket.id not in node_ids:
                node_ids.add(ticket.id)

                # Status-based colors
                colors = {
                    "done": "#4CAF50",
                    "in_progress": "#2196F3",
                    "review": "#9C27B0",
                    "todo": "#FFC107",
                    "backlog": "#757575"
                }

                color = colors.get(ticket.status.lower(), "#2196F3")

                nodes.append({
                    "id": ticket.id,
                    "label": f"{ticket.id}\\n{ticket.title[:30]}{'...' if len(ticket.title) > 30 else ''}",
                    "color": color,
                    "font": {"color": "white"} if ticket.status == "done" else {},
                    "size": 30 if is_main else 25
                })

        # Process the graph
        if "ticket" in graph:
            main_ticket = graph["ticket"]
            add_node(main_ticket, is_main=True)

            # Add relationships
            edge_id = 0
            if graph.get("blocks"):
                for blocked in graph["blocks"]:
                    add_node(blocked)
                    edges.append({
                        "id": edge_id,
                        "from": main_ticket.id,
                        "to": blocked.id,
                        "label": "blocks",
                        "color": {"color": "#FFA500"},
                        "arrows": "to"
                    })
                    edge_id += 1

            if graph.get("blocked_by"):
                for blocker in graph["blocked_by"]:
                    add_node(blocker)
                    edges.append({
                        "id": edge_id,
                        "from": blocker.id,
                        "to": main_ticket.id,
                        "label": "blocks",
                        "color": {"color": "#FF0000"},
                        "arrows": "to"
                    })
                    edge_id += 1

        # Generate HTML
        html_title = title or "Gira Dependency Graph"

        vis_js_cdn = ""
        if include_vis_js:
            vis_js_cdn = '''
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://unpkg.com/vis-network/styles/vis-network.min.css" rel="stylesheet" type="text/css" />'''

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{html_title}</title>{vis_js_cdn}
    <style type="text/css">
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        #mynetwork {{
            width: 100%;
            height: 600px;
            border: 1px solid #ccc;
            background-color: white;
        }}
        .header {{
            margin-bottom: 20px;
        }}
        h1 {{
            color: #333;
            margin: 0 0 10px 0;
        }}
        .controls {{
            margin-bottom: 10px;
        }}
        button {{
            margin-right: 10px;
            padding: 5px 15px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{html_title}</h1>
        <div class="controls">
            <button onclick="network.fit()">Fit to Screen</button>
            <button onclick="network.setOptions({{physics: {{enabled: true}}}})">Enable Physics</button>
            <button onclick="network.setOptions({{physics: {{enabled: false}}}})">Disable Physics</button>
        </div>
    </div>
    <div id="mynetwork"></div>

    <script type="text/javascript">
        // Create nodes and edges
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});

        // Create a network
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        
        var options = {{
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based'
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }},
            nodes: {{
                shape: 'box',
                margin: 10,
                font: {{
                    size: 14,
                    face: 'Arial'
                }}
            }},
            edges: {{
                font: {{
                    size: 12,
                    align: 'middle'
                }},
                smooth: {{
                    type: 'cubicBezier',
                    forceDirection: 'none'
                }}
            }}
        }};
        
        var network = new vis.Network(container, data, options);
        
        // Add double-click event to open ticket details (customize URL as needed)
        network.on("doubleClick", function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                console.log("Double-clicked on ticket: " + nodeId);
                // You can customize this to open ticket details
                // window.open("/ticket/" + nodeId, "_blank");
            }}
        }});
    </script>
</body>
</html>"""

        return html

    @staticmethod
    def export_graph(
        graph: Dict,
        format: str,
        output_path: Optional[str] = None,
        title: Optional[str] = None
    ) -> Optional[str]:
        """Export graph to specified format and optionally save to file."""
        exporters = {
            "mermaid": GraphExporter.to_mermaid,
            "dot": GraphExporter.to_dot,
            "html": GraphExporter.to_html,
            "json": lambda g, t: json.dumps(GraphExporter._graph_to_json(g), indent=2)
        }

        if format not in exporters:
            raise ValueError(f"Unsupported format: {format}. Use one of: {', '.join(exporters.keys())}")

        # Generate output
        output = exporters[format](graph, title)

        # Save to file if path provided
        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output)
            return str(path.absolute())

        return output

    @staticmethod
    def _graph_to_json(graph: Dict) -> Dict:
        """Convert graph to JSON-serializable format."""
        def ticket_to_dict(t: Ticket) -> dict:
            return {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "type": t.type,
                "priority": t.priority,
                "assignee": t.assignee,
                "reporter": t.reporter,
                "description": t.description[:200] if t.description else None
            }

        result = {}

        if "ticket" in graph:
            result["ticket"] = ticket_to_dict(graph["ticket"])
            result["relationships"] = {}

            if graph.get("blocks"):
                result["relationships"]["blocks"] = [
                    ticket_to_dict(t) for t in graph["blocks"]
                ]

            if graph.get("blocked_by"):
                result["relationships"]["blocked_by"] = [
                    ticket_to_dict(t) for t in graph["blocked_by"]
                ]

            if graph.get("parent"):
                result["relationships"]["parent"] = ticket_to_dict(graph["parent"])

            if graph.get("children"):
                result["relationships"]["children"] = [
                    ticket_to_dict(t) for t in graph["children"]
                ]

            if graph.get("epic"):
                result["relationships"]["epic"] = {
                    "id": graph["epic"].id,
                    "title": graph["epic"].title,
                    "status": graph["epic"].status
                }

        return result
