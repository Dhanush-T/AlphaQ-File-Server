import socket
import os
from Crypto.Cipher import AES


IP='127.0.0.1'
PORT=4466

# AES Encryption function

key=b'mypassword123456'
mode = AES.MODE_CBC
IV = 'This is an IV456'

def AES_EnDe(txt, type):
    while len(txt)%16 != 0:
        txt = txt + "*"

    cipher = AES.new(key, mode, IV)
    if type == "en":
        encrypt_txt = cipher.encrypt(txt)
        return encrypt_txt
    elif type == "de":
        decrypt_txt = cipher.decrypt(txt).rstrip(b'*').decode()
        return decrypt_txt


def Main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    print(AES_EnDe(client.recv(1024), "de"))

    uname = input("Enter you Username: ")
    client.send(AES_EnDe(uname, "en"))

    passwd = input("Enter your Password: ")
    client.send(AES_EnDe(passwd, "en"))

    response=AES_EnDe(client.recv(1024), "de")
    print(response)

    if "Invalid Credentials" == response:
        print("CONNECTION CLOSED.")
        client.close()

    elif "Login Successful" in response:

        while True:
            print("\n{}@server [~]".format(uname),end = " ")
            user_input = input()
            client.send(AES_EnDe(user_input, "en"))

            user_input = user_input.split(" ")
            command = user_input[0]

            if command == "HELP" or command == "?":
                print(AES_EnDe(client.recv(1024), "de"))

            elif command == "EXIT":
                print("\nConnection diconnected..!!!")
                client.close()
                break

            elif command == "UPLOAD":
                filename = user_input[1]
                match = "False"
                for file in os.listdir():
                    if file == filename:
                        match = "True"
                        break
                if match=="True":
                    msg = "YES EXIST,{}".format(os.path.getsize(filename))
                    client.send(AES_EnDe(msg, "en"))

                    yes_or_no = AES_EnDe(client.recv(1024), "de")
                    if yes_or_no == "OK":
                        with open(filename, 'r') as f:
                            data=f.read(1024)
                            client.send(AES_EnDe(data, "en"))
                            while data != "":
                                data=f.read(1024)
                                client.send(AES_EnDe(data, "en"))
                        print(AES_EnDe(client.recv(1024), "de"))
                    else:
                        print("UPLOAD ABORTED.")

                else:
                    client.send(AES_EnDe("NOT EXIST", "en"))
                    print("FILE NOT EXISTS.")


            elif command == "DOWNLOAD":
                filename = user_input[1]
                response = AES_EnDe(client.recv(1024), "de")
                if "EXIST" in response:
                    file_size = int(response[6:])
                    yes_or_no = input("\nFile exits. {} bytes, download (y/n) ?".format(file_size))
                    client.send(AES_EnDe(yes_or_no, "en"))

                    if yes_or_no == "y":
                        f = open("new_"+filename, 'w')
                        data = AES_EnDe(client.recv(1024), "de")
                        total_received = len(data)
                        f.write(data)
                        while total_received < file_size:
                            data = AES_EnDe(client.recv(1024), "de")
                            f.write(data)
                            total_received +=len(data)
                            percent_downloaded = (total_received/file_size)*100
                            print("{}% DONE.".format(percent_downloaded))
                        print("DOWNLOAD COMPLETED.")
                        f.close()

                    elif yes_or_no == "n":
                        print("DOWNLOAD ABORTED.")
                elif "NO" in response:
                    print("FILE DOES NOT EXISTS")

            elif command == "LIST":
                print(AES_EnDe(client.recv(1024), "de"))

            elif command == "DELETE":
                response = AES_EnDe(client.recv(1024), "de")
                yes_or_no = input("\nFILE EXIST, Do you want to remove ? (y/n) ")
                client.send(AES_EnDe(yes_or_no, "en"))
                if yes_or_no == "y":
                    print(AES_EnDe(client.recv(1024), "de"))
                else:
                    print("DELETING THE FILE CANCELLED")

            elif command == "SEARCH":
                response = AES_EnDe(client.recv(1024), "de")
                if "YES" in response:
                    print("FILE EXIST")
                else:
                    print(response)

            else:
                print("INVALID COMMAND.")




if __name__ == '__main__':
    Main()
