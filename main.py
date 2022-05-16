#Encryption of sensitive image with AES:
from PIL import Image
from Crypto.Cipher import AES
import matplotlib.pyplot as plt

filename = "assets\s.jpeg"
filename_out = "tux_encrypted"
format = "BMP"
key = "aaaabbbbccccdddd"
# AES requires that plaintexts be a multiple of 16, so we have to pad the data
def pad(data):
    return data + b"\x00"*(16-len(data)%16) 
# Maps the RGB 
def convert_to_RGB(data):
    r, g, b = tuple(map(lambda d: [data[i] for i in range(0,len(data)) if i % 3 == d], [0, 1, 2]))
    pixels = tuple(zip(r,g,b))
    return pixels
    
def process_image(filename):
    # Opens image and converts it to RGB format for PIL
    im = Image.open(filename)
    data = im.convert("RGB").tobytes() 
    # Since we will pad the data to satisfy AES's multiple-of-16 requirement, we will store the original data length and "unpad" it later.
    original = len(data) 
    # Encrypts using desired AES mode (we'll set it to ECB by default)
    new = convert_to_RGB(aes_ecb_encrypt(key, pad(data))[:original]) 
    
    # Create a new PIL Image object and save the old image data into the new image.
    im2 = Image.new(im.mode, im.size)
    im2.putdata(new)
    
    #Save image
    im2.save(filename_out+"."+format, format)
    return im2
# CBC
def aes_cbc_encrypt(key, data, mode=AES.MODE_CBC):
    IV = "A"*16  #We'll manually set the initialization vector to simplify things
    aes = AES.new(key.encode("utf8"), mode, IV.encode("utf8"))
    # obj = AES.new('This is a key123'.encode("utf8"), AES.MODE_CBC, 'This is an IV456'.encode("utf8"))
    new_data = aes.encrypt(data)
    return new_data
# ECB
def aes_ecb_encrypt(key, data, mode=AES.MODE_ECB):
    aes = AES.new(key.encode("utf8"), mode)
    new_data = aes.encrypt(data)
    return new_data




#Steganography with LSB

def __int_to_bin(rgb):
        """Convert an integer tuple to a binary (string) tuple.
        :param rgb: An integer tuple (e.g. (220, 110, 96))
        :return: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        """
        r, g, b = rgb
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))
    
def __bin_to_int(rgb):
        """Convert a binary (string) tuple to an integer tuple.
        :param rgb: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: Return an int tuple (e.g. (220, 110, 96))
        """
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))    
def __merge_rgb(rgb1, rgb2):
        """Merge two RGB tuples.
        :param rgb1: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :param rgb2: Another string tuple
        (e.g. ("00101010", "11101011", "00010110"))
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4],
               g1[:4] + g2[:4],
               b1[:4] + b2[:4])
        return rgb    
def merge(img1, img2):
        """Merge two images. The second one will be merged into the first one.
        :param img1: First image
        :param img2: Second image
        :return: A new merged image.
        """

        # Check the images dimensions
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Image 2 should not be larger than Image 1!')

        # Get the pixel map of the two images
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # Create a new image that will be outputted
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = __int_to_bin(pixel_map1[i, j])

                # Use a black pixel as default
                rgb2 = __int_to_bin((0, 0, 0))

                # Check if the pixel map position is valid for the second image
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = __int_to_bin(pixel_map2[i, j])

                # Merge the two pixels and convert it to a integer tuple
                rgb = __merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = __bin_to_int(rgb)

        return new_image    

def unmerge(img):
        """Unmerge an image.
        :param img: The input image.
        :return: The unmerged/extracted image.
        """

        # Load the pixel map
        pixel_map = img.load()

        # Create the new image and load the pixel map
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        # Tuple used to store the image original size
        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                r, g, b = __int_to_bin(pixel_map[i, j])

                # Extract the last 4 bits (corresponding to the hidden image)
                # Concatenate 4 zero bits because we are working with 8 bit
                rgb = (r[4:] + '0000',
                       g[4:] + '0000',
                       b[4:] + '0000')

                # Convert it to an integer tuple
                pixels_new[i, j] = __bin_to_int(rgb)

                # If this is a 'valid' position, store it
                # as the last valid position
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        # Crop the image based on the 'valid' pixels
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

        return new_image    


img1="assets/no_you.jpg"
img2 = process_image(filename)
# img2.show()
merged_image =merge(Image.open(img1), img2)
ui= "catty"
format2="JPEG"
unmerged_image = unmerge(merged_image)
unmerged_image.save("ui"+format2, format2)

# merged_image.show()
# unmerged_image.show()
plt.figure(figsize=(15, 12), dpi=80)

plt.subplot(4, 1, 1)
main_image = Image.open("assets/s.jpeg")
plt.imshow(main_image)
plt.title("main image")
plt.axis('off')
# plt.show()

plt.subplot(4, 1, 2)
plt.imshow(img2)
plt.title("Encrypted Image")
plt.axis('off')
# plt.show()

plt.subplot(4, 1, 3)
carrier_image =Image.open(img1)
plt.imshow(carrier_image)
plt.title("Carrier Image for steganography")
# plt.show()
plt.axis('off')

plt.subplot(4, 1, 4)
plt.imshow(merged_image)
plt.title("Steganography: Main image merged with carrier image")
plt.axis('off')
plt.show()


# plt.subplot(2, 4, 4)
# plt.imshow(unmerged_image)
# plt.title("Main image (still Encrypted)")
# plt.show()

