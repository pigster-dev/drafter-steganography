from drafter import *
from bakery import assert_equal
from dataclasses import dataclass
from PIL import Image

set_website_title("S T E G A N O G R A P H Y")
set_site_information(
    author = "Tyler S.",
    description - "Simple site to encode and decode an image with a message using steganography",
    sources = "Drafter docs, Drafter Tutor model, and a nice Geeks for Geeks article about Python Steganography",
    planning = "plan.pdf"
    links = []
)
hide_debug_information()


@dataclass
class Message:
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
    image: Image
    encoded_image : Image

# pages
@route
def index(state: State) -> Page:
    '''Main title page'''
    return Page(state,
                [Header("S T E G A N O G R A P H Y"),
                 Button("Encode", "encode_page"),
                 Button("Decode", "decode_page")])

@route
def encode_page(state: State) -> Page:
    '''Page to upload an image and enter a message for encoding'''
    return Page(state,
                [Header("E N C O D E"),
                 "Enter a message...",
                 TextBox("message_box"),
                 Button("Home", "index")])

@route
def decode_page(state: State) -> Page:
    '''Page to upload an encoded image to decode'''
    return Page(state,
                [Header("D E C O D E"),
                 Button("Home", "index")])


                        
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



start_server(State(Message("",[]),[],"default_img.png","default_image.png"))