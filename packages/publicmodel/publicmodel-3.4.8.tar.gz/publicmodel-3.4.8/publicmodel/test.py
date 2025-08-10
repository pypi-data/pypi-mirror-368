import qrcode
from PIL import Image, ImageDraw

from publicmodel.abnormal.error_class import OptionError


class QRCG:  # Quick Response Code Generator
    def __init__(self, data, img_size=(300, 300), qr_version=1, box_size=10, logo_path=None, save_path=None,
                 show=False, error_correct_levels="high", border=4, fill_color="black", back_color="white"):
        self.data = self._read_data(data)
        self.img_size = img_size
        self.qr_version = qr_version
        self.box_size = box_size
        self.logo_path = logo_path
        self.save_path = save_path
        self.show = show
        self.error_correct_levels = error_correct_levels
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color

    def _read_data(self, data):
        try:
            with open(data, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return data

    def generate_qr(self):
        if self.error_correct_levels == "low":
            error_correction = qrcode.constants.ERROR_CORRECT_L
        elif self.error_correct_levels == "default":
            error_correction = qrcode.constants.ERROR_CORRECT_M
        elif self.error_correct_levels == "medium":
            error_correction = qrcode.constants.ERROR_CORRECT_Q
        elif self.error_correct_levels == "high":
            error_correction = qrcode.constants.ERROR_CORRECT_H
        else:
            raise OptionError(f"Invalid error correction level: \"{self.error_correct_levels}\"")

        qr = qrcode.QRCode(
            version=self.qr_version,
            error_correction=error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color).convert('RGB')

        # Adjust the size of the QR code image
        img = img.resize(self.img_size, Image.NEAREST)  # Use nearest neighbor interpolation method

        # Round the corners of each black block
        img = self._round_corners(img)

        if self.logo_path:
            self._add_logo(img)

        if self.save_path:
            img.save(self.save_path)

        if self.show:
            img.show()

    def _round_corners(self, img):
        # Create a new image with white background
        rounded_img = Image.new('RGB', img.size, self.back_color)
        draw = ImageDraw.Draw(rounded_img)

        # Get the size of each block
        block_size = self.box_size

        # Iterate over each block in the QR code
        for y in range(0, img.size[1], block_size):
            for x in range(0, img.size[0], block_size):
                # Get the color of the current block
                block = img.crop((x, y, x + block_size, y + block_size))
                if block.getpixel((0, 0)) == (0, 0, 0):  # If the block is black
                    # Draw a rounded rectangle
                    draw.rounded_rectangle(
                        [(x, y), (x + block_size, y + block_size)],
                        radius=block_size // 4,
                        fill=self.fill_color
                    )

        return rounded_img

    def _add_logo(self, img):
        logo = Image.open(self.logo_path)

        # The size of the logo is one-fifth of the minimum side length of the QR code image
        logo_size = min(self.img_size) // 5

        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo)


if __name__ == '__main__':
    qr = QRCG(data="Hello, World!", save_path="img/rounded_qr.png", show=True)
    qr.generate_qr()
