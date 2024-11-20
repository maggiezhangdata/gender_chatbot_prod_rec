from util import *
import urllib.parse

st.subheader("")

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai.default_headers = {"OpenAI-Beta": "assistants=v2"}
assistant_id = st.secrets["recbot_m_prod_m"]
print(assistant_id)
speed = 200

min_duration = 0
max_duration = 20
human_speed = 80

max_messages = 40
min_messages = 0

rec_times = 1
i = 0 


import requests
from PIL import Image
from io import BytesIO
import json

import requests
from concurrent.futures import ThreadPoolExecutor
import base64
from io import BytesIO

import requests
import base64
from PIL import Image
from io import BytesIO

class QuickImgurUploader:
    def __init__(self, client_id):
        """Initialize with your Imgur client ID"""
        self.client_id = client_id
        self.headers = {'Authorization': f'Client-ID {client_id}'}
        self.upload_url = 'https://api.imgur.com/3/image'

    def resize_image(self, image_bytes, size=(150, 150)):
        """Resize the image to the specified size"""
        try:
            img = Image.open(BytesIO(image_bytes))
            img_resized = img.resize(size)
            buffer = BytesIO()
            img_resized.save(buffer, format=img.format)
            buffer.seek(0)
            return buffer
        except Exception as e:
            print(f"Image resizing failed: {str(e)}")
            return None

    def upload_image(self, image_url):
        """Upload a single image from a URL to Imgur after resizing"""
        try:
            # Download the image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Resize the image
            resized_image = self.resize_image(response.content)
            if not resized_image:
                raise Exception("Failed to resize image")

            # Prepare the image for upload
            files = {'image': base64.b64encode(resized_image.getvalue())}

            # Upload to Imgur
            imgur_response = requests.post(
                self.upload_url,
                headers=self.headers,
                data=files
            )
            imgur_response.raise_for_status()
            
            # Return the Imgur URL
            return imgur_response.json()['data']['link']

        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return None

# Replace with your actual Imgur client ID
IMGUR_CLIENT_ID = '72939b1e567fb39'

# Initialize uploader
uploader = QuickImgurUploader(IMGUR_CLIENT_ID)


def generate_image(prompt, n:int=1, size:str="1024x1024"):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1
    )

    dalle_image_url = response.data[0].url
    
    print(f"Generated image URL: {dalle_image_url}")

    # Upload the resized image to Imgur
    imgur_url = uploader.upload_image(dalle_image_url)

    if imgur_url:
        print(f"Success! Image uploaded to Imgur: {imgur_url}")
    else:
        print("Image upload to Imgur failed")


    return imgur_url, None

    # print(f'image_url: {image_url}')


    # imgur_url = uploader.upload_image(image_url)

    # if imgur_url:
    #     print(f"Success! Image URL: {imgur_url}")
    # else:
    #     print("Upload failed")

    # # im = Image.open(requests.get(image_url, stream=True).raw)
    # im = None
    # # im.save("temp.png")
    # # st.image(im)
    # print(f'image_url: {image_url}')
    # print(f'-------- imgur_url: {imgur_url}')
    # return imgur_url, im


partner_names = 'Samuel'
partner_avatar = 'https://i.imgur.com/sXhLUV0.png'

user_avatar = 'https://i.imgur.com/TJfjrkI.png'
user_name = "You"



local_css("style.css")
init_session_state()

    


