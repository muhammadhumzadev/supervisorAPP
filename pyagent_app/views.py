from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Include the ChatGPT class definition as previously provided
import os
import openai
import time

timestamp = time.strftime("%Y%m%d_%H%M%S")
directory_name = f"f_{timestamp}"
if not os.path.exists(f"./workspace/{directory_name}"):
    os.makedirs(f"./workspace/{directory_name}")
    print(f"Directory '{directory_name}' created")
else:
    print(f"Directory '{directory_name}' already exists")

file_name = os.path.join(f"./workspace/{directory_name}", f"my_file_{timestamp}.txt")
if not os.path.exists(file_name):
    with open(file_name, 'w') as f:
        f.write("This is my file\n")
        print(f"File '{file_name}' created")
else:
    print(f"File '{file_name}' already exists")



class ChatGPT:
    def __init__(self, api_key, chatbot):
        self.api_key = api_key  # Set the API key
        self.chatbot = chatbot  # Set the chatbot prompt
        self.conversation = []  # Initialize the conversation history

    def chat(self, user_input):
        # Add the user's input to the conversation history
        self.conversation.append({"role": "user", "content": user_input})

        # Get the chatbot's response
        response = self.chatgpt_with_retry(self.conversation, self.chatbot, user_input)

        # Add the chatbot's response to the conversation history
        self.conversation.append({"role": "assistant", "content": response})
        return response

    def chatgpt(self, conversation, chatbot, user_input, temperature=0.75, frequency_penalty=0.2, presence_penalty=0):
        # Set the API key for OpenAI
        openai.api_key = self.api_key

        # Prepare the input messages for the API call
        messages_input = conversation.copy()
        prompt = [{"role": "system", "content": chatbot}]
        messages_input.insert(0, prompt[0])

        # Call the OpenAI API to get a response
        completion = openai.Completion.create(
            engine="text-davinci-003",  # Use the text-davinci-003 model
            prompt="\n".join([msg["content"] for msg in messages_input]),
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=1024,
            n=1,
            stop=None,
            timeout=None,
        )

        # Extract the chat response from the API response
        chat_response = completion.choices[0].text.strip()
        return chat_response

    def chatgpt_with_retry(self, conversation, chatbot, user_input, temperature=0.75, frequency_penalty=0.2, presence_penalty=0, retries=3):
        # Retry the chatgpt function if there's an exception
        for i in range(retries):
            try:
                return self.chatgpt(conversation, chatbot, user_input, temperature, frequency_penalty, presence_penalty)
            except Exception as e:
                if i < retries - 1:
                    print(f"Error in chatgpt attempt {i + 1}: {e}. Retrying...")
                else:
                    print(f"Error in chatgpt attempt {i + 1}: {e}. No more retries.")
        return None



def index(request):
    return render(request, "index.html")

@csrf_exempt
def chat(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        api_key = request.POST.get("api_key")
        chatbot1_prompt = request.POST.get("chatbot1_prompt")
        chatbot2_prompt = request.POST.get("chatbot2_prompt")
        
        if not all([user_input, api_key, chatbot1_prompt, chatbot2_prompt]):
            return JsonResponse({"error": "Missing input parameters"}, status=400)
            
        

        chatbot1 = ChatGPT(api_key, chatbot1_prompt)
        chatbot2 = ChatGPT(api_key, chatbot2_prompt)

        chatbot1_response = chatbot1.chat(user_input)
        with open(file_name, 'a') as f:
                    f.write(chatbot1_response + "\n")
        chatbot2_response = chatbot2.chat(chatbot1_response)
        with open(file_name, 'a') as f:
                    f.write(chatbot2_response + "\n")

        return JsonResponse({"response1": chatbot1_response, "response2": chatbot2_response})

    return render(request, "index.html")
