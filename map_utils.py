# map_utils.py

import folium


BERLIN_CENTER = [52.5200, 13.4050]


BERLIN_DISTRICT_COORDINATES = {
    "Mitte": [52.5200, 13.4050],
    "Friedrichshain-Kreuzberg": [52.5158, 13.4543],
    "Pankow": [52.5692, 13.4025],
    "Charlottenburg-Wilmersdorf": [52.5079, 13.2637],
    "Spandau": [52.5358, 13.1974],
    "Steglitz-Zehlendorf": [52.4309, 13.1927],
    "Tempelhof-Schöneberg": [52.4667, 13.3833],
    "Neukölln": [52.4811, 13.4350],
    "Treptow-Köpenick": [52.4579, 13.6033],
    "Marzahn-Hellersdorf": [52.5225, 13.5877],
    "Lichtenberg": [52.5322, 13.5119],
    "Reinickendorf": [52.6048, 13.2950],
    "Other / Not specified": [52.5200, 13.4050],
}


def get_district_coordinates(district: str):
    return BERLIN_DISTRICT_COORDINATES.get(
        district,
        BERLIN_DISTRICT_COORDINATES["Other / Not specified"],
    )


def create_seed_map(listings):
    seed_map = folium.Map(
        location=BERLIN_CENTER,
        zoom_start=11,
        tiles="OpenStreetMap",
    )

    for listing in listings:
        district = listing.get("berlin_district", "Other / Not specified")
        coordinates = get_district_coordinates(district)

        seed_name = listing.get("seed_name", "Unnamed seed or seedling")
        category = listing.get("category", "Not specified")
        condition = listing.get("best_balcony_condition", "Not specified")
        suitable_for = listing.get("suitable_for", "Not specified")
        quantity = listing.get("quantity", "Not specified")
        owner_name = listing.get("owner_name", "Not specified")
        contact = listing.get("contact", "Not specified")
        description = listing.get("description", "")

        popup_html = f"""
        <div style="width: 260px;">
            <h4>{seed_name}</h4>
            <b>Category:</b> {category}<br>
            <b>District:</b> {district}<br>
            <b>Best balcony condition:</b> {condition}<br>
            <b>Suitable for:</b> {suitable_for}<br>
            <b>Quantity:</b> {quantity}<br>
            <b>Shared by:</b> {owner_name}<br>
            <b>Contact:</b> {contact}<br>
            <br>
            <b>Growing tip:</b><br>
            {description}
        </div>
        """

        folium.Marker(
            location=coordinates,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=seed_name,
            icon=folium.Icon(color="green", icon="leaf"),
        ).add_to(seed_map)

    return seed_map