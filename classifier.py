"""
Email Classification Module

Classifies emails as "Spam" or "Safe" using keyword matching.
Designed to be extensible for LLM-based classification in the future.
"""

import os
from dotenv import load_dotenv


class EmailClassifier:
    """Classifies emails as spam or safe."""
    
    def __init__(self):
        """
        Initialize the email classifier with spam keywords.
        Loads environment variables for potential LLM API keys.
        """
        # Load environment variables (for future LLM integration)
        load_dotenv()
        
        # Spam keywords for keyword-based classification
        self.spam_keywords = [
            'urgent',
            'lottery',
            'wire transfer',
            'click here',
            'limited time',
            'act now',
            'winner',
            'prize',
            'congratulations',
            'free money',
            'claim now',
            'expires soon',
            'guaranteed',
            'risk-free',
            'no obligation',
            'limited offer',
            'exclusive deal',
            'one-time offer',
            'act immediately',
            'don\'t miss out'
        ]
        
        # Optional: Load LLM API keys for future integration
        # self.openai_api_key = os.getenv('OPENAI_API_KEY')
        # self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    
    def analyze_email(self, subject, body):
        """
        Analyze email and determine if it's spam.
        
        Args:
            subject (str): Email subject line
            body (str): Email body content
            
        Returns:
            tuple: (is_spam: bool, confidence: float)
                - is_spam: True if email is classified as spam, False otherwise
                - confidence: Confidence score between 0.0 and 1.0
        """
        # TODO: Future LLM-based classification
        # Uncomment and implement when ready to use OpenAI:
        # if self.openai_api_key:
        #     return self._classify_with_openai(subject, body)
        
        # TODO: Future LLM-based classification
        # Uncomment and implement when ready to use Anthropic:
        # if self.anthropic_api_key:
        #     return self._classify_with_anthropic(subject, body)
        
        # Current implementation: Keyword-based matching
        return self._classify_with_keywords(subject, body)
    
    def _classify_with_keywords(self, subject, body):
        """
        Classify email using keyword matching.
        
        Args:
            subject (str): Email subject line
            body (str): Email body content
            
        Returns:
            tuple: (is_spam: bool, confidence: float)
        """
        # Combine subject and body for analysis
        text = f"{subject} {body}".lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in self.spam_keywords if keyword.lower() in text)
        
        # Calculate confidence based on number of matches
        # More matches = higher confidence
        # Formula: min(1.0, (matches / total_keywords) * 2.0)
        # This gives higher weight to matches (multiplier of 2.0)
        total_keywords = len(self.spam_keywords)
        confidence = min(1.0, (matches / total_keywords) * 2.0) if total_keywords > 0 else 0.0
        
        # Classify as spam if at least one keyword matches
        is_spam = matches > 0
        
        return is_spam, confidence
    
    # TODO: Implement OpenAI-based classification
    # def _classify_with_openai(self, subject, body):
    #     """
    #     Classify email using OpenAI API.
    #     
    #     Args:
    #         subject (str): Email subject line
    #         body (str): Email body content
    #     
    #     Returns:
    #         tuple: (is_spam: bool, confidence: float)
    #     """
    #     # Implementation example:
    #     # import openai
    #     # openai.api_key = self.openai_api_key
    #     # 
    #     # prompt = f"Classify this email as spam or safe. Subject: {subject}\nBody: {body[:500]}"
    #     # response = openai.ChatCompletion.create(...)
    #     # 
    #     # Parse response and return (is_spam, confidence)
    #     pass
    
    # TODO: Implement Anthropic-based classification
    # def _classify_with_anthropic(self, subject, body):
    #     """
    #     Classify email using Anthropic API.
    #     
    #     Args:
    #         subject (str): Email subject line
    #         body (str): Email body content
    #     
    #     Returns:
    #         tuple: (is_spam: bool, confidence: float)
    #     """
    #     # Implementation example:
    #     # import anthropic
    #     # client = anthropic.Anthropic(api_key=self.anthropic_api_key)
    #     # 
    #     # message = client.messages.create(...)
    #     # 
    #     # Parse response and return (is_spam, confidence)
    #     pass
