import folium


class Map(folium.Map):
    """A Folium Map subclass with additional helper methods for vector data and controls.

    Args:
        center (tuple, optional): Latitude and longitude for the map center. Defaults to (0, 0).
        zoom (int, optional): Initial zoom level. Defaults to 3.
        **kwargs: Additional keyword arguments passed to folium.Map.
    """

    def __init__(self, center=(0, 0), zoom=3, **kwargs):
        """Initializes the Map object.

        Args:
            center (tuple, optional): Latitude and longitude for the map center. Defaults to (0, 0).
            zoom (int, optional): Initial zoom level. Defaults to 3.
            **kwargs: Additional keyword arguments passed to folium.Map.
        """
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_basemap(self, basemap="OpenTopoMap"):
        """
        Adds a basemap to the map.

        Args:
            basemap (str, optional): Name of the basemap to add. Defaults to "OpenTopoMap".
                Available options include "OpenStreetMap", "Stamen Terrain", "Stamen Toner", "Stamen Watercolor", etc.

        Raises:
            Exception: If the specified basemap cannot be added, attempts to add it again.
        """
        try:
            layer = folium.TileLayer(tiles=basemap, name=basemap)
            layer.add_to(self)
        except:
            layer = folium.TileLayer(tiles=basemap, name=basemap)
            layer.add_to(self)

    def add_google_map(self, map_type="ROADMAP"):
        """
        Adds a Google Maps tile layer to the map.

        Args:
            map_type (str, optional): Type of Google Map to add.
                Available options are "ROADMAP", "SATELLITE", "HYBRID", and "TERRAIN". Defaults to "ROADMAP".
        """

        map_types = {"ROADMAP": "m", "SATELLITE": "s", "HYBRID": "h", "TERRAIN": "t"}
        map_attr = map_types[map_type.upper()]

        url = (
            f"https://mt1.google.com/vt/lyrs={map_attr.lower()}&x={{x}}&y={{y}}&z={{z}}"
        )
        layer = folium.TileLayer(
            tiles=url,
            attr="Google",
            name=f"Google {map_type.capitalize()}",
            overlay=True,
        )
        layer.add_to(self)

    def add_vector(
        self,
        vector,
        zoom_to_layer=True,
        hover_style=None,
        **kwargs,
    ):
        """Adds a vector layer (GeoJSON or file) to the map.

        Args:
            vector (str or dict): Path to a vector file (e.g., shapefile, GeoJSON) or a GeoJSON-like dict.
            zoom_to_layer (bool, optional): Whether to zoom to the layer bounds. Defaults to True.
            hover_style (dict, optional): Style to apply on hover. Defaults to {'color':'yellow', 'fillOpacity':0.2}.
            **kwargs: Additional keyword arguments passed to folium.GeoJson.
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

        gjson = folium.GeoJson(data=data, highlight_style=hover_style, **kwargs)
        gjson.add_to(self)

        if zoom_to_layer:
            self.fit_bounds(self.get_bounds())

    def add_layer_control(self):
        """Adds a layer control widget to the map.

        This control allows users to toggle the visibility of layers.
        """
        folium.LayerControl().add_to(self)
