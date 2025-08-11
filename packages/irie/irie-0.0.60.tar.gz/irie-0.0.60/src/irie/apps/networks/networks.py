#
# (c) Soga Research Group
# 
# Pengshun Li
#
from pathlib import Path
import zipfile
import pandas as pd
import numpy as np
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point
import folium
from folium.plugins import TagFilterButton, Search

from irie.apps.inventory.models import Asset

cwd = Path(__file__).parent

transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)


COLUMN_ALIASES = {
    "bridge":                           "Bridge",
    "corridor":                         "Corridor",
    'detour_length':                    'Detour length',
    "times_used_by_hospital_access":    "Zone-hospital pairs",
    "times_used_by_fire_access":        "Zone-fire pairs",
    "times_used_by_police_access":      "Zone-police pairs",
    "times_used_by_maintenance_access": "Zone-maintenance pairs",
    "times_used_by_airport_access":     "Zone-airport pairs",
    "times_used_by_seaport_access":     "Zone-seaport pairs",
    "times_used_by_ferry_access":       "Zone-seaport pairs",
    "long_decimal":                     "Lon",
    "lat_decimal":                      "Lat",
}

def _read_csv(arxiv, path):
    return pd.read_csv(arxiv.open(path))

def _read_csv_field(arxiv, file, dicts):
    return [
        {
            getattr(tmp, name): getattr(tmp, key)
            for tmp in _read_csv(arxiv, file).itertuples()
            for name, key in fields.items()
        } for fields in dicts
    ]

# Define style functions for default and highlighted states
def _style_function_zipcode(feature):
    return {"color": "pink", "weight": 1, "opacity": 0.2}  # Default color

def _style_function_network(feature):
    return {"color": "gray", "weight": 1, "opacity": 1}  # Default color

def _style_function(feature):
    return {"color": "blue", "weight": 2, "opacity": 1}  # Default color

def _style_function_strahnet(feature):
    return {"color": "brown", "weight":2, "opacity":0.5} # Default color

def _highlight_function(feature):
    return {"color": "red", "weight": 4, "opacity": 1}  # Highlight color


