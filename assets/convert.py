import base64

# Pastikan nama filenya sesuai sama gambar kelopak lu
with open("petal.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Bikin file txt isinya kodingan panjang Base64 gambar lu
    with open("hasil_base64.txt", "w") as text_file:
        text_file.write(encoded_string)

print("Beres bang! Buka file hasil_base64.txt, terus copas isinya!")