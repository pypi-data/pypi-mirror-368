"""Network topology visualization for infrastructure systems."""

import folium
import networkx as nx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from folium import plugins


class NetworkVisualizer:
    """Visualize infrastructure networks and topologies."""

    def __init__(self):
        self.default_colors = px.colors.qualitative.Set1
        self.state_colors = {
            0: "red",  # Failed
            1: "orange",  # Critical
            2: "orange",
            3: "yellow",  # Poor
            4: "yellow",
            5: "lightgreen",  # Fair
            6: "lightgreen",
            7: "green",  # Good
            8: "green",
            9: "darkgreen",  # Excellent
            10: "darkgreen",
        }

    def create_network_graph(
        self,
        components: list[dict],
        connections: list[tuple] = None,
        layout: str = "spring",
    ) -> go.Figure:
        """Create network graph visualization of infrastructure components."""
        G = nx.Graph()

        # Add nodes
        for comp in components:
            comp_id = comp.get("id", 0)
            G.add_node(comp_id, **comp)

        # Add edges if provided
        if connections:
            G.add_edges_from(connections)

        # Calculate layout
        if layout == "spring":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "random":
            pos = nx.random_layout(G)
        else:
            pos = nx.spring_layout(G)

        # Extract node positions
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]

        # Node colors based on state
        node_colors = []
        node_text = []
        for node in G.nodes():
            state = G.nodes[node].get("state", 10)
            node_colors.append(self.state_colors.get(state, "gray"))

            # Create hover text
            node_info = G.nodes[node]
            text = f"ID: {node}<br>"
            text += f"State: {state}<br>"
            if "name" in node_info:
                text += f"Name: {node_info['name']}<br>"
            if "type" in node_info:
                text += f"Type: {node_info['type']}<br>"
            if "importance" in node_info:
                text += f"Importance: {node_info['importance']:.2f}<br>"
            node_text.append(text)

        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create figure
        fig = go.Figure()

        # Add edges
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=2, color="lightgray"),
                hoverinfo="none",
                showlegend=False,
            )
        )

        # Add nodes
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                marker=dict(
                    size=20,
                    color=node_colors,
                    line=dict(width=2, color="black"),
                    opacity=0.8,
                ),
                text=[str(node) for node in G.nodes()],
                textposition="middle center",
                hovertext=node_text,
                hoverinfo="text",
                showlegend=False,
            )
        )

        fig.update_layout(
            title="Infrastructure Network Topology",
            showlegend=False,
            hovermode="closest",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template="plotly_white",
        )

        return fig

    def create_geographic_map(
        self,
        components: list[dict],
        center_lat: float = 52.5,
        center_lon: float = 13.4,
        zoom: int = 10,
    ) -> folium.Map:
        """Create geographic map with infrastructure components."""
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon], zoom_start=zoom, tiles="OpenStreetMap"
        )

        # Add components as markers
        for comp in components:
            if "coordinates" in comp and comp["coordinates"]:
                lat, lon = comp["coordinates"][:2]

                # Determine marker color based on state
                state = comp.get("state", 10)
                color = self._get_folium_color(state)

                # Create popup text
                comp_id = comp.get("id", "?")
                comp_name = comp.get("name", f"Component {comp_id}")
                popup_text = f"<b>{comp_name}</b><br>"
                popup_text += f"State: {state}/10<br>"
                popup_text += f"Type: {comp.get('type', 'Unknown')}<br>"
                if "importance" in comp:
                    popup_text += f"Importance: {comp['importance']:.2f}<br>"
                if "criticality" in comp:
                    popup_text += f"Criticality: {comp['criticality']}<br>"

                # Add marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=300),
                    color="black",
                    fillColor=color,
                    fillOpacity=0.8,
                    weight=2,
                ).add_to(m)

        # Add legend
        legend_html = self._create_map_legend()
        m.get_root().html.add_child(folium.Element(legend_html))

        return m

    def create_cascade_visualization(
        self,
        components: list[dict],
        cascade_steps: list[dict],
        connections: list[tuple] = None,
    ) -> list[go.Figure]:
        """Create animation frames showing cascade failure propagation."""
        frames = []

        for step_idx, step_data in enumerate(cascade_steps):
            # Update component states for this step
            updated_components = []
            for comp in components:
                comp_copy = comp.copy()
                comp_id = comp["id"]
                if comp_id in step_data.get("failed_components", []):
                    comp_copy["state"] = 0  # Failed
                elif comp_id in step_data.get("degraded_components", []):
                    comp_copy["state"] = max(1, comp_copy.get("state", 10) - 2)
                updated_components.append(comp_copy)

            # Create network graph for this step
            fig = self.create_network_graph(
                updated_components, connections, layout="spring"
            )
            fig.update_layout(
                title=f"Cascade Step {step_idx + 1}: {step_data.get('description', '')}"
            )

            frames.append(fig)

        return frames

    def create_traffic_flow_map(
        self, road_network: dict, traffic_data: dict = None
    ) -> folium.Map:
        """Create map showing traffic flow on road network."""
        if not road_network.get("nodes") or not road_network.get("edges"):
            return folium.Map(location=[52.5, 13.4], zoom_start=10)

        # Calculate map center
        lats = [node["y"] for node in road_network["nodes"].values()]
        lons = [node["x"] for node in road_network["nodes"].values()]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)

        m = folium.Map(
            location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap"
        )

        # Add road segments
        for edge_id, edge_data in road_network["edges"].items():
            start_node = road_network["nodes"][edge_data["start"]]
            end_node = road_network["nodes"][edge_data["end"]]

            # Determine road color and width based on traffic
            if traffic_data and edge_id in traffic_data:
                traffic_level = traffic_data[edge_id].get("volume", 0)
                color = self._get_traffic_color(traffic_level)
                weight = max(2, min(8, traffic_level / 1000))
            else:
                color = "blue"
                weight = 3

            # Add road segment
            folium.PolyLine(
                locations=[
                    [start_node["y"], start_node["x"]],
                    [end_node["y"], end_node["x"]],
                ],
                color=color,
                weight=weight,
                opacity=0.8,
                popup=f"Road: {edge_data.get('name', edge_id)}<br>Traffic: {traffic_data.get(edge_id, {}).get('volume', 'Unknown')}",
            ).add_to(m)

        # Add traffic legend
        traffic_legend = self._create_traffic_legend()
        m.get_root().html.add_child(folium.Element(traffic_legend))

        return m

    def create_heatmap(
        self,
        components: list[dict],
        value_field: str = "state",
        center_lat: float = 52.5,
        center_lon: float = 13.4,
    ) -> folium.Map:
        """Create heatmap of component values."""
        m = folium.Map(
            location=[center_lat, center_lon], zoom_start=10, tiles="OpenStreetMap"
        )

        # Prepare heatmap data
        heat_data = []
        for comp in components:
            if "coordinates" in comp and comp["coordinates"]:
                lat, lon = comp["coordinates"][:2]
                value = comp.get(value_field, 0)
                heat_data.append([lat, lon, value])

        if heat_data:
            # Add heatmap layer
            plugins.HeatMap(
                heat_data,
                min_opacity=0.2,
                max_val=10,
                radius=20,
                blur=15,
                gradient={0.2: "blue", 0.4: "lime", 0.6: "orange", 1: "red"},
            ).add_to(m)

        return m

    def _get_folium_color(self, state: int) -> str:
        """Get folium marker color based on component state."""
        if state == 0:
            return "red"
        elif state <= 2:
            return "orange"
        elif state <= 4:
            return "yellow"
        elif state <= 6:
            return "lightgreen"
        else:
            return "green"

    def _get_traffic_color(self, volume: int) -> str:
        """Get color based on traffic volume."""
        if volume >= 5000:
            return "red"
        elif volume >= 3000:
            return "orange"
        elif volume >= 1000:
            return "yellow"
        else:
            return "green"

    def _create_map_legend(self) -> str:
        """Create HTML legend for component state map."""
        return """
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 150px; height: 120px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <h4>Component State</h4>
        <p><i class="fa fa-circle" style="color:green"></i> Excellent (7-10)</p>
        <p><i class="fa fa-circle" style="color:lightgreen"></i> Good (5-6)</p>
        <p><i class="fa fa-circle" style="color:yellow"></i> Poor (3-4)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Critical (1-2)</p>
        <p><i class="fa fa-circle" style="color:red"></i> Failed (0)</p>
        </div>
        """

    def _create_traffic_legend(self) -> str:
        """Create HTML legend for traffic flow map."""
        return """
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 150px; height: 100px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <h4>Traffic Volume</h4>
        <p><i class="fa fa-minus" style="color:red"></i> Heavy (5000+)</p>
        <p><i class="fa fa-minus" style="color:orange"></i> Moderate (3000+)</p>
        <p><i class="fa fa-minus" style="color:yellow"></i> Light (1000+)</p>
        <p><i class="fa fa-minus" style="color:green"></i> Low (<1000)</p>
        </div>
        """
