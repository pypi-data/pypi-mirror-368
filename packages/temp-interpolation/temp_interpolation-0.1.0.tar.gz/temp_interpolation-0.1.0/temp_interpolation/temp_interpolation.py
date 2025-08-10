"""Main module."""

import os
import folium
import ipyleaflet


class Map(ipyleaflet.Map):
    def __init__(self, center=[19, 72], zoom=2, height="600px", **kwargs):
        """Map class to create Map View

        Args:
            center (list, optional): Map Center. Defaults to [19, 72]
            zoom (int, optional): Zoom level. Defaults to 2.
            height (str, optional): Map Height. Defaults to "600px".
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenTopoMap"):
        """Adds basemap to Map View

        Args:
            basemap (str, optional): Base Map. Defaults to "OpenTopoMap".
        """

        try:
            url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
            layer = ipyleaflet.TileLayer(url=url, name=basemap)
            self.add_layer(layer)
        except:
            url = eval(f"ipyleaflet.basemaps.OpenTopoMap").build_url()
            layer = ipyleaflet.TileLayer(url=url, name=basemap)
            self.add_layer(layer)

    def add_google_map(self, map_type="ROADMAP"):
        """Adds Google Maps layer to Map View

        Args:
            map_type (str, optional): Type of Google Map.
                Defaults to "ROADMAP". Available options : "ROADMAP", "SATELLITE", "HYBRID","TERRAIN"
        """

        map_types = {"ROADMAP": "m", "SATELLITE": "s", "HYBRID": "h", "TERRAIN": "t"}
        map_type = map_types[map_type.upper()]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = ipyleaflet.TileLayer(url=url, name="Google Map")
        self.add_layer(layer)

    def add_vector(
        self,
        vector,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Adds Vector layer to Map View

        Args:
            vector (str or dict): URL or path to vector file. Can be a shapefile, GeoDataFrame, GeoJSON, etc.
            zoom_to_layer (bool, optional): Whether to zoom to added layer. Defaults to True.
            hover_style (dict, optional): Style to apply on hover. Defaults to Defaults to {'color':'yellow', 'fillOpacity':0.2}.
            **kwargs: Additional keyword arguments passed to ipyleaflet.GeoJSON.
        """

        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.2}

        if isinstance(vector, str):
            gdf = gpd.read_file(vector)
            gdf = gdf.to_crs(epsg=4326)
            data = gdf.__geo_interface__
        elif isinstance(vector, dict):
            data = vector

        gjson = ipyleaflet.GeoJSON(data=data, hover_sytle=hover_style, **kwargs)
        self.add_layer(gjson)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_layer_control(self):
        """Adds Layer Control Button to Map View

        This control allows users to toggle the visibility of layers.
        """
        self.add_control(control=ipyleaflet.LayersControl())
