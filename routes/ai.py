from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.ai_service import parse_segment_prompt, generate_campaign_message, get_api_key
from services.segment_service import get_segmented_customers
from routes.utils import templates

router = APIRouter()

@router.get("/ai-segment")
def ai_segment_page(request: Request):
    return templates.TemplateResponse(
        "ai_segment.html", 
        {
            "request": request, 
            "prompt": "", 
            "customers": [], 
            "parsed_filters": None,
            "error": None
        }
    )

@router.post("/ai-segment")
def handle_ai_segment(request: Request, prompt: str = Form(...), db: Session = Depends(get_db)):
    if not get_api_key():
        return templates.TemplateResponse(
            "ai_segment.html",
            {
                "request": request,
                "prompt": prompt,
                "customers": [],
                "parsed_filters": None,
                "error": "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file."
            }
        )
        
    try:
        filters = parse_segment_prompt(prompt)
    except Exception as e:
        return templates.TemplateResponse(
            "ai_segment.html",
            {
                "request": request,
                "prompt": prompt,
                "customers": [],
                "parsed_filters": None,
                "error": f"Failed to parse prompt with Gemini: {str(e)}"
            }
        )
        
    customers_data = get_segmented_customers(
        db,
        min_spend=filters.get("min_spend"),
        inactive_days=filters.get("inactive_days"),
        city=filters.get("city")
    )
        
    return templates.TemplateResponse(
        "ai_segment.html",
        {
            "request": request,
            "prompt": prompt,
            "customers": customers_data,
            "parsed_filters": filters,
            "error": None
        }
    )

@router.post("/campaigns/generate-message")
def generate_ai_message(prompt: str = Form(...)):
    try:
        message_text = generate_campaign_message(prompt)
        return {"message": message_text}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate message: {str(e)}")