class _NetworkBase:
    arxiv: zipfile.ZipFile
    _weights: dict
    _consider_population: bool

    #
    # Loaded with load_data
    #
    _hospital_corridor    : dict
    _fire_corridor        : dict
    _police_corridor      : dict
    _maintenance_corridor : dict
    _airport_corridor     : dict
    _seaport_corridor     : dict
    _ferry_corridor       : dict


    _hospital_corridor_consider_pop_dict    : dict
    _fire_corridor_consider_pop_dict        : dict
    _police_corridor_consider_pop_dict      : dict
    _maintenance_corridor_consider_pop_dict : dict
    _airport_corridor_consider_pop_dict     : dict
    _seaport_corridor_consider_pop_dict     : dict
    _ferry_corridor_consider_pop_dict       : dict

    #
    # Loaded with load_bridges
    #
    _hospital_count_dict    : dict
    _fire_count_dict        : dict
    _police_count_dict      : dict
    _maintenance_count_dict : dict
    _airport_count_dict     : dict
    _seaport_count_dict     : dict
    _ferry_count_dict       : dict

    _bridge_corridor_corres_gdf : gpd.GeoDataFrame
    bridge_detour_dict : dict


    def __init__(self, preferences, weights, consider_population, load_bridges=False):
        self._weights = weights
        self._corridors = None
        self._preferences = preferences
        self._consider_population = consider_population

        self.load_data()

        if load_bridges:
            self.load_bridges()

            bridge_corridor_corres_df = _read_csv(self.arxiv, "data/bridge_corridor_corres.csv")
            bridge_corridor_corres_df["geometry"] = bridge_corridor_corres_df.apply(
                lambda row: Point(row["long_decimal"], row["lat_decimal"]), axis=1
            )
            self._bridge_corridor_corres_gdf = gpd.GeoDataFrame(
                bridge_corridor_corres_df, geometry="geometry", crs="EPSG:4326"
            )

            bridge_detour_df = _read_csv(self.arxiv, "data/D4_bridges.csv")
            self.bridge_detour_dict = {
                        getattr(tmp, 'bridge_nbi'): getattr(tmp,'detour_length_NBI19')
                                for tmp in bridge_detour_df.itertuples()
            }


    def load_data(self):
        pass

    def load_bridges(self):
        pass
    
    # def ranked_corridors(self):
    #     if self._corridors is None:
    #         self._corridors = gpd.read_file(self.arxiv.open("data/corridor_line.geojson"))
    #         corridor_weights, corridor_ranks = self.corridor_ranking(self._weights, 
    #                                                                  self._consider_population)
    #         self._corridors["corridor_weighted"] = self._corridors["id"].map(corridor_weights)
    #         self._corridors["corridor_rank"]     = self._corridors["id"].map(corridor_ranks)

    #     return self._corridors

    def ranked_corridors(self):
        if self._corridors is None:
            self._corridors = gpd.read_file(self.arxiv.open("data/corridor_line.geojson"))
            corridor_weights, corridor_ranks, zone_count_dict = self.corridor_ranking(self._weights, 
                                                                     self._consider_population)
            self._corridors["corridor_weighted"] = self._corridors["id"].map(corridor_weights)
            self._corridors["corridor_rank"]     = self._corridors["id"].map(corridor_ranks)
            self._corridors["corridor_rank_str"] = self._corridors["corridor_rank"].apply(lambda x:str(int(x)) + ' of 161')
            self._corridors["zone_count"]        = self._corridors["id"].map(zone_count_dict)
        return self._corridors

    def create_map(self, corridor=None):

        if corridor is not None:
            bridges, categories = self._get_bridges(corridor, self._weights)
            location = sum(np.array(m.location) for m in bridges) / len(bridges)
        else:
            location = (self._preferences.latitude, self._preferences.longitude)

        chart = folium.Map(
            location=location,
            tiles="cartodb positron",
            show=True,
            zoom_start=10,
            control_scale=True,
        )

        if corridor is not None:
            self._add_zipcodes(chart)

            self._add_network(chart)

            for m in reversed(bridges):
                m.add_to(chart)

            TagFilterButton(categories).add_to(chart)

            html_text = """
                        <div style="position: absolute; top: 86px; left: 48px; z-index: 1000; background: white; padding: 5px; border: 1px solid black; font-size: 12px; font-weight:bold";font-family: 'Times New Roman', Times, serif;>
                        ← this is a filter button
                        </div>
                        """
            chart.get_root().html.add_child(folium.Element(html_text))

        self.add_corridor(chart, corridor=corridor)

        try:
            self.add_strahnet(chart)
        except:
            pass

        folium.LayerControl().add_to(chart)
        return chart

    def add_strahnet(self, chart):
        popup_strahnet = folium.GeoJsonPopup(
            fields = ['RouteID','NHS_TYPE'],
            aliases = [
                "RouteID:",
                "Type:"
            ],
            localize=True,
            labels=True,
            style="background-color: yellow;")

        with self.arxiv.open("data/strahnet.geojson") as f:
            strahnet_gdf = gpd.read_file(f)
        # Load the GeoJSON from the URL
        strahnet_geo = folium.GeoJson(
            strahnet_gdf.to_json(),
            name="Strahnet",
            popup=popup_strahnet,
            style_function=_style_function_strahnet,
            localize=True,
            show=False
        ).add_to(chart)


    def add_corridor(self, chart, corridor=None):
        MAX_CORRIDOR = 161

        popup_corridor = folium.GeoJsonPopup(
            fields=["id", "name_new", "type", "zone_count", "corridor_weighted", "corridor_rank_str"],
            aliases=[
                "Corridor #",
                "Corridor ID",
                "Corridor Type",
                "Zone Count",
                "Corridor Value",
                "Corridor Rank",
            ],
            localize=True,
            labels=True,
        )

        tooltip_corridor = folium.GeoJsonTooltip(
            fields=["id", "name_new"],
            aliases=["Corridor #", "Corridor ID"],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        )

        #
        corridor_line_gdf = self.ranked_corridors().copy()

        if corridor is not None:
            corridor_line_gdf = corridor_line_gdf.loc[corridor_line_gdf["id"] == corridor, :]

        corridor_line_gdf["name_new"] = corridor_line_gdf.apply(
                lambda x: f'<a href="" onclick="handleCorridorSelection(\'corr-{x["id"]}\')">{x["name_new"]}</a>', axis=1
        )

        corridor_geo = folium.GeoJson(
            corridor_line_gdf.to_json(),
            name="corridor",
            popup=popup_corridor,
            tooltip=tooltip_corridor,
            style_function=_style_function,
            localize=True,
        ).add_to(chart)

        if corridor is None:

            Search(
                layer=corridor_geo,
                geom_type="Polygon",
                placeholder="Search for a corridor based on its number",
                collapsed=False,
                search_label="id",
                color="#FF0000",
                weight = 4
            ).add_to(chart)

            text_string = f"""
                <div style="position: absolute; top: 10px; left: 50px; background-color: rgba(255, 255, 255); padding: 5px; z-index: 1000;font-size: 10px;">
                    <label for="min_id">Highest Rank:</label>
                    <input type="number" id="min_id" name="min_id" value="1">
                    <label for="max_id">Lowest Rank:</label>
                    <input type="number" id="max_id" name="max_id" value="10">
                    <button onclick="applyFilter()">Apply Filter</button>
                    <button onclick="resetFilter()">Reset Filter</button>
                </div>

                <script>
                var highlightedIDs = []; // Array to store highlighted IDs

                function applyFilter() {{
                    // Get the min and max ID values from input fields
                    var minID = document.getElementById("min_id").value;
                    var maxID = document.getElementById("max_id").value;

                    // Call the filter function with the input values
                    filterByIDRange(minID, maxID);
                }}

                function filterByIDRange(min, max) {{
                    // Filter through GeoJson layer and highlight matching features
                    var layer = {corridor_geo.get_name()};  // This is the layer name passed from Python
                    layer.eachLayer(function (layer) {{
                        var featureID = layer.feature.properties.corridor_rank;
                        if (featureID >= min && featureID <= max) {{
                            layer.setStyle({{color: 'red', weight: 4}});  // Highlight in red
                            if (!highlightedIDs.includes(featureID)) {{
                                highlightedIDs.push(featureID); // Keep track of highlighted IDs
                            }}
                        }} else {{
                            // Reset to default color only if not highlighted
                            if (!highlightedIDs.includes(featureID)) {{
                                layer.setStyle({{color: 'blue', weight: 2}});  // Default color
                            }}
                        }}
                    }});
                }}

                function resetFilter() {{
                    // Reset all styles to default and clear highlighted IDs
                    var layer = {corridor_geo.get_name()};  // This is the layer name passed from Python
                    layer.eachLayer(function (layer) {{
                        layer.setStyle({{color: 'blue', weight: 2}});  // Reset to default color
                    }});
                    highlightedIDs = []; // Clear highlighted IDs array
                }}

                </script>
            """
            chart.get_root().html.add_child(folium.Element(text_string))

            text_string1 = f"""
                <div style="position: absolute; top: 120px; left: 10px; z-index: 1000;font-size: 10px;">
                    <button onclick="resetFilter_corridor()">Reset Filter for corridor search</button>
                </div>
    
                <script> 
                function resetFilter_corridor() {{
                    // Reset all styles to default and clear highlighted IDs
                    var layer = {corridor_geo.get_name()};  // This is the layer name passed from Python
                    layer.eachLayer(function (layer) {{
                        layer.setStyle({{color: 'blue', weight: 2}});  // Reset to default color
                    }});
                }}
                </script>            
            """
            chart.get_root().html.add_child(folium.Element(text_string1))

    def corridor_ranking(self, weights, consider_population=False):
        total_weight = weights.get("hospital_weight", 1) + \
                       weights.get("fire_weight", 1) + \
                       weights.get("police_weight", 1) + \
                       weights.get("maintenance_weight", 1) + \
                       weights.get("airport_weight", 1) + \
                       weights.get("seaport_weight", 1) + \
                       weights.get("ferry_weight", 1)
        hospital_weight    = weights.get("hospital_weight", 1)    / total_weight
        fire_weight        = weights.get("fire_weight", 1)        / total_weight
        police_weight      = weights.get("police_weight", 1)      / total_weight
        maintenance_weight = weights.get("maintenance_weight", 1) / total_weight
        airport_weight     = weights.get("airport_weight", 1)     / total_weight
        seaport_weight     = weights.get("seaport_weight", 1)     / total_weight
        ferry_weight       = weights.get("ferry_weight", 1)       / total_weight

        hospital_weight_tmp = 1 if hospital_weight !=0 else 0
        fire_weight_tmp = 1 if fire_weight !=0 else 0
        police_weight_tmp = 1 if police_weight !=0 else 0
        maintenance_weight_tmp = 1 if maintenance_weight !=0 else 0
        airport_weight_tmp = 1 if airport_weight !=0 else 0
        seaport_weight_tmp = 1 if seaport_weight !=0 else 0
        ferry_weight_tmp = 1 if ferry_weight !=0 else 0

        corridor_agg_df = pd.DataFrame()
        corridor_agg_df["corridor_id"] = np.arange(1, 162)

        corridor_agg_df["hospital_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._hospital_corridor
        )
        corridor_agg_df["fire_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._fire_corridor
        )
        corridor_agg_df["police_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._police_corridor
        )
        corridor_agg_df["maintenance_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._maintenance_corridor
        )
        corridor_agg_df["airport_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._airport_corridor
        )
        corridor_agg_df["seaport_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._seaport_corridor
        )
        corridor_agg_df["ferry_count_weight"] = corridor_agg_df["corridor_id"].map(
            self._ferry_corridor
        )

        corridor_agg_df["zone_count"] = corridor_agg_df.apply(
            lambda x: x["hospital_count_weight"]*hospital_weight_tmp
                    + x["fire_count_weight"]*fire_weight_tmp
                    + x["police_count_weight"]*police_weight_tmp
                    + x["maintenance_count_weight"]*maintenance_weight_tmp
                    + x["airport_count_weight"]*airport_weight_tmp
                    + x["seaport_count_weight"]*seaport_weight_tmp
                    + x["ferry_count_weight"]*ferry_weight_tmp,
            axis=1,
        )

        if consider_population:
            corridor_agg_df["hospital_count_weight"] = corridor_agg_df["corridor_id"].map(
                self._hospital_corridor_consider_pop_dict
            )
            corridor_agg_df["fire_count_weight"] = corridor_agg_df["corridor_id"].map(
                self._fire_corridor_consider_pop_dict
            )
            corridor_agg_df["police_count_weight"] = corridor_agg_df["corridor_id"].map(
                self._police_corridor_consider_pop_dict
            )
            corridor_agg_df["maintenance_count_weight"] = corridor_agg_df[
                "corridor_id"
            ].map(self._maintenance_corridor_consider_pop_dict)
            corridor_agg_df["airport_count_weight"] = corridor_agg_df["corridor_id"].map(
                self._airport_corridor_consider_pop_dict
            )
            corridor_agg_df["seaport_count_weight"] = corridor_agg_df["corridor_id"].map(
                self._seaport_corridor_consider_pop_dict
            )
            corridor_agg_df["ferry_count_weight"] = corridor_agg_df["corridor_id"].map(
                self._ferry_corridor_consider_pop_dict
            )
        
        corridor_agg_df["hospital_count_weight"]    *= hospital_weight
        corridor_agg_df["fire_count_weight"]        *= fire_weight
        corridor_agg_df["police_count_weight"]      *= police_weight
        corridor_agg_df["maintenance_count_weight"] *= maintenance_weight
        corridor_agg_df["airport_count_weight"]     *= airport_weight
        corridor_agg_df["seaport_count_weight"]     *= seaport_weight
        corridor_agg_df["ferry_count_weight"]       *= ferry_weight

        corridor_agg_df["weighted_count"] = corridor_agg_df.apply(
            lambda x: x["hospital_count_weight"]
                    + x["fire_count_weight"]
                    + x["police_count_weight"]
                    + x["maintenance_count_weight"]
                    + x["airport_count_weight"]
                    + x["seaport_count_weight"]
                    + x["ferry_count_weight"],
            axis=1,
        )
        corridor_agg_df.sort_values("weighted_count", ascending=False, inplace=True)
        corridor_agg_df["rank"] = corridor_agg_df["weighted_count"].rank(method='dense', ascending=False)
        corridor_agg_df = corridor_agg_df[["corridor_id", "weighted_count", "rank", "zone_count"]].copy()
        zone_count_dict = dict(
            zip(corridor_agg_df["corridor_id"], corridor_agg_df["zone_count"])
        )
        corridor_weighted_value_dict = dict(
            zip(corridor_agg_df["corridor_id"], corridor_agg_df["weighted_count"])
        )
        corridor_rank_dict = dict(
            zip(corridor_agg_df["corridor_id"], corridor_agg_df["rank"])
        )
        return corridor_weighted_value_dict, corridor_rank_dict, zone_count_dict


    def _add_network(self, chart):
        road_network_geojson_data = gpd.read_file(self.arxiv.open("data/recovery_bridge_network_links.json"))
        network_feature = folium.GeoJson(
            road_network_geojson_data,
            name="Network",
            style_function=_style_function_network,
            highlight_function=_highlight_function,
            show=False,
        )
        network_feature.add_to(chart)


    def _add_zipcodes(self, chart):
        tooltip_zipcode = folium.GeoJsonTooltip(
            fields=["po_name", "zip"],  # Specify the fields you want to show
            aliases=["Post Office Name", "ZIP Code"],
        )
        zipcode_geojson_data = gpd.read_file(self.arxiv.open("data/zipcode.geojson"))
        # Create a GeoJson feature with the correct fields
        zipcode_feature = folium.GeoJson(
            zipcode_geojson_data,
            name="Zip Code",
            style_function=_style_function_zipcode,
            highlight_function=_highlight_function,
            tooltip=tooltip_zipcode,
            show=False,
        )

        zipcode_feature.add_to(chart)


    def _get_bridges(self, corridor, weights):

        bridge_required_gdf = self.bridge_info_for_a_corridor(weights, corridor)

        bridge_required_gdf['detour_length'] = bridge_required_gdf['bridge'].map(self.bridge_detour_dict)
        column = bridge_required_gdf.pop('detour_length')
        bridge_required_gdf.insert(4, 'detour_length', column)

        categories = ['used &detour length>2km','used &detour length<=2km','unused']
        bridge_required_gdf["used"] = bridge_required_gdf.iloc[:, 6:].sum(axis=1)

        markers = []
        for bridge in bridge_required_gdf.itertuples():

            # Find the asset associated with the bridge
            try:
                asset = Asset.objects.get(calid=bridge.bridge.replace(" ", "-"))
            except Asset.DoesNotExist:
                asset = None

            if (getattr(bridge, 'used') > 0) and (getattr(bridge, 'detour_length')<=2):
                category = 'used &detour length<=2km'
            elif (getattr(bridge, 'used')>0) and (getattr(bridge, 'detour_length')>2):
                category = 'used &detour length>2km'
            else:
                category = 'unused'

            popup_content = """
            <table style="width: 200px; border-collapse: collapse; border: none;">
                """

            for column in bridge_required_gdf.columns.values:
                if column == "bridge" and asset is not None:
                    popup_content += f"""
                    <tr>
                        <td>{COLUMN_ALIASES[column]}</td>
                        <td><a target="_blank" href="/inventory/{asset.calid}/">{bridge.bridge}</a></td>
                    </tr>
                    """
                elif column not in {"long_decimal", "lat_decimal", "geometry", "detour_length", "used"}:
                    popup_content += f"""
                    <tr>
                      <td>{COLUMN_ALIASES[column]}</td>
                      <td>{getattr(bridge, column)}</td>
                    </tr>
                    """

            popup_content += "</table>"

            if asset is not None:
                marker = folium.Marker(
                    location=[bridge.geometry.y, bridge.geometry.x],
                    popup=popup_content,
                    tags=[category],
                    tooltip=asset.name,
                    z_index_offset=1000,
                    icon=folium.Icon(color="blue"),
                )
            else:
                marker = folium.Marker(
                    location=[bridge.geometry.y, bridge.geometry.x],
                    popup=popup_content,
                    tags=[category],
                    z_index_offset=900,
                    icon=folium.Icon(color="gray"),
                )
            markers.append(marker)

        return markers, categories

    def bridge_info_for_a_corridor(self, weights, corridor_input):

        bridge_required_gdf = self._bridge_corridor_corres_gdf.loc[
            (self._bridge_corridor_corres_gdf["one_corridor"] == corridor_input)
            | (self._bridge_corridor_corres_gdf["another_corridor"] == corridor_input),
            ["bridge", "lat_decimal", "long_decimal", "geometry"],
        ].copy()

        bridge_required_gdf["corridor"] = corridor_input
        bridge_required_gdf = bridge_required_gdf[
            ["bridge", "corridor", "long_decimal", "lat_decimal", "geometry"]
        ]
        if weights["hos_weight"] != 0:
            bridge_required_gdf["times_used_by_hospital_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._hospital_count_dict)
        if weights["fire_weight"] != 0:
            bridge_required_gdf["times_used_by_fire_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._fire_count_dict)
        if weights["police_weight"] != 0:
            bridge_required_gdf["times_used_by_police_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._police_count_dict)
        if weights["maintenance_weight"] != 0:
            bridge_required_gdf["times_used_by_maintenance_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._maintenance_count_dict)
        if weights["airport_weight"] != 0:
            bridge_required_gdf["times_used_by_airport_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._airport_count_dict)

        if weights["seaport_weight"] != 0:
            bridge_required_gdf["times_used_by_seaport_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._seaport_count_dict)
        if weights["ferry_weight"] != 0:
            bridge_required_gdf["times_used_by_ferry_access"] = bridge_required_gdf[
                "bridge"
            ].map(self._ferry_count_dict)
        return bridge_required_gdf


class BridgeNetworks_method_a(_NetworkBase):
    def load_data(self):
        arxiv = self.arxiv = zipfile.ZipFile(cwd/"data.zip")

        self._hospital_corridor, self._hospital_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/hospital_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._fire_corridor, self._fire_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/fire_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._police_corridor, self._police_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/police_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._maintenance_corridor, self._maintenance_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/maintenance_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._airport_corridor, self._airport_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/airport_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._seaport_corridor, self._seaport_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/seaport_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._ferry_corridor, self._ferry_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/ferry_access_corridor_info.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

    def load_bridges(self):

        arxiv = self.arxiv

        hospital_visualization_df = _read_csv(arxiv, "data/hospital_access_visualization.csv")
        self._hospital_count_dict = dict(
            zip(hospital_visualization_df["bridge"], hospital_visualization_df["bridge_count"])
        )
        fire_visualization_df = _read_csv(arxiv, "data/fire_access_visualization.csv")
        self._fire_count_dict = dict(
            zip(fire_visualization_df["bridge"], fire_visualization_df["bridge_count"])
        )
        police_visualization_df = _read_csv(arxiv, "data/police_access_visualization.csv")
        self._police_count_dict = dict(
            zip(police_visualization_df["bridge"], police_visualization_df["bridge_count"])
        )
        maintenance_visualization_df = _read_csv(arxiv, "data/maintenance_access_visualization.csv")
        self._maintenance_count_dict = dict(
            zip(
                maintenance_visualization_df["bridge"], maintenance_visualization_df["bridge_count"],
            )
        )
        airport_visualization_df = _read_csv(arxiv, "data/airport_access_visualization.csv")
        self._airport_count_dict = dict(
            zip(airport_visualization_df["bridge"], airport_visualization_df["bridge_count"])
        )
        seaport_visualization_df = _read_csv(arxiv, "data/seaport_access_visualization.csv")
        self._seaport_count_dict = dict(
            zip(seaport_visualization_df["bridge"], seaport_visualization_df["bridge_count"])
        )
        ferry_visualization_df = _read_csv(arxiv, "data/ferry_access_visualization.csv")
        self._ferry_count_dict = dict(
            zip(ferry_visualization_df["bridge"], ferry_visualization_df["bridge_count"])
        )


class BridgeNetworks_method_b(_NetworkBase):
    def load_data(self):

        arxiv = self.arxiv = zipfile.ZipFile(cwd/"data.zip")

        self._hospital_corridor, self._hospital_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/hospital_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._fire_corridor, self._fire_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/fire_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._police_corridor, self._police_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/police_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._maintenance_corridor, self._maintenance_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/maintenance_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._airport_corridor, self._airport_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/airport_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._seaport_corridor, self._seaport_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/seaport_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._ferry_corridor, self._ferry_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/ferry_access_corridor_info_method_b.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

    def load_bridges(self):

        arxiv = self.arxiv

        hospital_visualization_df = _read_csv(arxiv, "data/hospital_access_visualization_method_b.csv")
        self._hospital_count_dict = dict(
            zip(hospital_visualization_df["bridge"], hospital_visualization_df["bridge_count"])
        )
        fire_visualization_df = _read_csv(arxiv, "data/fire_access_visualization_method_b.csv")
        self._fire_count_dict = dict(
            zip(fire_visualization_df["bridge"], fire_visualization_df["bridge_count"])
        )
        police_visualization_df = _read_csv(arxiv, "data/police_access_visualization_method_b.csv")
        self._police_count_dict = dict(
            zip(police_visualization_df["bridge"], police_visualization_df["bridge_count"])
        )
        maintenance_visualization_df = _read_csv(arxiv, "data/maintenance_access_visualization_method_b.csv")
        self._maintenance_count_dict = dict(
            zip(
                maintenance_visualization_df["bridge"],
                maintenance_visualization_df["bridge_count"],
            )
        )
        airport_visualization_df = _read_csv(arxiv, "data/airport_access_visualization_method_b.csv")
        self._airport_count_dict = dict(
            zip(airport_visualization_df["bridge"], airport_visualization_df["bridge_count"])
        )
        seaport_visualization_df = _read_csv(arxiv, "data/seaport_access_visualization_method_b.csv")
        self._seaport_count_dict = dict(
            zip(seaport_visualization_df["bridge"], seaport_visualization_df["bridge_count"])
        )
        ferry_visualization_df = _read_csv(arxiv, "data/ferry_access_visualization_method_b.csv")
        self._ferry_count_dict = dict(
            zip(ferry_visualization_df["bridge"], ferry_visualization_df["bridge_count"])
        )

class BridgeNetworks_method_b_alt(_NetworkBase):
    def load_data(self):

        arxiv = self.arxiv = zipfile.ZipFile(cwd/"data.zip")
        self._hospital_corridor, self._hospital_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/hospital_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._fire_corridor, self._fire_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/fire_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._police_corridor, self._police_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/police_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._maintenance_corridor, self._maintenance_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/maintenance_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._airport_corridor, self._airport_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/airport_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._seaport_corridor, self._seaport_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/seaport_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

        self._ferry_corridor, self._ferry_corridor_consider_pop_dict = _read_csv_field(arxiv, "data/ferry_access_corridor_info_method_b_alt.csv", ({"corridor_id": "count"}, {"corridor_id": "count_consider_pop"}))

    def load_bridges(self):
        arxiv = self.arxiv

        hospital_visualization_df = _read_csv(arxiv, "data/hospital_access_visualization_method_b_alt.csv")
        self._hospital_count_dict = dict(
            zip(hospital_visualization_df["bridge"], hospital_visualization_df["bridge_count"])
        )
        fire_visualization_df = _read_csv(arxiv, "data/fire_access_visualization_method_b_alt.csv")
        self._fire_count_dict = dict(
            zip(fire_visualization_df["bridge"], fire_visualization_df["bridge_count"])
        )
        police_visualization_df = _read_csv(arxiv, "data/police_access_visualization_method_b_alt.csv")
        self._police_count_dict = dict(
            zip(police_visualization_df["bridge"], police_visualization_df["bridge_count"])
        )
        maintenance_visualization_df = _read_csv(arxiv, "data/maintenance_access_visualization_method_b_alt.csv")
        self._maintenance_count_dict = dict(
            zip(
                maintenance_visualization_df["bridge"],
                maintenance_visualization_df["bridge_count"],
            )
        )
        airport_visualization_df = _read_csv(arxiv, "data/airport_access_visualization_method_b_alt.csv")
        self._airport_count_dict = dict(
            zip(airport_visualization_df["bridge"], airport_visualization_df["bridge_count"])
        )
        seaport_visualization_df = _read_csv(arxiv, "data/seaport_access_visualization_method_b_alt.csv")
        self._seaport_count_dict = dict(
            zip(seaport_visualization_df["bridge"], seaport_visualization_df["bridge_count"])
        )
        ferry_visualization_df = _read_csv(arxiv, "data/ferry_access_visualization_method_b_alt.csv")
        self._ferry_count_dict = dict(
            zip(ferry_visualization_df["bridge"], ferry_visualization_df["bridge_count"])
        )
