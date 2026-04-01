import logging
import aiohttp
from config import CONFIG

logger = logging.getLogger(__name__)

class QwenService:
    def __init__(self):
        self.api_key = CONFIG['api']['qwen_api_key']
        self.endpoint = CONFIG['api']['qwen_endpoint']
        self.model = CONFIG['api']['qwen_model']
        self.use_mock = CONFIG.get('mock_services', {}).get('ai_responses', False)
        
        if self.use_mock:
            logger.warning("Qwen AI is in mock mode - using simulated responses")
        elif not self.api_key or self.api_key.startswith('YOUR_'):
            logger.warning("Qwen API key not configured - falling back to mock mode")
            self.use_mock = True
    
    async def generate_description(self, listing_data: dict, tone: str, focus: str) -> str:
        if self.use_mock:
            logger.debug(f"Generating mock description (tone: {tone}, focus: {focus})")
            return self._mock_response(listing_data, tone, focus)
        
        prompt = self._build_prompt(listing_data, tone, focus)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        description = data['choices'][0]['message']['content']
                        logger.info(f"AI description generated successfully ({len(description)} chars)")
                        return description
                    else:
                        error_text = await self._handle_error(response)
                        logger.error(f"Qwen API error: {error_text}")
                        return error_text
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling Qwen API: {e}", exc_info=True)
            # Fallback to mock on network error
            return self._mock_response(listing_data, tone, focus)
        except Exception as e:
            logger.error(f"Unexpected error calling Qwen API: {e}", exc_info=True)
            # Fallback to mock on unexpected error
            return self._mock_response(listing_data, tone, focus)
    
    def _build_prompt(self, listing: dict, tone: str, focus: str) -> str:
        tone_prompt = CONFIG['description']['tones'].get(tone, '')
        min_words = CONFIG['description']['min_words']
        max_words = CONFIG['description']['max_words']
        
        prompt = f"""
        {tone_prompt}
        
        Property Details:
        - Type: {listing.get('property_type', 'Property')}
        - Address: {listing.get('address', '')} {listing.get('city', '')} {listing.get('state', '')}
        - Bedrooms: {listing.get('bedrooms', 'N/A')}
        - Bathrooms: {listing.get('bathrooms', 'N/A')}
        - Square Feet: {listing.get('square_feet', 'N/A')}
        - Price: ${listing.get('price', 'N/A'):,}
        - Description: {listing.get('description', '')}
        - Nearby Places: {listing.get('poi_text', '')}
        
        Focus: {focus} appeal
        
        Write between {min_words} and {max_words} words.
        Make it engaging and professional.
        """
        return prompt.strip()
    
    def _mock_response(self, listing: dict, tone: str, focus: str) -> str:
        templates = {
            'professional': f"""
            Presenting this exceptional {listing.get('property_type', 'property')} located in {listing.get('city', 'a prime location')}. 
            This {listing.get('bedrooms', 'multi-bedroom')} bedroom residence offers {listing.get('square_feet', 'spacious')} square feet 
            of thoughtfully designed living space. Priced at ${listing.get('price', '0'):,}, this property represents an outstanding opportunity.
            
            The home features modern amenities and is situated near excellent schools, shopping, and dining options. 
            Professional management and meticulous attention to detail make this an ideal choice for discerning buyers.
            """,
            'friendly': f"""
            Welcome home to this wonderful {listing.get('property_type', 'property')} in {listing.get('city', 'a lovely neighborhood')}! 
            With {listing.get('bedrooms', 'cozy')} bedrooms and {listing.get('bathrooms', 'modern')} bathrooms, this {listing.get('square_feet', 'comfortable')} sq ft home 
            has something for everyone. At ${listing.get('price', '0'):,}, it's a fantastic find!
            
            Imagine your mornings in this bright space, surrounded by nearby parks, cafes, and friendly neighbors. 
            This is more than a house—it's where your best memories will be made!
            """,
            'luxury': f"""
            Discover unparalleled elegance in this exquisite {listing.get('property_type', 'estate')} situated in the prestigious 
            {listing.get('city', 'location')}. This sophisticated {listing.get('bedrooms', 'multi-bedroom')} residence spans 
            {listing.get('square_feet', 'expansive')} square feet of refined living space.
            
            Offering ${listing.get('price', '0'):,} in value, this property features premium finishes, 
            state-of-the-art amenities, and breathtaking views. The epitome of luxury living awaits.
            """,
            'modern': f"""
            Experience contemporary living at its finest in this sleek {listing.get('property_type', 'property')} in {listing.get('city', 'the city')}. 
            This {listing.get('square_feet', 'spacious')} sq ft home features {listing.get('bedrooms', 'multiple')} bedrooms 
            with clean lines, open spaces, and smart home technology throughout.
            
            Priced at ${listing.get('price', '0'):,}, this modern masterpiece offers floor-to-ceiling windows, 
            premium appliances, and seamless indoor-outdoor flow. The future of living is here.
            """
        }
        
        return templates.get(tone, templates['professional']).strip()
    
    async def _handle_error(self, response) -> str:
        status = response.status
        if status == 401:
            return "Error: Invalid API key. Please check your configuration."
        elif status == 429:
            return "Error: Rate limit exceeded. Please try again later."
        elif status == 500:
            return "Error: Service temporarily unavailable. Please try again later."
        else:
            return f"Error: Unable to generate description (status {status}). Please try again."

qwen_service = QwenService()
