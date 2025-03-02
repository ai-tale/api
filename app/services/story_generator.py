import openai
import json
import logging
from typing import Dict, List, Any, Optional

from app.core.config import settings

logger = logging.getLogger("aitale_api")

class StoryGenerator:
    """Service for generating stories using OpenAI's API."""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        if settings.OPENAI_ORG_ID:
            openai.organization = settings.OPENAI_ORG_ID
        self.model = settings.STORY_GEN_MODEL
    
    async def generate_story(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a story based on the provided parameters."""
        try:
            # Build the prompt for the story generation
            prompt = self._build_prompt(parameters)
            
            # Call OpenAI to generate the story
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert storyteller specializing in children's fairy tales that are imaginative, engaging, and suitable for the target age group."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=settings.MAX_STORY_LENGTH,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            
            # Extract the generated story
            story_text = response.choices[0].message.content.strip()
            
            # Process the story into pages
            pages = self._split_into_pages(story_text)
            
            # Generate image prompts for each page
            image_prompts = await self._generate_image_prompts(pages)
            
            return {
                "full_text": story_text,
                "pages": [
                    {
                        "number": i + 1,
                        "content": page,
                        "image_prompt": image_prompts[i] if i < len(image_prompts) else None
                    }
                    for i, page in enumerate(pages)
                ]
            }
        
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise
    
    def _build_prompt(self, parameters: Dict[str, Any]) -> str:
        """Build a prompt for story generation based on parameters."""
        # Extract parameters with defaults
        title = parameters.get("title", "")
        theme = parameters.get("theme", "")
        age_group = parameters.get("age_group", "children")
        characters = parameters.get("characters", [])
        setting = parameters.get("setting", "")
        mood = parameters.get("mood", "happy")
        length = parameters.get("length", "medium")
        style = parameters.get("style", "fairy tale")
        custom_prompt = parameters.get("custom_prompt", "")
        
        # Map length to approximate page count
        page_counts = {
            "short": "3-5 pages",
            "medium": "6-10 pages",
            "long": "11-15 pages"
        }
        page_count = page_counts.get(length, "6-10 pages")
        
        # Build the prompt
        prompt_parts = [
            "Create a delightful children's story with the following characteristics:",
            f"Length: {page_count}"
        ]
        
        if title:
            prompt_parts.append(f"Title: {title}")
        
        if theme:
            prompt_parts.append(f"Theme: {theme}")
            
        if age_group:
            prompt_parts.append(f"Target audience: {age_group}")
            
        if characters:
            prompt_parts.append(f"Characters: {', '.join(characters)}")
            
        if setting:
            prompt_parts.append(f"Setting: {setting}")
            
        if mood:
            prompt_parts.append(f"Mood: {mood}")
            
        if style:
            prompt_parts.append(f"Style: {style}")
            
        if custom_prompt:
            prompt_parts.append(f"Additional instructions: {custom_prompt}")
        
        prompt_parts.append(
            "Format the story into clearly separated pages suitable for a children's book. "
            "Each page should have a cohesive scene that works well with an illustration."
        )
        
        return "\n".join(prompt_parts)
    
    def _split_into_pages(self, text: str) -> List[str]:
        """Split the generated story into pages."""
        # First try to find page markers
        if "PAGE " in text or "Page " in text:
            pages = []
            current_page = ""
            lines = text.split('\n')
            
            for line in lines:
                if line.startswith(("PAGE ", "Page ")) and current_page:
                    pages.append(current_page.strip())
                    current_page = line
                else:
                    current_page += line + "\n"
            
            if current_page:
                pages.append(current_page.strip())
            
            # Clean up page markers
            pages = [p.replace("PAGE ", "", 1).replace("Page ", "", 1) if p.startswith(("PAGE ", "Page ")) else p for p in pages]
            
            return pages
        
        # If no page markers, split by paragraphs
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        # Combine paragraphs into pages (2-3 paragraphs per page)
        pages = []
        current_page = ""
        para_count = 0
        
        for para in paragraphs:
            current_page += para + "\n\n"
            para_count += 1
            
            if para_count >= 2:
                pages.append(current_page.strip())
                current_page = ""
                para_count = 0
        
        if current_page:
            pages.append(current_page.strip())
        
        return pages
    
    async def _generate_image_prompts(self, pages: List[str]) -> List[str]:
        """Generate image prompts for each page."""
        prompts = []
        
        for page in pages:
            try:
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert at creating descriptive prompts for AI image generation based on story text."},
                        {"role": "user", "content": f"Create a vivid, detailed prompt for an AI image generator to illustrate the following page from a children's story. Focus on the main scene, characters, and setting. Make it detailed but concise, emphasizing the style of a children's book illustration:\n\n{page}"}
                    ],
                    temperature=0.7,
                    max_tokens=150,
                    top_p=1
                )
                
                prompt = response.choices[0].message.content.strip()
                prompts.append(prompt)
                
            except Exception as e:
                logger.error(f"Error generating image prompt: {str(e)}")
                prompts.append(f"Illustration for children's story: {page[:100]}...")
        
        return prompts 