st.sidebar.markdown("Please start the conversation with the chatbot by typing :red[Hello] 👋  <br><br><br><br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("A thread ID will show up here after the AI finishes product recommendation. Please copy the thread ID and paste it into the text box below.", unsafe_allow_html=True)

thred_id_placeholder = st.sidebar.empty()
   
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"], avatar=user_avatar):
            st.empty()
            user_input = message["content"]
            st.markdown("<span style='color: red;'>" + user_name + "：</span>" + user_input, unsafe_allow_html=True)
            
    else:
        with st.chat_message(message["role"],avatar=partner_avatar):
            st.empty()
            partner_input = message["content"]
            st.markdown("<span style='color: red;'>" + partner_names + "：</span>" + partner_input, unsafe_allow_html=True)
        

if (not st.session_state.first_input_time) or (st.session_state.first_input_time and time.time() - st.session_state.first_input_time <= max_duration * 60):
    refresh_timer()
    user_input = st.chat_input("")

    if user_input:
        
            
        if not st.session_state.first_input_time:
            st.session_state.first_input_time = time.time()

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar=user_avatar):
            st.markdown("<span style='color: red;'>" + user_name + "：</span>" + user_input, unsafe_allow_html=True)

        with st.chat_message("assistant",avatar=partner_avatar):
            st.empty()
            message_placeholder = st.empty()
            waiting_message = st.empty()  # Create a new placeholder for the waiting message
            dots = 0
        
            import time
            
            try:
                update_typing_animation(waiting_message, 5,partner_names)  # Update typing animation
                message = openai.beta.threads.messages.create(thread_id=st.session_state.thread_id,role="user",content=user_input)
                run = openai.beta.threads.runs.create(
                        thread_id=st.session_state.thread_id,
                        assistant_id=assistant_id,
                        tools=[{
                            "type": "function",
                            "function": {
                                "name": "generate_image",
                                "description": "Generate image using DALL-E 3",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "prompt": {"type": "string", "description": "The prompt to generate image"},
                                        "size": {"type": "string", "enum": ["1024x1024", "1792x1024", "1024x1792"]}
                                    },
                                    "required": ["prompt"]
                                }
                            }
                        }]
                    )

                while True:
                    run_status = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
                    if run_status.status == "completed":
                        break
                    
                    elif run_status.status == "requires_action":
                        tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                        tool_outputs = []
                        for tool_call in tool_calls:
                            if tool_call.function.name == "generate_image":
                                args = json.loads(tool_call.function.arguments)
                                image_url,im = generate_image(args["prompt"], size=args.get("size", "1024x1024"))
                                print(f'image_url: {image_url}')
                                # st.image(im)
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": image_url
                                })
                        i += 1
                        if i >= rec_times:
                            st.sidebar.info(st.session_state.thread_id)
    
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=st.session_state.thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs,
                            stream=True
                        )


                    
                    elif run_status.status == "failed":
                        full_response = "Sorry, I encountered an error. Please try again."
                        if 'waiting_message' in locals():
                            waiting_message.empty()
                        break

                    # dots = update_typing_animation(waiting_message, dots,partner_names)
                    # time.sleep(0.3)
                # Retrieve and display messages
                messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                full_response = messages.data[0].content[0].text.value

                print(f'full_response: {full_response}')
                
                def delay_display(text):
                    # calculate the number of characters in the text
                    # get number of chinese characters
                    # return delay time in seconds
                    char_length = len(text)
                    print(f'char_length: {char_length}')
                    # delay = char_length / human_speed * 60
                    delay = 0
                    return delay
                
                wait_deplay = delay_display(full_response)
                print(f'wait_deplay: {wait_deplay}')
                
                def display_typing(placeholder, duration, gap):
                    # display typing message for a certain duration
                    interval = int(duration / (1/gap)) + 1
                    for i in range(interval):
                        num_dots = (i % 6) + 1  # Cycle through 1 to 3 dots
                        placeholder.markdown(f"Waiting for {partner_names}'s response" + "." * num_dots)
                        time.sleep(gap)
                        placeholder.empty()
                
                display_typing(waiting_message, int(wait_deplay), 0.5)
                    
                
                
                
                waiting_message.empty()
                
                
                
                
                
                message_placeholder.markdown("<span style='color: red;'>" + partner_names + "：</span>" + full_response, unsafe_allow_html=True)
            
            
            except Exception as e:
                print(e)
                error_message_html = """
                    <div style='display: inline-block; border:2px solid red; padding: 4px; border-radius: 5px; margin-bottom: 20px; color: red;'>
                        <strong>Network error:</strong> please try again.
                    </div>
                    """
                full_response = error_message_html
                waiting_message.empty()
                message_placeholder.markdown(full_response, unsafe_allow_html=True)

#------------------------------------------------------------------------------------------------------------------------------#


        


            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
    st.empty()
    st.empty()

else:
    st.sidebar.info(st.session_state.thread_id)
    if user_input := st.chat_input("", disabled=True):
        st.info("The time is up. Please copy the thread ID from the sidebar. Paste the thread ID into the text box below.")
        st.session_state.session_end = True



while True:
    if st.session_state.show_thread_id:
        thred_id_placeholder.info(st.session_state.thread_id)
    
    # thred_id_placeholder.info(st.session_state.thread_id)
    if st.session_state.session_end:
        st.session_state.show_thread_id = False
        break
    refresh_timer()
    time.sleep(0.6)  # Adjust this value as necessary for your use case