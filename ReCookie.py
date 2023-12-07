import requests
import time
import os
import hashlib
import pygetwindow as gw
def cls(): os.system("cls") # Clears the console
def path(): return os.getcwd() # Returns local path

banner = """
██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗███████╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔═══██╗██║ ██╔╝██║██╔════╝   
██████╔╝█████╗  ██║     ██║   ██║██║   ██║█████╔╝ ██║█████╗  
██╔══██╗██╔══╝  ██║     ██║   ██║██║   ██║██╔═██╗ ██║██╔══╝  
██║  ██║███████╗╚██████╗╚██████╔╝╚██████╔╝██║  ██╗██║███████╗       
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝  -jedpep                                            
"""

def parse_cookies(cookie_string):
    cookies = cookie_string.split(', ') # Splits the cookies
    parsed_cookies = {}

    for cookie in cookies:
        parts = cookie.split('; ') # Splits cookie again
        name_value = parts[0].split('=')
        name = name_value[0]
        value = '='.join(name_value[1:]) # Join back any additinal '=' found in the value
        parsed_cookies[name] = {'value': value}
        for part in parts[1:]: # Parse the other components of the cookie (domain, path, etc)
            if '=' in part:
                key, val = part.split('=')
                parsed_cookies[name][key] = val
            else:
                parsed_cookies[name][part] = True

    return parsed_cookies

def wait_until_file_changes(filename, interval=1): # Pauses the code until it detects a file change
    def get_file_hash(filename):
        with open(filename, 'rb') as file:
            return hashlib.md5(file.read()).hexdigest() # Gets the files md5 hash

    last_hash = get_file_hash(filename)

    while True:
        try:
            time.sleep(interval)
            current_hash = get_file_hash(filename)
            if current_hash != last_hash:
                return True # If the hash has changed, it returns, resuming the code
        except FileNotFoundError:
            return False

def get_xcsrf(cookie):
    req = requests.post("https://auth.roblox.com/v1/logoutfromallsessionsandreauthenticate", cookies={".ROBLOSECURITY": cookie}) # Trys to request an X-CSRF-TOKEN
    try:
        return req.headers['x-csrf-token'] # Looks for the token in the request, and returns it
    except:
        return ":(" # If no token is found, it retuns an empty value (meaning cookie is invalid)

def refresh_cookie(cookie):
    req = requests.post("https://auth.roblox.com/v1/logoutfromallsessionsandreauthenticate", cookies={".ROBLOSECURITY": cookie}, headers={"X-Csrf-Token": get_xcsrf(cookie)}) # Trys to request a new cookie
    if req.status_code == 200:
        try:
            return req.headers["set-cookie"] # If the cookie is succesfully returned from roblox, it returns it
        except:
            pass # If its not, then it retrys
    else:
        print("\nFailed to request auth ticket, your cookie is invalid/expired")
        time.sleep(5)

def get_authticket(cookie):
    req = requests.post("https://auth.roblox.com/v1/authentication-ticket", cookies={".ROBLOSECURITY": cookie}, headers={"x-csrf-token": get_xcsrf(cookie), "referer": "https://www.roblox.com/", "Content-Type": "application/json"}) # Generates new auth ticket
    if req.status_code == 200:
        try:
            return req.headers["rbx-authentication-ticket"] # If it succesfully made a new ticket, itll return it
        except:
            pass # If not, then it retrys
    else:
        print("\nFailed to request auth ticket, your cookie is invalid/expired")
        time.sleep(5)

def redeem_authticket(ticket):
    req = requests.post("https://auth.roblox.com/v1/authentication-ticket/redeem", data={"authenticationTicket": ticket}, headers={"RBXAuthenticationNegotiation": "1"}) # Trys to redeem the auth ticket
    try:
        return req.headers['set-cookie'] # Looks for new cookies in the headers
    except:
        return

def main():
    while True:
        try:
            cls()
            print(banner)
            print("""
    1 | Refresh cookie
    2 | Bulk refresh cookies (list)
    3 | Exit
    """)

            selection = input(">> ")

            if selection == "1":
                cls()
                print(banner)

                cookie = input("Paste your cookie that you would like to refresh: ")
                method = input("\n1 | Refresh cookie (this will delete ALL other cookies to the account)\n2 | Generate cookie (this will generate a brand new cookie to the account, keeping all old ones)\n\n>> ")

                if method == "1":
                    sure = input("Are you sure you want to continue? (y/n)\nWARNING: THIS WILL DELETE ALL OLD COOKIES TO THIS ACCOUNT\n>> ")
                    if sure == "y":
                        recookie = refresh_cookie(cookie)
                        parsed_cookie = parse_cookies(recookie)[".ROBLOSECURITY"]["value"]

                        for r in range(3):
                            cls()
                            print(banner)
                            print("Your new cookie: \n\n" + parsed_cookie)
                            input(f"\nPress RETURN {3-r} more time{'s' if 3-r > 1 else ''} to exit.")
                if method == "2":
                    ticket = get_authticket(cookie)
                    recookie = redeem_authticket(ticket)
                    parsed_cookie = parse_cookies(recookie)[".ROBLOSECURITY"]["value"]

                    for r in range(3):
                        cls()
                        print(banner)
                        print("Your new cookie: \n\n" + parsed_cookie)
                        input(f"\nPress RETURN {3-r} more time{'s' if 3-r > 1 else ''} to exit.")

            if selection == "2":
                bulk = path() + r"\bulk.txt"
                with open(bulk, "w") as f: # Create a new text file.
                    os.system("explorer.exe " + bulk) # Open the newly created file in notepad
                    print("Please paste your cookies inside the opened text file, and then save the file once pasted\nNOTE: SEPERATED BY NEWLINE")
                    f.close() # Close the file in python

                wait_until_file_changes(bulk) # Wait until the user has saved the file

                with open(bulk, "r") as f:
                    cookies = f.read().splitlines() # Get cookies from file

                for window in gw.getWindowsWithTitle("bulk.txt"):
                    window.close()

                cls()
                print("Found cookies!\n")
                method = input("\n1 | Refresh cookie (this will delete ALL other cookies to the account)\n2 | Generate cookie (this will generate a brand new cookie to the account, keeping all old ones)\n\n>> ")

                if method == "1":
                    cls()
                    sure = input("\nAre you sure you want to continue? (y/n)\nWARNING: THIS WILL DELETE ALL OLD COOKIES TO THESE ACCOUNTS\n>> ")

                    if sure == "y":

                        recookies = []

                        for cookie in cookies:
                            recookie = refresh_cookie(cookie)
                            parsed_cookie = parse_cookies(recookie)[".ROBLOSECURITY"]["value"]
                            recookies.append(parsed_cookie)

                        with open(bulk, "w") as f:
                            for cookie in recookies:
                                f.write(cookie + "\n") # Write cookies back to file
                            f.close()

                        os.system("explorer.exe " + bulk) # Open the new cookies in notepad

                        time.sleep(10)
                if method == "2":
                    cls()
                    recookies = []

                    for cookie in cookies:
                        ticket = get_authticket(cookie)
                        recookie = redeem_authticket(ticket)
                        parsed_cookie = parse_cookies(recookie)[".ROBLOSECURITY"]["value"]
                        recookies.append(parsed_cookie)

                    with open(bulk, "w") as f:
                        for cookie in recookies:
                            f.write(cookie + "\n") # Write cookies back to file
                        f.close()

                    os.system("explorer.exe " + bulk) # Open the new cookies in notepad

                    time.sleep(10)
            if selection == "3":
                break
        except KeyboardInterrupt:
            break
        except:
            pass

main()