from typing import Optional, Tuple, List
from common_ai_core.providers import ProviderType, LLMProvider
from common_ai_core.types import Message, Role
import logging

logger = logging.getLogger('common_ai_core')

class ModelPricing:
    def __init__(self, input_price: float, output_price: float):
        self.input_price = input_price  # USD per 1K tokens
        self.output_price = output_price  # USD per 1K tokens

class TokenTracker:
    """Håller koll på token-användning och kostnader"""
    
    def __init__(self, 
                 pricing: Optional[ModelPricing] = None,
                 verbose: bool = False):
        self.pricing = pricing
        self.verbose = verbose
        self.logger = logging.getLogger(f'common_ai_core.{self.__class__.__name__}')
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        
        # Token counts
        self.input_tokens = 0
        self.output_tokens = 0

    def add(self, input_tokens: int, output_tokens: int):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def get_token_counts(self) -> Tuple[int, int]:
        """Returnera totalt antal tokens (input, output)"""
        return self.input_tokens, self.output_tokens

    def get_cost_estimate(self) -> Optional[float]:
        """Beräkna kostnad baserat på token-användning"""
        if not self.pricing:
            return None
        input_cost = (self.input_tokens / 1000) * self.pricing.input_price
        output_cost = (self.output_tokens / 1000) * self.pricing.output_price
        return input_cost + output_cost

