import socket
import os

IP='127.0.0.1'
PORT=4466

def Main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    print(client.recv(1024).decode('utf-8'))

    uname = input("Enter you Username: ")
    client.send(uname.encode('utf-8'))

    passwd = input("Enter your Password: ")
    client.send(passwd.encode('utf-8'))

    response=client.recv(1024).decode('utf-8')
    print(response)

    if "Invalid Credentials" == response:
        print("CONNECTION CLOSED.")
        client.close()

    elif "Login Successful" in response:

        while True:
            print("\n{}@server [~]".format(uname),end = " ")
            user_input = input()
            client.send(user_input.encode('utf-8'))

            user_input = user_input.split(" ")
            command = user_input[0]

            if command == "HELP" or command == "?":
                print(client.recv(1024).decode('utf-8'))

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
                    client.send(msg.encode('utf-8'))
                    yes_or_no = client.recv(1024).decode('utf-8')
                    if yes_or_no == "OK":
                        with open(filename, 'r') as f:
                            data=f.read(1024)
                            client.send(data.encode('utf-8'))
                            while data != "":
                                data=f.read(1024)
                                client.send(data.encode('utf-8'))
                        print(client.recv(1024).decode('utf-8'))
                    else:
                        print("UPLOAD ABORTED.")

                else:
                    client.send("NOT EXISTS".encode('utf-8'))
                    print("FILE NOT EXISTS.")


            elif command == "DOWNLOAD":
                filename = user_input[1]
                response = client.recv(1024).decode('utf-8')
                if "EXIST" in response:
                    file_size = int(response[6:])
                    yes_or_no = input("\nFile exits. {} bytes, download (y/n) ?".format(file_size))
                    client.send(yes_or_no.encode('utf-8'))
                    if yes_or_no == "y":
                        f = open("new_"+filename, 'w')
                        data = client.recv(1024).decode('utf-8')
                        total_received = len(data)
                        f.write(data)
                        while total_received < file_size:
                            data = client.recv(1024).decode('utf-8')
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
                print(client.recv(1024).decode('utf-8'))

            elif command == "DELETE":
                response = client.recv(1024).decode('utf-8')
                yes_or_no = input("\nFILE EXIST, Do you want to remove ? (y/n) ")
                client.send(yes_or_no.encode('utf-8'))
                if yes_or_no == "y":
                    print(client.recv(1024).decode('utf-8'))
                else:
                    print("DELETING THE FILE CANCELLED")

            else:
                print("INVALID COMMAND.")





if __name__ == '__main__':
    Main()
