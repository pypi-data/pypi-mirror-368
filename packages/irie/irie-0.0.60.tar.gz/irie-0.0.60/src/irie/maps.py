
import folium
import numpy as np

class AssetMap:

    def __init__(self, assets, name=None, colors=None, color_name=None):
        if name is None:
            name = "Assets"

        if colors is not None and len(assets)>0 and len(colors) > 0:
            cm = folium.branca.colormap.LinearColormap(colors=["green", "yellow", "orange", "red"], 
                                                       vmin=0, vmax=max(colors.values()),
                                                       caption=color_name)
            colors = {
                k: cm.rgb_hex_str(v) for k,v in colors.items()
            }
        else:
            colors = None
            cm = None 

        markers = self.add_bridges(assets, colors=colors)

        if len(markers) > 0:
            location = sum(np.array(m.location) for m in markers) / len(markers)
        else:
            location = [37.7735, -122.0993] # (self._preferences.latitude, self._preferences.longitude)

        self._map    = m      = folium.Map(
            location=location, 
            zoom_start=6, 
            tiles='cartodbpositron'
        )

        if cm is not None:
            cm.add_to(m)

        for marker in markers:
            marker.add_to(m)


    def get_html(self, **kwargs):
        return self._map._repr_html_()


    def add_bridges(self, assets, colors=None):
        if colors is None:
            colors = {}

        markers = []
        top_markers = []
        for b in assets:
            lat, lon = b.coordinates
            if lat is None or lon is None:
                continue

            popup = folium.Popup(
                    folium.Html(
                        '<a style="display: inline;" target="_blank" href="/inventory/{calid}/">{label}</a>'.format(
                            calid=b.calid,
                            label=b.calid
                        ),
                        script=True
                    ),
                    min_width= 50,
                    max_width=100
            )

            marker = folium.CircleMarker(
                        location=[lat, lon],
                        popup=popup,
                        color = "blue" if b.is_complete else "black",
                        fill_color=colors.get(b.id, "blue" if b.is_complete else "gray"),
                        fill=True,
                        opacity=1,
                        fill_opacity=1,
                        radius=2,
                        weight=1,
                        z_index_offset=10 if b.is_complete else 100000
                    )

            if b.is_complete:
                marker = folium.Marker(
                       location=[lat, lon],
                       popup=popup,
                       icon=folium.Icon(icon="cloud", color="blue" if not b.is_complete else "beige"),
                       z_index_offset=1000
                   )
                top_markers.append(marker)

            elif b.calid in {"33-0526G", "33-0395L", "33-0525G", "33-0189L", "33-0523K", "33-0443", "33-0202F", "33-0202R", "33-0524F"}:
                pass

            else:
                markers.append(marker)

            markers.extend(top_markers)
        return markers

    #       top_markers.extend(markers)
    #   return top_markers
