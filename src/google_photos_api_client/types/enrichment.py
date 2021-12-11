class TextEnrichment:
    """An enrichment containing text."""
    # Text for this enrichment item.
    text: str

    def __init__(self, text_enrichment: dict):
        self.text = text_enrichment['text']


class LatLng:
    """An object that represents a latitude/longitude pair. This is expressed as a pair of doubles to represent
    degrees latitude and degrees longitude. Unless specified otherwise, this object must conform to the WGS84
    standard. Values must be within normalized ranges. """

    # The latitude in degrees. It must be in the range [-90.0, +90.0].
    latitude: float

    # The longitude in degrees. It must be in the range [-180.0, +180.0].
    longitude: float

    def __init__(self, lat_lng: dict):
        self.latitude = float(lat_lng['latitude'])
        if self.latitude < (-90.0) or self.latitude > 90.0:
            raise TypeError('Latitude must be in range [-90.0, +90.0]')

        self.longitude = float(lat_lng['longitude'])
        if self.longitude < (-180.0) or self.longitude > 180.0:
            raise TypeError('Longitude must be in range [-180.0, 180.0]')


class Location:
    """Represents a physical location."""

    # Name of the location to be displayed.
    location_name: str

    # Position of the location on the map.
    latlng: LatLng

    def __init__(self, location: dict):
        self.location_name = str(location['locationName'])
        self.latlng = LatLng(location['latlng'])


class LocationEnrichment:
    """An enrichment containing a single location."""

    # Location for this enrichment item.
    location: Location

    def __init__(self, location_enrichment: dict):
        self.location = Location(location_enrichment['location'])


class MapEnrichment:
    """An enrichment containing a map, showing origin and destination locations."""

    # Origin location for this enrichment item.
    origin: Location

    # Destination location for this enrichment item.
    destination: Location

    def __init__(self, map_enrichment: dict):
        self.origin = Location(map_enrichment['origin'])
        self.destination = Location(map_enrichment['destination'])


class EnrichmentItem:
    """An enrichment item."""

    # Identifier of the enrichment item.
    id: str

    def __init__(self, enrichment_item: dict):
        self.id = str(enrichment_item['id'])
