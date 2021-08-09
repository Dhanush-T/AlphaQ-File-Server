import os
import socket
import threading
import re
from Crypto.Cipher import AES



IP = '127.0.0.1'
PORT = 4466
main_path = "/home/daemondan/Delta/Task_3/"
tLock = threading.Lock()

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

# This function is to handle all the client requests

def client(conn, addr):
    print("NEW CONNECTIONS : {}".format(addr))
    conn.send(AES_EnDe("WELCOME TO THE FILE SERVER.Please enter your login credentials for login into the SERVER", "en"))
    uname = AES_EnDe(conn.recv(1024), "de")
    passwd = AES_EnDe(conn.recv(1024), "de")
    if uname in usernames and passwd==uname:
        conn.send(AES_EnDe("Login Successful..!!! \nTo see the server commands type HELP or ? ","en"))

        while True:
            command = AES_EnDe(conn.recv(1024), "de")

        #This is to give a brief explaination about the available commands.

            if command == 'HELP' or command == '?':
                tLock.acquire()
                help = "\n\tLIST : To list all the available files from server.\n"
                help += "\tUPLOAD <filename> : To upload file to the server.\n"
                help += "\tDELETE <filename> : To delete the file from the server.\n"
                help += "\tDOWNLOAD <filename> : To download file from the server.\n"
                help += "\tSEARCH <filename> : To search for file or related file from server.\n"
                help += "\tEXIT : To get logout from the server.\n"
                help += "\tHELP : To list all the available commands."
                conn.send(AES_EnDe(help, "en"))
                tLock.release()

        #To exit out of the server terminal

            elif command == "EXIT":
                print("{} disconnected.".format(addr))
                conn.close()
                break

        #To upload file to the server into the respective directory

            elif "UPLOAD" in command:
                tLock.acquire()
                response = AES_EnDe(conn.recv(1024), "de")
                if "YES" in response:
                    conn.send(AES_EnDe("OK", "en"))
                    cmd = command.split(" ")
                    filename = cmd[1]
                    if uname in sysAd:
                        path="main_folder/sysAd"
                    elif uname in appDev:
                        path="main_folder/appDev"
                    elif uname in webDev:
                        path="main_folder/webDev"

                    file_size = int(response[10:])
                    os.chdir(main_path+path)
                    new_filename = "new_"+str(filename)
                    with open(new_filename, 'w') as f:
                        data = AES_EnDe(conn.recv(1024), "de")
                        f.write(data)
                        total_received = len(data)
                        while total_received < file_size:
                             data = AES_EnDe(conn.recv(1024), "de")
                             total_received += len(data)
                             f.write(data)

                    conn.send(AES_EnDe("FILE UPLOADED SUCCESSFULLY..!!!", "en"))
                    tLock.release()

            #To download files from the server into our local storage

            elif "DOWNLOAD" in command:
                tLock.acquire()
                cmd = command.split(" ")
                filename = cmd[1]
                if uname in sysAd:
                    path = "main_folder/sysAd"
                elif uname in appDev:
                    path = "main_folder/appDev"
                elif uname in webDev:
                    path = "main_folder/webDev"

                os.chdir(main_path+path)
                for file in os.listdir(main_path+path):
                    if file == filename:
                        match = "True"
                        break
                if match=="True":
                    file_size = os.path.getsize(filename)
                    msg = "EXIST,{}".format(file_size)
                    conn.send(AES_EnDe(msg, "en"))
                    response = AES_EnDe(conn.recv(1024), "de")
                    if response == "y":
                        with open(filename, 'r') as f:
                            data = f.read(1024)
                            conn.send(AES_EnDe(data, "en"))
                            while data != "":
                                data = f.read(1024)
                                conn.send(AES_EnDe(data, "en"))
                else:
                    msg = "NO SUCH FILE EXISTS"
                    conn.send(AES_EnDe(msg, "en"))
                tLock.release()

            #To list all the available files for the users from their respective domains

            elif command == "LIST":
                tLock.acquire()
                if uname in sysAd:
                    path="main_folder/sysAd"
                elif uname in appDev:
                    path="main_folder/appDev"
                elif uname in webDev:
                    path="main_folder/webDev"

                available_files = "\n"
                i=1
                for file in os.listdir(main_path+path):
                    available_files = available_files+str(i)+") "+file +"\n"
                    i=i+1

                conn.send(AES_EnDe(available_files, "en"))
                tLock.release()

            #To remove a file from the server.

            elif "DELETE" in command:
                tLock.acquire()
                cmd = command.split(" ")
                filename = cmd[1]
                if uname in sysAd:
                    path = "main_folder/sysAd"
                elif uname in appDev:
                    path = "main_folder/appDev"
                elif uname in webDev:
                    path = "main_folder/webDev"

                os.chdir(main_path+path)
                for file in os.listdir(main_path+path):
                    if file == filename:
                        match = "True"
                        break
                conn.send(AES_EnDe("FILE EXIST", "en"))
                yes_or_no = AES_EnDe(conn.recv(1024), "de")
                if yes_or_no == "y":
                    os.remove(filename)
                    conn.send(AES_EnDe("SUCCESSFULLY REMOVED..!!", "en"))
                tLock.release()

            elif "SEARCH" in command:
                tLock.acquire()
                cmd = command.split(" ")
                filename = cmd[1]
                if uname in sysAd:
                    path = "main_folder/sysAd"
                elif uname in appDev:
                    path = "main_folder/appDev"
                elif uname in webDev:
                    path = "main_folder/webDev"

                match = "False"
                for file in os.listdir(main_path+path):
                    if file == filename:
                        match = "True"
                        break
                if match == "True":
                    conn.send(AES_EnDe("YES, FILE EXISTS", "en"))
                elif match == "False":
                    msg="\nFILE NOT EXISTS\nBut similar files are listed below\n"
                    similar_file = filename[0:4]
                    i=1
                    for file in os.listdir(main_path+path):
                        if(re.search(similar_file, file)):
                            msg = msg+"\t"+str(i)+") "+file+"\n"
                            i=i+1
                    conn.send(AES_EnDe(msg, "en"))
                tLock.release()



    else:
        conn.send(AES_EnDe("Invalid Credentials.", "en"))
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
