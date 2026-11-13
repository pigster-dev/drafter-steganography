# import statements
from drafter import *
from bakery import assert_equal
from dataclasses import dataclass
from PIL import Image as PIL_Image
import io

# website info
set_website_title("S T E G A N O G R A P H Y")
set_site_information(
    author = "Tyler S.",
    description = "Simple site to encode and decode an image with a message using steganography",
    sources = "Thanks to Drafter docs, Drafter Tutor model, and a nice Geeks for Geeks article about Python Steganography",
    planning = ["plan1.pdf", "plan0.pdf"],
    links = ["https://github.com/pigster-dev/drafter-steganography/blob/main/plan1s.pdf",
             "https://github.com/pigster-dev/drafter-steganography/blob/main/plan0.pdf"]
)
hide_debug_information()
set_website_framed(False)


@dataclass
class Message:
    '''
    dataclass for messages that contains both the text of the message and a list containing
    binary representation of each character
    '''
    plaintext : str
    binary: list[str]
    
@dataclass
class State:
    '''
    The purpose of this site is to utilize steganography techniques to encode
    a message within an image. Additionally, the site will be able to decode
    these same images to retrieve the message.
    '''
    message : Message
    message_log : list[Message]
    image: PIL_Image.Image
    encoded_image : PIL_Image.Image

# pages
@route
def index(state: State) -> Page:
    '''Main title page'''
    return Page(state,
                [Header("S T E G A N O G R A P H Y"),
                 Button("Encode", "encode_page"),
                 Button("Decode", "decode_page"),
                 Button("Message History", "history_page")
                 ])

@route
def encode_page(state: State) -> Page:
    '''Page to upload an image for encoding'''
    return Page(state,
                [Header("E N C O D E"),
                 "Upload an image...",
                 FileUpload("image_file", accept="image/*"),
                 Button("Submit", "upload_image"),
                 Button("Home", "index")])

@route
def decode_page(state: State) -> Page:
    '''Page to upload an encoded image to decode'''
    return Page(state, [
        Header("D E C O D E"),
        "Upload an encoded image...",
        FileUpload("image_file", accept="image/*"),
        Button("Submit", "upload_encoded_image"),
        Button("Home", "index")
    ])

@route
def upload_encoded_image(state: State, image_file: bytes) -> Page:
    '''
    Returns page containing the uploaded encoded image and the final decoded message.
    Additionally, this uploads the decoded mesage to the log, including the binary
    '''
    state.encoded_image = PIL_Image.open(io.BytesIO(image_file)).convert("RGB")

    state.message = decode_message(state.encoded_image)

    # append decoded message to the log
    state.message_log.append(Message(state.message.plaintext, state.message.binary.copy()))

    return Page(state, [
        Header("D E C O D E D"),
        Image(state.encoded_image),
        "Your hidden message is:",
        state.message.plaintext,
        Button("Home", "index")
    ])

@route
def encode(state: State, message: str) -> Page:
    '''
    returns page displaying the original and encoded image
    '''
    # Convert the message into binary
    binary_list = string_to_binary(message)
    # Store the message information
    state.message = Message(message, binary_list)
    # Encode the image
    state.encoded_image = encode_message(state.image, message)

    return Page(state, [
        Header("E N C O D I N G S U C C E S S"),
        "Original image:",
        Image(state.image),
        "Encoded image:",
        Image(state.encoded_image),
        "Message:",
        state.message.plaintext,
        "Binary:",
        str(state.message.binary),
        Download("Download Image", "secret.png", state.encoded_image),
        Button("Home", "index")
    ])

@route
def upload_image(state: State, image_file: bytes) -> Page:
    '''
    Page that displays after an image has been uploaded, allowing the user to then implement
    a message for encoding into said uploaded image.
    '''
    # Convert the uploaded bytes into a PIL image
    state.image = PIL_Image.open(io.BytesIO(image_file)).convert("RGB")

    return Page(state, [
        Header("E N C O D E"),
        Image(state.image),
        "Your image is ready!",
        "Enter your secret message:",
        TextBox("message"),
        Button("Encode Message", "encode"),
        Button("Home", "index")
    ])

@route
def history_page(state: State) -> Page:
    '''
    page that containes a log of successfully decoded messages.
    '''
    content = [
        Header("M E S S A G E H I S T O R Y")
    ]

    for message in state.message_log:
        content.append("Message: " + message.plaintext)
        content.append("Binary: " + str(message.binary))
        content.append(HorizontalRule())

    if len(state.message_log) == 0:
        content.append("No messages have been encoded or decoded yet.")

    content.append(Button("Home", "index"))

    return Page(state, content)
           
           
