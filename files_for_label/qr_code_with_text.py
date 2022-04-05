import hashlib
import math

import qrcode

################### Add Here #####################
from PIL import Image, ImageDraw,ImageFont
import PIL
import zlib
import barcode
##################################################

def generate_hash_key(row, features_selected):
    # initialize hash_key as empty string
    hash_key = ""
    # concatenate values from given features to generate hash_key
    for feature in features_selected:
        hash_key += str(row[feature]) + "-"
    print(hash_key.encode())
    print(zlib.crc32(hash_key.encode()))
    # hash_key = hashlib.sha256(hash_key.encode()).hexdigest()
    hash_key = hex(zlib.crc32(hash_key.encode()))[2:] # new hash key - only 8 digits

    return hash_key

def test_fit_using_ttf_font(font_size, string, font_filename, available_width):
    font = ImageFont.truetype(font_filename, font_size)
    text_width, text_height = font.getsize(string)
    while not (text_width <= available_width and text_height <= 40):
        font_size -= 1
        font = ImageFont.truetype(font_filename, font_size)
        text_width, text_height = font.getsize(string)
        #print(f"font mask= {font.getmask(string).getbbox()}")
    print(f"text height={text_height}")
    return ImageFont.truetype(font_filename, font_size), font_size

def anchor_adjustment(desired_location, string, font): # find location for "la" given "ms"
    text_width, text_height = font.getsize(string)
    left_location = (desired_location[0] - text_width / 2, desired_location[1] - text_height)
    return left_location

