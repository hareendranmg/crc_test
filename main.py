# import serial

# # Configure the COM port settings
# com_port = "COM1"
# baud_rate = 9600

# # Open the COM port
# ser = serial.Serial(com_port, baud_rate)

# # Open a file for writing
# filename = "data.txt"
# file = open(filename, "w")

# try:
#     while True:
#         # Read data from the COM port
#         data = ser.readline().decode().strip()

#         # Write data to the file
#         file.write(data + "\n")
#         file.flush()  # Flush the buffer to ensure immediate writing

#         # Print the received data
#         print(data)

# except KeyboardInterrupt:
#     pass

# finally:
#     # Close the file and COM port
#     file.close()
#     ser.close()


def modbusCrc(msg: str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


msg = bytes.fromhex("0210002500050A0206000000640000BB80")
msg = bytes.fromhex("0210002500050A0206000000640000BB80")
print(msg)

crc = modbusCrc(msg)
print("0x%04X" % (crc))

ba = crc.to_bytes(2, byteorder="little")
print("%02X %02X" % (ba[0], ba[1]))
