import os
import socket
import threading
import re


IP = '127.0.0.1'
PORT = 4466
main_path = "/home/daemondan/Delta_T3/"

sysAd = []
appDev = []
webDev = []

for i in range(1, 31):
    if i < 10:
        sysAd.append("sysAd_0"+str(i))
        appDev.append("appDev_0"+str(i))
        webDev.append("webDev_0"+str(i))
    else:
        sysAd.append("sysAd_"+str(i))
        appDev.append("appDev_"+str(i))
        webDev.append("webDev_"+str(i))

usernames = sysAd+appDev+webDev


def client(conn, addr):
    print("NEW CONNECTIONS : {}".format(addr))
    conn.send("WELCOME TO THE FILE SERVER.Please enter your login credentials for login into the SERVER".encode('utf-8'))
    uname = conn.recv(1024).decode('utf-8')
    passwd = conn.recv(1024).decode('utf-8')
    if uname in usernames and passwd==uname:
        conn.send("Login Successful..!!! \nTo see the server commands type HELP or ? ".encode('utf-8'))

        while True:
            command = conn.recv(1024).decode('utf-8')

        #This is to give a brief explaination about the available commands.

            if command == 'HELP' or command == '?':
                help = "\n\tLIST : To list all the available files from server.\n"
                help += "\tUPLOAD <filename> : To upload file to the server.\n"
                help += "\tDELETE <filename> : To delete the file from the server.\n"
                help += "\tDOWNLOAD <filename> : To download file from the server.\n"
                help += "\tEXIT : To get logout from the server.\n"
                help += "\tHELP : To list all the available commands."
                conn.send(help.encode('utf-8'))

        #To exit out of the server terminal

            elif command == "EXIT":
                print("{} disconnected.".format(addr))
                conn.close()
                break

        #To upload file to the server into the respective directory

            elif "UPLOAD" in command:
                response = conn.recv(1024).decode('utf-8')
                if "YES" in response:
                    conn.send("OK".encode('utf-8'))
                    cmd = command.split(" ")
                    filename = cmd[1]
                    if uname in sysAd:
                        path="sysAd"
                    elif uname in appDev:
                        path="appDev"
                    elif uname in webDev:
                        path="webDev"

                    file_size = int(response[10:])
                    os.chdir(main_path+path)
                    new_filename = "new_"+str(filename)
                    with open(new_filename, 'w') as f:
                        data = conn.recv(1024).decode('utf-8')
                        f.write(data)
                        total_received = len(data)
                        while total_received < file_size:
                             data = conn.recv(1024).decode('utf-8')
                             total_received += len(data)
                             f.write(data)

                    conn.send("FILE UPLOADED SUCCESSFULLY..!!!".encode('utf-8'))

            #To download files from the server into our local storage

            elif "DOWNLOAD" in command:
                cmd = command.split(" ")
                filename = cmd[1]
                if uname in sysAd:
                    path = "sysAd"
                elif uname in appDev:
                    path = "appDev"
                elif uname in webDev:
                    path = "webDev"

                os.chdir(main_path+path)
                for file in os.listdir(main_path+path):
                    if file == filename:
                        match = "True"
                        break
                if match=="True":
                    file_size = os.path.getsize(filename)
                    msg = "EXIST,{}".format(file_size)
                    conn.send(msg.encode('utf-8'))
                    response = conn.recv(1024).decode('utf-8')
                    if response == "y":
                        with open(filename, 'r') as f:
                            data = f.read(1024)
                            conn.send(data.encode('utf-8'))
                            while data != "":
                                data = f.read(1024)
                                conn.send(data.encode('utf-8'))
                else:
                    msg = "NO SUCH FILE EXISTS"
                    conn.send(msg.encode('utf-8'))

            #To list all the available files for the users from their respective domains

            elif command == "LIST":
                if uname in sysAd:
                    path="sysAd"
                elif uname in appDev:
                    path="appDev"
                elif uname in webDev:
                    path="webDev"

                available_files = "\n"
                i=1
                for file in os.listdir(main_path+path):
                    available_files = available_files+str(i)+") "+file +"\n"
                    i=i+1

                conn.send(available_files.encode('utf-8'))

            #To remove a file from the server.

            elif "DELETE" in command:
                cmd = command.split(" ")
                filename = cmd[1]
                if uname in sysAd:
                    path = "sysAd"
                elif uname in appDev:
                    path = "appDev"
                elif uname in webDev:
                    path = "webDev"

                os.chdir(main_path+path)
                for file in os.listdir(main_path+path):
                    if file == filename:
                        match = "True"
                        break
                conn.send("FILE EXIST.".encode('utf-8'))
                yes_or_no = conn.recv(1024).decode('utf-8')
                if yes_or_no == "y":
                    os.remove(filename)
                    conn.send("SUCCESSFULLY REMOVED..!!".encode('utf-8'))



    else:
        conn.send("Invalid Credentials.".encode('utf-8'))
        print("CONNECTION ENDED.")
        conn.close()
        print("Number of ACTIVE CONNECTIONS = {}".format(threading.activeCount()-1))


def Main():
    print("Server Starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    print("Sever Started listening on {}:{}".format(IP, PORT))

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client, args=(conn, addr))
        thread.start()
        print("Number of ACTIVE CONNECTIONS = {}".format(threading.activeCount()-1))



if __name__ == '__main__':
    Main()
