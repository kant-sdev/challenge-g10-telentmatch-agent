from app.services.gemini.client import GeminiClient
from app.services.gemini.prompts import RESUME_EXTRACTION_PROMPT
from app.services.gemini.models import CandidateProfile


class GeminiExtractor:

    def __init__(self):

        self.client = GeminiClient()

    def extract(self, resume: str) -> CandidateProfile:

        prompt = RESUME_EXTRACTION_PROMPT.format(
            resume=resume
        )

        return self.client.generate_profile(prompt)