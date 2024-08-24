import google.generativeai as genai
from config import GEMINI_API_KEY
import json

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_item_effects(item_id):
    prompt = f"""
    Generate realistic effects for using a {item_id} in a survival game. Consider:
    1. How it affects thirst, hunger, comfort, and energy (positive or negative).
    2. Its impact on the environment (positive or negative).

    Respond with a JSON object in this exact format:
    {{
        "status_bars": {{
            "thirst": <value between -100 and 100>,
            "hunger": <value between -100 and 100>,
            "comfort": <value between -100 and 100>,
            "energy": <value between -100 and 100>
        }},
        "environment_points": <value between -100 and 100>
    }}
    """

    try:
        response = model.generate_content(prompt)
        effects = json.loads(response.text)
        
        # Ensure all required keys are present
        required_keys = ['status_bars', 'environment_points']
        status_bar_keys = ['thirst', 'hunger', 'comfort', 'energy']
        
        if all(key in effects for key in required_keys) and all(key in effects['status_bars'] for key in status_bar_keys):
            return effects
        else:
            raise ValueError("Invalid response format")
    
    except Exception as e:
        print(f"Error generating item effects: {e}")
        return {
            'status_bars': {
                'thirst': 0,
                'hunger': 0,
                'comfort': 0,
                'energy': 0
            },
            'environment_points': 0
        }