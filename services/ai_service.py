import google.generativeai as genai
import os
import json

api_key = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

def parse_segment_prompt(prompt: str) -> dict:
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.")
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    system_prompt = (
        "You are an AI assistant that extracts customer segmentation criteria from natural language prompts.\n"
        "Your output must be a valid JSON object only, with no markdown formatting (like ```json), no explanations, and no surrounding text.\n"
        "The JSON object must have exactly these keys: \"min_spend\" (float or null), \"inactive_days\" (integer or null), and \"city\" (string or null).\n"
        "If currency is in Rupees (e.g. ₹5000), extract it as a numeric value (e.g. 5000).\n"
        "Examples:\n"
        "Input: \"Customers who spent more than ₹5000 and haven't purchased in 60 days\"\n"
        "Output: {\"min_spend\": 5000, \"inactive_days\": 60, \"city\": null}\n"
    )
    response = model.generate_content(f"{system_prompt}\nInput: \"{prompt}\"")
    response_text = response.text.strip()
    
    if response_text.startswith("```"):
        response_text = response_text.strip("`").replace("json", "", 1).strip()
        
    return json.loads(response_text)

def generate_campaign_message(prompt: str) -> str:
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.")
        
    model = genai.GenerativeModel("gemini-1.5-flash")
    ai_prompt = (
        f"Generate a campaign message based on this prompt: '{prompt}'.\n"
        "Keep it short, professional, and copy-focused. Return only the campaign message body without any introductory text, markdown formatting, or greetings like 'Here is the campaign:'."
    )
    response = model.generate_content(ai_prompt)
    message_text = response.text.strip()
    if message_text.startswith("```"):
        message_text = "\n".join(message_text.split("\n")[1:-1])
    return message_text

def generate_customer_persona(customer_name: str, city: str, total_spend: float, total_orders: int, orders: list) -> str:
    if not api_key:
        return f"{customer_name} is a customer based in {city} who has placed {total_orders} order(s) with a total lifetime spend of ${total_spend:.2f}."
        
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        orders_desc = ", ".join([f"${o.amount} on {o.order_date}" for o in orders[:5]])
        ai_prompt = (
            f"Generate a short buying persona summary for customer '{customer_name}' from '{city}'.\n"
            f"Key metrics: Total spend: ${total_spend:.2f}, Total orders: {total_orders}.\n"
            f"Recent orders: [{orders_desc}].\n"
            "Keep the summary extremely professional, engaging, and copy-focused. Limit it to exactly 2 sentences summarizing their buying behavior, loyalty, and a potential engagement strategy. Do not mention any code, variables, or markdown formatting."
        )
        response = model.generate_content(ai_prompt)
        return response.text.strip()
    except Exception:
        return f"{customer_name} is a customer based in {city} who has placed {total_orders} order(s) with a total lifetime spend of ${total_spend:.2f}."

