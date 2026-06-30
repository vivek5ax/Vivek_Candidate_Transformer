import spacy
import logging

logger = logging.getLogger(__name__)

class AIValidator:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("en_core_web_sm not found. Falling back to blank model.")
            self.nlp = spacy.blank("en")

    def is_valid_organization(self, text: str) -> bool:
        """
        Check if the text predominantly contains an ORG (Organization).
        If the text is entirely a DATE, returns False.
        """
        if not text:
            return False
        
        doc = self.nlp(text)
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        
        # If it's literally just a date string, it's not an ORG.
        if dates and not orgs and len(text) < 30:
            return False
            
        return True

    def extract_org_and_title(self, texts: list[str]) -> tuple[str | None, str | None]:
        """
        Given a list of bold text lines representing a job header, use spaCy to classify ORG vs Title.
        Returns: (Company, Title)
        """
        if not texts:
            return None, None
            
        company = None
        title = None
        
        # If there are multiple lines, check which one is ORG
        for text in texts:
            doc = self.nlp(text)
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if orgs and not company:
                company = text
            elif not title:
                title = text
            elif not company:
                company = text # Fallback
                
        # If only one line was given, and we didn't split it, it's usually the title for freelancers
        if len(texts) == 1 and not company and title:
            pass # Keep it as title
            
        return company, title

    def is_valid_date(self, text: str) -> bool:
        """
        Check if the text contains a DATE entity.
        """
        if not text:
            return False
            
        doc = self.nlp(text)
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        
        if dates:
            return True
            
        # Fallback check for year-like digits
        import re
        if re.search(r'\b(19|20)\d{2}\b', text):
            return True
            
        return False

    def is_technology_list(self, text: str) -> bool:
        """
        Check if a string is actually just a list of technologies.
        (e.g., 'Technologies Used: React, Django, MongoDB')
        """
        if not text:
            return False
            
        lower_text = text.lower()
        if lower_text.startswith("technologies used") or lower_text.startswith("tech stack"):
            return True
            
        # If it's a comma separated list of tech
        if len(text.split(',')) >= 4 and len(text) < 100:
            return True
            
        return False

# Singleton instance
ai_validator = AIValidator()
