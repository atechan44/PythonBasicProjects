from rembg import remove
#MAKE SURE TO COPY IN FOLDER THE FILE
input_path=input("enter your image file name, please put the extension(for ex: image.png):  ")
output_path = "output.png"     #output always png

with open(input_path,'rb') as i: #rb=read binary
    with open(output_path, 'wb') as o:  #wr=write binary
        input_file = i.read()
        output_file = remove(input_file)
        o.write(output_file)