# functions                        
@route
def string_to_binary(plaintext : str) -> list[str]:
    '''
    Intakes a plaintext string and returns a list of strings that contains
    each character of the plaintext converted into binary.
    '''
    binary_list = []

    for character in plaintext:
        binary = format(ord(character), "08b")
        binary_list.append(binary)

    return binary_list

assert_equal(string_to_binary("Hi"), ["01001000", "01101001"])
assert_equal(string_to_binary(""), [])

@route
def message_to_binary(message: str) -> str:
    '''
    takes the list of strings from string_to_binary and iterates to create one continuous
    string containing all of the binary character representations.
    '''
    binary_list = string_to_binary(message)

    binary_message = ""

    for binary in binary_list:
        binary_message += binary

    return binary_message

@route
def image_to_binary(image: PIL_Image.Image) -> str:
    '''
    iterates through the image's RGB values (image.convert("RGB")) and converts those values
    into binary values to later be used in the decoding process.
    '''
    image = image.convert("RGB")

    width, height = image.size
    pixels = image.load()

    binary_message = ""

    for y in range(height):
        for x in range(width):
            red, green, blue = pixels[x, y]

            binary_message += str(red % 2)
            binary_message += str(green % 2)
            binary_message += str(blue % 2)

    return binary_message

@route
def encode_message(image: PIL_Image, message: str) -> PIL_Image:
    '''
    intakes an image and the message, and iterates through the image's pixels to modify
    the pixels, encoding the provided message using least siginficant bit encryption.
    '''
    binary_message = message_to_binary(message)
    message_length = format(len(binary_message), "032b") # Store the length of the message as 32 bits
    binary_data = message_length + binary_message # Combine the length and the actual message
    image = image.convert("RGB").copy() # ensure RGB image is being used

    width, height = image.size
    pixels = image.load()

    bit_index = 0

    for y in range(height):
        for x in range(width):
            red, green, blue = pixels[x, y]

            # Put the pixel's color values into a list
            color_values = [red, green, blue]

            # Each pixel can store 3 bits
            for channel_index in range(3):
                if bit_index < len(binary_data):
                    bit = binary_data[bit_index]

                    value = color_values[channel_index]

                    # Change the last bit if necessary
                    if bit == "0" and value % 2 == 1:
                        value -= 1
                    elif bit == "1" and value % 2 == 0:
                        value += 1

                    color_values[channel_index] = value
                    bit_index += 1

            # Save the modified pixel
            pixels[x, y] = (
                color_values[0],
                color_values[1],
                color_values[2]
            )
    return image

@route
def binary_to_message(binary_message: str) -> str:
    '''
    intakes a string (that is the message in binary form) and returns it as the message
    in plaintext rather than in binary.
    '''
    plaintext = ""

    for index in range(0, len(binary_message), 8):
        binary_character = binary_message[index:index + 8]

        character_number = int(binary_character, 2)
        character = chr(character_number)

        plaintext += character

    return plaintext

assert_equal(binary_to_message("0100100001101001"), "Hi")

@route
def decode_message(image: PIL_Image.Image) -> Message:
    '''
    intakes the secret encoded image and returns the decoded message.
    '''
    binary_data = image_to_binary(image)

    message_length_binary = binary_data[:32] # The first 32 bits denote the message length
    message_length = int(message_length_binary, 2)

    binary_message = binary_data[32:32 + message_length]

    plaintext = binary_to_message(binary_message) # convert the binary back into plaintext using helper function

    # for storing each character as an individual binary string
    binary_list = []

    for index in range(0, len(binary_message), 8):
        binary_character = binary_message[index:index + 8]
        binary_list.append(binary_character)

    return Message(plaintext, binary_list)

#assert equal test cases
assert_equal(binary_to_message("01001000"), "H")
assert_equal(binary_to_message("0100100001101001"),"Hi")
assert_equal(message_to_binary("Hi"), "0100100001101001")

test_image = PIL_Image.new("RGB", (100, 100))
encoded = encode_message(test_image, "Hello")
decoded = decode_message(encoded)
assert_equal(decoded.plaintext, "Hello")

#start server function with blank data and a default image.
blank_image = PIL_Image.new("RGB", (10,10))

start_server(State(Message("",[]),[],blank_image,blank_image.copy()))