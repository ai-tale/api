import openai
import boto3
import logging
import os
import requests
import time
from io import BytesIO
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from PIL import Image

from app.core.config import settings

logger = logging.getLogger("aitale_api")

class ImageGenerator:
    """Service for generating images using OpenAI DALL-E."""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        if settings.OPENAI_ORG_ID:
            openai.organization = settings.OPENAI_ORG_ID
        
        self.model = settings.IMAGE_GEN_MODEL
        self.image_size = settings.IMAGE_SIZE
        self.image_quality = settings.IMAGE_QUALITY
        
        # Initialize S3 client if AWS credentials are provided
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.S3_BUCKET:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.s3_bucket = settings.S3_BUCKET
        else:
            self.s3_client = None
            self.s3_bucket = None
            
    async def generate_image(self, prompt: str, style: Optional[str] = None) -> Dict[str, Any]:
        """Generate an image based on the prompt."""
        try:
            # Enhance the prompt with style if provided
            if style:
                enhanced_prompt = f"{prompt}, {style} style, children's book illustration"
            else:
                enhanced_prompt = f"{prompt}, children's book illustration"
            
            # Call OpenAI to generate the image
            response = await openai.Image.acreate(
                model=self.model,
                prompt=enhanced_prompt,
                size=self.image_size,
                quality=self.image_quality,
                n=1
            )
            
            image_url = response['data'][0]['url']
            
            # Save to S3 if configured
            s3_url = None
            if self.s3_client and self.s3_bucket:
                s3_url = await self._save_to_s3(image_url, prompt)
            
            return {
                "url": image_url,
                "s3_url": s3_url,
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    async def _save_to_s3(self, image_url: str, prompt: str) -> str:
        """Save the generated image to S3."""
        try:
            # Download the image
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            
            # Create a unique filename
            filename = f"aitale-image-{int(time.time())}.png"
            
            # Save locally temporarily
            temp_path = f"/tmp/{filename}"
            image.save(temp_path, format="PNG")
            
            # Upload to S3
            object_key = f"images/{filename}"
            self.s3_client.upload_file(
                temp_path,
                self.s3_bucket,
                object_key,
                ExtraArgs={'ContentType': 'image/png'}
            )
            
            # Clean up temporary file
            os.remove(temp_path)
            
            # Return the S3 URL
            s3_url = f"https://{self.s3_bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{object_key}"
            return s3_url
            
        except Exception as e:
            logger.error(f"Error saving image to S3: {str(e)}")
            return None 