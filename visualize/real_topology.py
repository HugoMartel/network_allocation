import folium

def plot_use_case(EUs, BSs) :
    m = folium.Map(location=[45.75, 4.85], zoom_start=13)
    # Compute Voronoi diagram
    points = []
    for end_user in self.EUs : #Ici index est la STA   
        point = [end_user.x, end_user.y]
        # Add a point marker using CircleMarker
        folium.CircleMarker(
            location=point,  # Latitude and longitude
            radius=1,               # Radius of the circle marker (adjust as needed)
            color='black',           # Color of the circle marker
            fill=True,              # Fill the circle with color
            fill_color='black',      # Fill color
            fill_opacity=1.0,       # Fill opacity (0 to 1)
        ).add_to(m)

    for end_user in self.BSs : #Ici index est la STA   
        point = [end_user.x, end_user.y]
        points.append(point)
        # Add a point marker using CircleMarker
        folium.CircleMarker(
            location=point,  # Latitude and longitude
            radius=3,               # Radius of the circle marker (adjust as needed)
            color='red',           # Color of the circle marker
            fill=True,              # Fill the circle with color
            fill_color='red',      # Fill color
            fill_opacity=1.0,       # Fill opacity (0 to 1)
        ).add_to(m)

        folium.PolyLine(locations=[vor.vertices[i], far_point], color="blue", weight=2).add_to(m)

    # Display the map
    m.save('real_topology_map.html')


