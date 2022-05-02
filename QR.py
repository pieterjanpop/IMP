from pyzbar.pyzbar import decode

def qr(image):
	return decode(image)