import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from config import INVENTORY_PATH, CAROUSEL_MAPPING_PATH

logger = logging.getLogger(__name__)

class KeywordMapper:
    """
    Maps keywords to carousel card indices based on inventory.json
    Implements smart keyword extraction with disambiguation for similar products.
    """
    
    def __init__(self, 
                 inventory_path=None,
                 carousel_map_path=None):
        """
        Initialize keyword mapper from inventory file.
        
        Args:
            inventory_path: Path to inventory.json
            carousel_map_path: Path to carousel mapping file
        """
        self.inventory_path = inventory_path or str(INVENTORY_PATH)
        carousel_map_path = carousel_map_path or str(CAROUSEL_MAPPING_PATH)
        
        self.inventory = self._load_inventory()
        self.carousel_mapping = self._load_carousel_mapping(carousel_map_path)
        self.keyword_map = self._build_keyword_map()
        
        logger.info(f"[KeywordMapper] Loaded {len(self.inventory)} products")
        logger.info(f"[KeywordMapper] Mapped {len(self.keyword_map)} unique keywords")
    
    def _load_inventory(self) -> List[Dict]:
        """Load inventory from JSON file"""
        try:
            with open(self.inventory_path, 'r') as f:
                data = json.load(f)
                # Handle both dict and list formats
                if isinstance(data, dict):
                    return data.get('equipment', [])
                elif isinstance(data, list):
                    return data
                else:
                    return []
        except FileNotFoundError:
            logger.warning(f"[KeywordMapper] Inventory file not found: {self.inventory_path}")
            return []
        except Exception as e:
            logger.warning(f"[KeywordMapper] Failed to load inventory: {e}")
            return []
    
    def _load_carousel_mapping(self, path: str) -> Dict[int, int]:
        """
        Load inventory-to-carousel index mapping.
        Returns dict: {inventory_index: carousel_index}
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Build reverse mapping: inventory_index -> carousel_index
                mapping = {}
                
                # Handle both list and dict formats
                if isinstance(data, list):
                    carousel_items = data
                else:
                    carousel_items = data.get('carousel_mapping', [])
                
                for item in carousel_items:
                    if isinstance(item, dict):
                        inv_idx = item.get('inventory_index')
                        car_idx = item.get('carousel_index')
                        if inv_idx is not None and car_idx is not None:
                            mapping[inv_idx] = car_idx
                return mapping
        except FileNotFoundError:
            logger.warning(f"[KeywordMapper] Carousel mapping not found, using direct indices")
            # Fallback: 1:1 mapping
            return {i: i for i in range(len(self.inventory))}
        except Exception as e:
            logger.warning(f"[KeywordMapper] Failed to load carousel mapping: {e}")
            # Fallback: 1:1 mapping
            return {i: i for i in range(len(self.inventory))}
    
    def _extract_keywords(self, product: Dict, index: int) -> List[str]:
        """
        Extract keywords for a single product with smart disambiguation.
        
        Args:
            product: Product dictionary from inventory
            index: Card index in carousel
            
        Returns:
            List of keyword strings (ordered by specificity, longest first)
        """
        keywords = []
        name = product.get('name', '')
        category = product.get('category', '')
        specs = product.get('specs', '')
        
        # 1. Full product name (highest priority)
        keywords.append(name.lower())
        
        # 2. Name without brand (e.g., "jetson orin nano" from "NVIDIA Jetson Orin Nano")
        name_no_brand = re.sub(r'^(nvidia|intel|raspberry|unitree|arduino)\s+', '', name, flags=re.IGNORECASE)
        if name_no_brand.lower() != name.lower():
            keywords.append(name_no_brand.lower())
        
        # 3. Disambiguating terms from specs
        # Extract key distinguishing features
        spec_keywords = self._extract_spec_keywords(name, specs)
        keywords.extend(spec_keywords)
        
        # 4. Category as fallback
        keywords.append(category.lower())
        
        # 5. Individual significant words (3+ chars, excluding common words)
        stop_words = {'the', 'and', 'with', 'for', 'from'}
        words = re.findall(r'\b\w{3,}\b', name.lower())
        for word in words:
            if word not in stop_words and word not in ['ltd', 'inc', 'corp']:
                keywords.append(word)
        
        # Remove duplicates while preserving order (longer phrases first)
        seen = set()
        unique_keywords = []
        for kw in sorted(keywords, key=len, reverse=True):
            kw_clean = kw.strip()
            if kw_clean and kw_clean not in seen:
                seen.add(kw_clean)
                unique_keywords.append(kw_clean)
        
        return unique_keywords
    
    def _extract_spec_keywords(self, name: str, specs: str) -> List[str]:
        """
        Extract disambiguating keywords from specs.
        
        Examples:
            - "4GB" for Jetson Nano vs "8GB" for Jetson Orin Nano
            - "Maxwell" vs "Ampere" for GPU architecture
            - "D435i" for specific RealSense model
        """
        spec_keywords = []
        
        # RAM sizes
        ram_match = re.search(r'(\d+GB)', name + ' ' + specs, re.IGNORECASE)
        if ram_match:
            spec_keywords.append(ram_match.group(1).lower())
        
        # Model numbers/suffixes
        model_match = re.search(r'([A-Z]\d+[A-Za-z]*)', name)
        if model_match:
            spec_keywords.append(model_match.group(1).lower())
        
        # Architecture names
        arch_keywords = ['maxwell', 'ampere', 'cortex', 'turing', 'pascal']
        for arch in arch_keywords:
            if arch in specs.lower():
                spec_keywords.append(arch)
        
        # Version numbers
        version_match = re.search(r'v(\d+)', name.lower())
        if version_match:
            spec_keywords.append(f"v{version_match.group(1)}")
        
        return spec_keywords
    
    def _build_keyword_map(self) -> Dict[str, int]:
        """
        Build mapping from keywords to card indices.
        Longer/more specific keywords have priority.
        
        Returns:
            Dictionary mapping keyword -> card_index
        """
        keyword_map = {}
        
        for idx, product in enumerate(self.inventory):
            keywords = self._extract_keywords(product, idx)
            
            logger.debug(f"[KeywordMapper] Card {idx}: {product['name']}")
            logger.debug(f"               Keywords: {keywords[:5]}")  # Log first 5
            
            for keyword in keywords:
                # Store mapping (later entries might overwrite, but we process in order)
                # For conflicts, the first product wins (earlier in inventory)
                if keyword not in keyword_map:
                    keyword_map[keyword] = idx
        
        return keyword_map
    
    def detect_keyword(self, text: str) -> Optional[Tuple[int, str]]:
        """
        Detect if text contains any mapped keywords.
        Returns the card index and matched keyword.
        
        Args:
            text: User input text (transcription)
            
        Returns:
            Tuple of (card_index, matched_keyword) or None if no match
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Sort keywords by length (longest first) for greedy matching
        sorted_keywords = sorted(self.keyword_map.keys(), key=len, reverse=True)
        
        for keyword in sorted_keywords:
            # Use word boundary matching for single words, substring for phrases
            if ' ' in keyword:
                # Multi-word phrase: substring match
                if keyword in text_lower:
                    inventory_idx = self.keyword_map[keyword]
                    # Convert to carousel index
                    carousel_idx = self.carousel_mapping.get(inventory_idx, inventory_idx)
                    logger.info(f"[🎯 KEYWORD MATCH] '{keyword}' → Card {carousel_idx} ({self.inventory[inventory_idx]['name']})")
                    return (carousel_idx, keyword)
            else:
                # Single word: word boundary match
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    inventory_idx = self.keyword_map[keyword]
                    # Convert to carousel index
                    carousel_idx = self.carousel_mapping.get(inventory_idx, inventory_idx)
                    logger.info(f"[🎯 KEYWORD MATCH] '{keyword}' → Card {carousel_idx} ({self.inventory[inventory_idx]['name']})")
                    return (carousel_idx, keyword)
        
        logger.debug(f"[KeywordMapper] No keyword match in: '{text}'")
        return None
    
    def get_product_name(self, card_index: int) -> str:
        """Get product name for a card index"""
        # Look up the inventory index from carousel mapping
        if card_index in self.carousel_to_inventory:
            inv_idx = self.carousel_to_inventory[card_index]
            if 0 <= inv_idx < len(self.inventory):
                return self.inventory[inv_idx]['name']
        return "Unknown"
