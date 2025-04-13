import google.generativeai as genai
import time

# Read API key
with open("D:\\Projects\\Eden\\AIFriday\\Data\\Api.txt", 'r') as file:
    API = file.read().strip()

# Configure with error handling
try:
    genai.configure(api_key=API)
except Exception as e:
    print(f"API configuration error: {e}")
    exit(1)

def BrainReply(questions, chat_log=None):
    try:
        with open("D:\\Projects\\Eden\\AIFriday\\Database\\chat_log.txt", "r") as file:
            chat_log_template = file.read()
        
        if chat_log is None:
            chat_log = chat_log_template

        prompt = f'{chat_log}You : {questions}\nFriday :'
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        time.sleep(1)  # Add small delay to prevent rate limiting
        
        response = model.generate_content(prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                top_p=0.3,
                max_output_tokens=60
            )
        )
        
        answer = response.text.strip()
        chat_log_template_update = chat_log_template + f"\nYou : {questions} \nFriday : {answer}"
        
        with open("D:\\Projects\\Eden\\AIFriday\\Database\\chat_log.txt", 'w') as file:
            file.write(chat_log_template_update)
        
        return answer
    
    except Exception as e:
        print(f"Error in BrainReply: {e}")
        return "Sorry, I encountered an error."

