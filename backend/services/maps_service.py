import logging
import aiohttp
from config import CONFIG

logger = logging.getLogger(__name__)

class GoogleMapsService:
    def __init__(self):
        self.api_key = CONFIG['api']['google_maps_api_key']
        self.use_mock = CONFIG.get('mock_services', {}).get('maps_responses', False)
        self.search_radius = CONFIG['poi'].get('search_radius_meters', 1500)
        self.max_results = CONFIG['poi'].get('max_results', 5)
        self.poi_types = CONFIG['poi'].get('types', [
            "restaurant", "school", "park", "shopping_mall", "transit_station"
        ])
        
        if self.use_mock:
            logger.warning("Google Maps is in mock mode - using simulated responses")
        elif not self.api_key or self.api_key.startswith('YOUR_'):
            logger.warning("Google Maps API key not configured - falling back to mock mode")
            self.use_mock = True
    
    async def get_location_coordinates(self, address: str) -> dict:
        if self.use_mock:
            logger.debug(f"Returning mock coordinates for address: {address}")
            return {
                "lat": 40.7128,
                "lng": -74.0060,
                "formatted_address": f"{address}, New York, NY, USA"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    "address": address,
                    "key": self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'OK' and data.get('results'):
                            result = data['results'][0]
                            location = result['geometry']['location']
                            logger.info(f"Geocoded address: {address} -> {location['lat']}, {location['lng']}")
                            return {
                                "lat": location['lat'],
                                "lng": location['lng'],
                                "formatted_address": result['formatted_address']
                            }
                        else:
                            logger.error(f"Google Maps geocoding failed for {address}: {data.get('status')}")
                            return None
                    else:
                        logger.error(f"Google Maps geocoding request failed with status: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error during geocoding {address}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error during geocoding {address}: {e}", exc_info=True)
            return None
    
    async def search_nearby_poi(self, lat: float, lng: float) -> list:
        if self.use_mock:
            logger.debug(f"Returning mock POI results for location: {lat}, {lng}")
            return self._mock_poi_results()
        
        poi_results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for poi_type in self.poi_types:
                    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    params = {
                        "location": f"{lat},{lng}",
                        "radius": self.search_radius,
                        "type": poi_type,
                        "key": self.api_key
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('status') == 'OK' and data.get('results'):
                                for place in data['results'][:self.max_results]:
                                    poi_results.append({
                                        "name": place.get('name'),
                                        "type": poi_type,
                                        "vicinity": place.get('vicinity'),
                                        "rating": place.get('rating'),
                                        "user_ratings_total": place.get('user_ratings_total')
                                    })
                                logger.debug(f"Found {len(data['results'])} {poi_type} locations")
                            elif data.get('status') == 'REQUEST_DENIED':
                                logger.error(f"Google Maps API request denied: {data.get('html_errors', '')}")
                        else:
                            logger.warning(f"POI search failed for type {poi_type}: status {response.status}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error during POI search at {lat}, {lng}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error during POI search at {lat}, {lng}: {e}", exc_info=True)
        
        logger.info(f"Found {len(poi_results)} total POI results for location {lat}, {lng}")
        return poi_results
    
    def _mock_poi_results(self) -> list:
        return [
            {
                "name": "Central Park",
                "type": "park",
                "vicinity": "New York, NY",
                "rating": 4.8,
                "user_ratings_total": 125000
            },
            {
                "name": "Whole Foods Market",
                "type": "shopping_mall",
                "vicinity": "10 Columbus Circle, New York, NY",
                "rating": 4.5,
                "user_ratings_total": 3200
            },
            {
                "name": "The Capital Grille",
                "type": "restaurant",
                "vicinity": "120 Broadway, New York, NY",
                "rating": 4.6,
                "user_ratings_total": 1850
            },
            {
                "name": "PS 11 Adolph S. Ochs",
                "type": "school",
                "vicinity": "900 5th Ave, New York, NY",
                "rating": 4.3,
                "user_ratings_total": 245
            },
            {
                "name": "Columbus Circle Station",
                "type": "transit_station",
                "vicinity": "Columbus Circle, New York, NY",
                "rating": 4.2,
                "user_ratings_total": 5600
            }
        ]
    
    def format_poi_for_description(self, poi_list: list) -> str:
        if not poi_list:
            return ""
        
        grouped = {}
        for poi in poi_list:
            poi_type = poi.get('type', 'other')
            if poi_type not in grouped:
                grouped[poi_type] = []
            grouped[poi_type].append(poi)
        
        sections = []
        type_labels = {
            'restaurant': 'Dining',
            'school': 'Education',
            'park': 'Recreation',
            'shopping_mall': 'Shopping',
            'transit_station': 'Transportation'
        }
        
        for poi_type, places in grouped.items():
            label = type_labels.get(poi_type, poi_type)
            top_places = places[:2]
            place_names = [p['name'] for p in top_places]
            sections.append(f"{label}: {', '.join(place_names)}")
        
        return f"Nearby amenities include: {' | '.join(sections)}."

google_maps_service = GoogleMapsService()