def small_format(qr_img, obj, font_filename, background_filename):
    # setup values
    size_s = (223, 223) # size of the small label
    text_margin = 25
    qr_margin = 30
    qr_margin1 = 8
    qr_size = (size_s[0]-qr_margin*2, size_s[1]-qr_margin*2)
    qr_size_crop = (qr_margin1*2, qr_margin1*2, qr_size[0]-qr_margin1*2, qr_size[0]-qr_margin1*2)
    qr_location = (qr_margin + qr_margin1*2 + 5, qr_margin + qr_margin1*2  + 5)
    actual_margin = qr_margin*3 # max height for text around qr code

    text_mb_upper = (size_s[0]//2, text_margin) # the middle bottom location of text located at the upper margin
    text_mb_lower = (size_s[1]//2, size_s[1])


    fnt = ImageFont.truetype(font_filename, 24)
    #fnt = ImageFont.load_default() # anchor = "la"

    # get a background white image for label
    img = Image.open(background_filename)
    # resize it to a label size suitable for QR printer
    img = img.resize(size_s)

    # information needed
    experiment_id = obj["experiment_id"]
    temperature, PH = obj["storage_condition"].split(", ")
    date_entered = obj["date_entered"]
    analyst = obj["analyst"]


    # add text to the background
    draw = ImageDraw.Draw(img)
    msg1 = "Stored at: " + temperature
    msg2 = "Prep By: " + analyst
    msg3 = date_entered
    msg4 = experiment_id

    # rotated text at the left
    left_location = anchor_adjustment(text_mb_upper, msg1, fnt)
    draw.text(left_location, msg1, font=fnt, fill=0)
    # rotated text at the right
    left_location = anchor_adjustment(text_mb_lower, msg2, fnt)
    draw.text(left_location, msg2, font=fnt, fill=0)

    img = img.rotate(90)
    draw = ImageDraw.Draw(img)
    #test_fit(draw, font_size, string, font_file, img_bound)


    # text at the bottom
    left_location = anchor_adjustment(text_mb_lower, msg4, fnt)
    draw.text(left_location, msg4, font=fnt, fill=0)
    # text at the top
    left_location = anchor_adjustment(text_mb_upper, msg3, fnt)
    draw.text(left_location, msg3, font=fnt, fill=0)

    
    # resize the qr image to put on the background
    qr_img = qr_img.resize(qr_size)
    # crop the white margin of qr code
    qr_img = qr_img.crop(qr_size_crop)
    # add qr code image to the background
    img.paste(qr_img, qr_location) # left upper corner coordinates

    return img

def small_format2(qr_img, obj, font_filename, background_filename):
    # setup values
    size_l = (696, 223)  # size of the large label
    qr_margin = 40  # the pixel distance between right border of qr code and the right border of white background
    qr_size = (size_l[1] - 2 * qr_margin, size_l[1] - 2 * qr_margin)
    qr_location = (size_l[0] - qr_size[0], qr_margin)  # where the left upper corner of qr code is

    # get a background white image for label
    img = Image.open(background_filename)
    # resize it to a label size suitable for QR printer
    img = img.resize(size_l)
    # resize the qr image to put on the background
    qr_img = qr_img.resize(qr_size)
    img.paste(qr_img, qr_location)  # left upper corner coordinates

    draw = ImageDraw.Draw(img)

    # information needed
    experiment_id = obj["experiment_id"]
    storage_condition = obj["storage_condition"]
    contents = obj["contents"]
    date_entered = obj["date_entered"]
    expiration_date = obj["expiration_date"]
    analyst = obj["analyst"]

    msg_num = 4
    fnt_sizes = [25, 25, 25, 25]
    fnts = []
    for i in range(msg_num):
        fnts.append(ImageFont.truetype(font_filename, fnt_sizes[i]))

    # formatting
    lines = []
    lines.append(str(experiment_id))  # line 1: font size = 30
    lines.append("Prep " + str(date_entered))  # line 2: font size = 25
    lines.append("Prep By: " + analyst)  # line 3: font size = 25
    lines.append("Stored at: " + storage_condition) # line 4: font size = 25

    left_align = 200 # the pixel distance between the left of the text and the left of the border of white background
    available_width = size_l[0]

    # adjust font size to fit the available width
    fnt1_new, fnt1_size = test_fit_using_ttf_font(fnt_sizes[0], lines[0], font_filename, available_width)
    fnt2_new, fnt2_size = test_fit_using_ttf_font(fnt_sizes[1], lines[1], font_filename, available_width)
    fnt3_new, fnt3_size = test_fit_using_ttf_font(fnt_sizes[2], lines[2], font_filename, available_width)
    fnt4_new, fnt4_size = test_fit_using_ttf_font(fnt_sizes[3], lines[3], font_filename, available_width)

    line_heights = [60, 100, 140, 180]
    # draw texts line by line on the white background
    draw.text((left_align, line_heights[0]), lines[0], font=fnt1_new, stroke_width = 1, anchor="ls", fill=0)
    draw.text((left_align, line_heights[1]), lines[1], font=fnt2_new, anchor="ls", fill=0)
    draw.text((left_align, line_heights[2]), lines[2], font=fnt3_new, anchor="ls", fill=0)
    draw.text((left_align, line_heights[3]), lines[3], font=fnt4_new, anchor="ls", fill=0)

    return img


def large_format(qr_img, obj, font_filename, background_filename):
    # setup values
    size_l = (696, 223) # size of the large label
    qr_margin = 40 # the pixel distance between right border of qr code and the right border of white background
    qr_size = (size_l[1]-2*qr_margin, size_l[1]-2*qr_margin)
    qr_location = (size_l[0]-qr_size[0]-qr_margin, qr_margin) # where the left upper corner of qr code is

    # get a background white image for label
    img = Image.open(background_filename)
    # resize it to a label size suitable for QR printer
    img = img.resize(size_l)
    # resize the qr image to put on the background
    qr_img = qr_img.resize(qr_size)
    img.paste(qr_img, qr_location) # left upper corner coordinates

    # Add text information
    msg_num = 4
    fnt_sizes = [35,35,35,35]
    fnts = []
    for i in range(msg_num):
        fnts.append(ImageFont.truetype(font_filename, fnt_sizes[i]))


    draw = ImageDraw.Draw(img)

    # information needed
    experiment_id = obj["experiment_id"]
    storage_condition = obj["storage_condition"]
    contents = obj["contents"]
    date_entered = obj["date_entered"]
    expiration_date = obj["expiration_date"]
    analyst = obj["analyst"]

    # formatting
    lines = []
    lines.append(str(experiment_id)) # line 1: font size = 30, stroke width = 1
    lines.append(str(contents)) # line 2: font size = 30

    lines.append("Prep " + str(date_entered) + " " * 4 + "Expiry " + str(expiration_date)) # line 4: font size = 25
    lines.append("Prep By: " + str(analyst) + " " * 5 + "Stored at: " + str(storage_condition)) # line 5: font size = 25

    left_align = 20  # the pixel distance between the left of the text and the left of the border of white background
    available_width = size_l[0] - qr_size[0] - qr_margin - left_align

    # adjust font size to fit the available width
    fnt1_new, fnt1_size = test_fit_using_ttf_font(fnt_sizes[0], lines[0], font_filename, available_width)
    fnt2_new, fnt2_size = test_fit_using_ttf_font(fnt_sizes[1], lines[1], font_filename, available_width)
    fnt3_new, fnt3_size = test_fit_using_ttf_font(fnt_sizes[2], lines[2], font_filename, available_width)
    fnt4_new, fnt4_size = test_fit_using_ttf_font(fnt_sizes[3], lines[3], font_filename, available_width)


    line_heights = [50, 90, 130, 170, 200]
    # draw texts line by line on the white background
    draw.text((left_align, line_heights[0]), lines[0], font=fnt1_new, stroke_width=1, anchor="ls", fill=0)
    draw.text((left_align, line_heights[1]), lines[1], font=fnt2_new, anchor="ls", fill=0)
    draw.text((left_align, line_heights[2]), lines[2], font=fnt3_new, anchor="ls", fill=0)
    draw.text((left_align, line_heights[3]), lines[3], font=fnt4_new, anchor="ls", fill=0)

    img1 = img.resize((696//2, 223//2))
    img1.save("img_resize.png")


    return img



def create_qr_code(obj, size): # size: 2,2.5,4,20
    # size = 2, 2.5, 4, 20
    # size >= 4: larger ones: label info with QR code => img_larger
    # size < 4: smaller ones: QR code => img_smaller
    # save img (img_larger or img_smaller)
    '''
    obj = {
        'experiment_id':"5010613001301" ,
        'storage_condition': "50C, pH 6.8",
        'analyst': "AKPM",
        'contents': "10 mM potassium phosphate buffer",
        'date_entered': "06Jan2022",
        'expiration_date': "09Jan2022",
        'date_modified': "12Feb2022"
    }
    '''

    # Modified hash key (need to improve with order-carefree)
    features_selected = ['experiment_id', 'storage_condition', 'analyst','contents','date_entered','expiration_date']
    unique_hash = generate_hash_key(obj, features_selected)  # hash key is a long string for generating qr code

    # Creating an instance of qrcode
    obj_qrkey = {
        "qr_code_key": f"{unique_hash}",
        "date_modified": obj["date_modified"]
    }

    # Using the library to create the QR code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,#45*10
        border=5) #5*2
    qr.add_data(obj_qrkey)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')

    qr_img.save('qr_label.png')
    qr_img1 = qr_img.resize((50, 50))
    qr_img1.save('qr_label_resize.png')

    ################### Add Here #####################
    # Using the library to create the barcode
    CODE128 = barcode.get_barcode_class('code128')
    my_code = CODE128(unique_hash)
    my_code.save('code128_barcode')


    # ttf font
    #path1 = "/Users/zhangyuke/Downloads/"  # # In merck_dashboard, the path should be "backend/files_for_label/"
    #font_filename = path1 + "Arial_Unicode.ttf"

    path = "files_for_label/" # /server/backend/files_for_label/
    #path = "/server/backend/files_for_label/"
    font_filename = path + "reg.ttf"
    background_filename = path + "white image.jpeg"

    if size >= 4:
        img = large_format(qr_img, obj, font_filename, background_filename)
        img.save(path + 'large_label.png', quality = 100)  # for testing
    else:
        img = small_format2(qr_img, obj, font_filename, background_filename)# modify to add small format function here
        img.save(path + 'small_label.png', quality = 100)  # for testing

    # Temporarily saves QR code into /qr_codes folder
    # Will be improved as we do not need to store it as we will send the QR code to the printer
    # qr_code_dir = os.path.join(os.getcwd(), 'backend', 'qr_codes')
    #img.save(path + 'label.png') # for testing


    ##################################################

    return unique_hash

def main():
    obj = {
        'experiment_id': "NB-9999999-301-01",
        'temperature': "50C",
        'PH': "pH 6.8",
        'analyst': "AKPM",
        'concentration': "10 mM",
        'contents': "potassium phosphate buffer",
        'date_entered': "06Jan2022",
        'expiration_date': "09Jan2022",
        'date_modified': "12Feb2022"

    }
    obj = {
                'experiment_id':"NB-9999999-301-01" ,
                'storage_condition': "50C, pH 6.8",
                'analyst': "AKPM",
                'contents': "10 mM, potassium phosphate buffer",
                'date_entered': "10/24/2022",
                'expiration_date': "01/28/2022",
                'date_modified': "10/24/2022"
            }
    size = 2
    unique_hash = create_qr_code(obj, size)
    print(f'unique_hash is {unique_hash}')
    size = 4
    unique_hash = create_qr_code(obj, size)
    print(f'unique_hash is {unique_hash}')

main()