import qrcode
import clipboard

if __name__ == '__main__':
    # Create and show QR code from clipboard
    s = clipboard.paste()
    print("Generating QR code for:", s)
    img = qrcode.make(s)
    img.show()
