"""
Before running this script, make sure to install the required dependencies:
pip install cryptography
pip install thefuzz
"""

import pandas as pd
from datetime import datetime, date
from thefuzz import process
from cryptography.fernet import Fernet
import os
import random
import string

def store_ai():
    """
    This is the main function to call when using this module.
    It gives user access to the Store AI.

    Parameters:
    None

    Return:
    None

    """
    while True:
        print("\nWelcome to Bruno's Store. My name is Store AI, How can I be of service?\n")
        print("There are 3 portals. Select what portal you want to access.")
        print("1. Sales Portal")
        print("2. Attendance Portal")
        print("3. Admin Portal")
        print("4. Exit")
        print("Please note that Sales and Attendance Portals can only be accessed during work hours (8AM - 8PM)")

        choice = input("Enter your choice (1-4): ")
        if choice == "1":
            sales_portal()
        elif choice == "2":
            attendance_portal()
        elif choice == "3":
            admin_portal()
        elif choice == "4":
            print("Thank you for using Store AI. Goodbye!")
            break
        else:
            print("Please enter a valid response (1-4)")


# Admin Section
def admin_portal():
    """
    The Admin Portal enables access to the backend session of the Store.
    NB: Only employees who have admin privilages can access this portal and it is not time limited.
    The portal gives users access to the following:
    1. View sales data
    2. View and create employees' salaries
    3. View profit/loss made from sales
    4. View tips from sales
    5. Update Product database
    6. Change existing admin's password and give admin privileges (Only Master Admin Privileges)

    Args:
    None

    Return:
    None (print and update databases)
    """
    employee_id = "E-" + input("Enter your Employee ID: ")
    input_password =input("Enter your master/admin password: ")
    if check_master_password(input_password) or check_admin_password(employee_id, input_password) is True:
        print("\nWelcome to the Admin Portal")
    else:
        print("\nYou do not have access to the Admin Portal")
        return

    while True:
        print("Select the options below")
        print("1. View Sales")
        print("2. Employee Salary")
        print("3. View Profit/Loss")
        print("4. View Tips")
        print("5. Add Product")
        print("6. Admin Password")
        print("7. Back  ")

        admin_choice = input('Enter your choice (1-7): ')
        if admin_choice == "1":
            admin_view_sales()
            break
        elif admin_choice == "2":
            admin_employee_salary()
            break
        elif admin_choice == "3":
            admin_profit_or_loss()
            break
        elif admin_choice == "4":
            admin_employee_tips()
            break
        elif admin_choice == "5":
            admin_product()
            break
        elif admin_choice == "6":
            admin_password()
            break
        elif admin_choice == "7":
            break
        else:
            print("Please, enter the correct option. Choose between (1-7)")

# Calculates employee wages and terminates active sessions
def admin_employee_salary():
    """
    Please, run at the close of each business day.
    This function terminates every active sessions and calculates the wages each employee gets for a day's work
    """
    try:
        employee_wages_df = pd.read_csv("attendance_data.csv")
        check_active_session_df = pd.read_csv("active_session.csv")

    except FileNotFoundError:
        print("You don't have an employee database yet!")
        return

    while True:
        try:
            wage_rate = float(input("How much do you pay your employees per hour? "))
            break
        except ValueError:
            print("Please input only the figures.")
        
    # If some employee did not sign out, replace their Hour Worked with 0
    check_active_session_df["Previous Session"] = check_active_session_df["Previous Session"].replace("Active", "Inactive")
    employee_wages_df["Hours Worked"].fillna(0, inplace=True)  

    employee_pay = round(employee_wages_df["Hours Worked"] * wage_rate, 2)

    employee_wages_df["Wage (N)"] = employee_pay

    grouped_employee_wages = employee_wages_df.groupby(["Date", "Employee ID", "First Name"])["Wage (N)"].sum()
    grouped_employee_wages_df = pd.DataFrame(grouped_employee_wages)
    
    # Saving our DataFrames to CSV files
    grouped_employee_wages_df.to_csv("employee_wages.csv")
    check_active_session_df.to_csv("active_session.csv")

    # Display DataFrame that shows 
    print(grouped_employee_wages_df)

# Updates and add products to the database
def admin_product():
    try:
        # Attempt to read the CSV file into a pandas DataFrame
        a_product_df = pd.read_csv('product_data.csv')
    except FileNotFoundError:
        a_product_df = pd.DataFrame(columns=['Product ID', 'Product Name', 'Selling Price per unit (N)', 'Cost Price per unit (N)'])

    print("Do you want to view or update Product Info database?")            
    view_or_update = input("View or Update: ")
    vu_matches = process.extractOne(view_or_update, ["View", "Update"])

    if vu_matches[0] == "View":
        print(a_product_df)

    else:    
        while True:    
            exit_or_stay = input("Do you want to exit? (y/n)").title()
            if exit_or_stay in ["No","N"]:
                print("Only enter the numerical portion of the Product ID")
                product_id = "P" + input("Enter Product ID: ")
                
                # Check if the product already exists
                existing_product = a_product_df[a_product_df['Product ID'].str.strip() == product_id.strip()]
                # If the product exists
                if not existing_product.empty:
                    print(f"Product '{product_id}' already exists in the inventory.")
                    update_option = input('Do you want to update the existing product? (y/n): ').title()

                    print(a_product_df.loc[a_product_df['Product ID'].str.strip() == product_id.strip()])
                        
                    # If user chooses to update the existing product
                    if update_option in ['Y','Yes']:
                        print("Do you want to update the cost price or selling price or both?")
                        cost_or_selling = input("Enter Cost Price or Selling Price or Both: ")
                        matches = process.extractOne(cost_or_selling, ["Cost Price per unit (N)", "Selling Price per unit (N)", "Both"], score_cutoff= 70)

                        if matches[0] == "Cost Price per unit (N)":
                            while True:
                                try:    
                                    # Get new cost price
                                    new_cost_price = float(input('Enter new cost price per unit: '))
                                    break
                                
                                except ValueError:
                                    print("ERROR! Enter numbers only")
                                    
                            
                            # Update cost price for the existing product
                            a_product_df.loc[a_product_df['Product ID'].str.strip() == product_id.strip(), 
                                ['Cost Price per unit (N)']] = new_cost_price
                                
                            print(f'Product: {product_id} updated successfully.')
                            print(f"{new_cost_price=}")

                        elif matches[0] == "Selling Price per unit (N)":
                            while True:
                                try:
                                    # Get new selling price
                                    new_selling_price = float(input('Enter new selling price per unit: '))
                                    break

                                except ValueError:
                                    print("ERROR! Enter numbers only")
                                    
                                
                            # Update selling price for the existing product
                            a_product_df.loc[a_product_df['Product ID'].str.strip() == product_id.strip(), 
                                ['Selling Price per unit (N)']] = new_selling_price
                                
                            print(f'Product: {product_id} updated successfully.')
                            print(f"{new_selling_price=}")

                        elif matches[0] == "Both":
                            while True:
                                try:
                                    new_cost_price = float(input('Enter new cost price per unit: '))
                                    new_selling_price = float(input('Enter new selling price per unit: '))
                                    break

                                except ValueError:
                                    print("ERROR! Enter numbers only")
                                    

                            a_product_df.loc[a_product_df['Product ID'].str.strip() == product_id.strip(), 
                                ['Cost Price per unit (N)']] = new_cost_price
                            a_product_df.loc[a_product_df['Product ID'].str.strip() == product_id.strip(), 
                                ['Selling Price per unit (N)']] = new_selling_price
                            print(f'Product: {product_id} updated successfully.')
                            print(f"{new_cost_price=}")
                            print(f"{new_selling_price=}")

                        else:
                            print("Please, enter the necessary statements!")
                        
                        # Save the updated DataFrame back to the CSV file
                        a_product_df.to_csv('product_data.csv', index=False)
                        
                        
                    else:
                        # If user chooses not to update, exit the function
                        print('No changes made.')
                        
                
                else:
                    # Prompt user for quantity and price
                    product_name = input("Enter the product name: ")
                    while True:
                        try:
                            selling_price = float(input('Enter selling price per unit: '))
                            cost_price = float(input('Enter cost price per unit: '))
                            break
                        except ValueError:
                            print("ERROR! Enter numbers only")
                            
                    
                    # Add new product to the DataFrame
                    new_product = pd.DataFrame({'Product ID': [product_id], 'Product Name': [product_name],
                                                'Selling Price per unit (N)': [selling_price], 'Cost Price per unit (N)': [cost_price]})
                    a_product_df = pd.concat([a_product_df, new_product], ignore_index=True)
                        
                    # Save the updated DataFrame back to the CSV file
                    a_product_df.to_csv('product_data.csv', index=False)
                    
                    print(f'Product: {product_name} ({product_id})! added successfully!\n')
                    
                    # Print the DataFrame after adding the new product
                    print(a_product_df)
                    #return True
                    
            elif exit_or_stay in ["Y","Yes"]:
                print("Have a pleasant day!")
                break

            else:
                print("Input the correct option")

def admin_view_sales():
    try:
        admin_sales_df = pd.read_csv("admin_sales_data.csv")
    except FileNotFoundError:
        print("ERROR! No sales found.")
        return

    admin_sales_df["Sales Amount (N)"] = admin_sales_df["Selling Price per unit (N)"] * admin_sales_df["Quantity sold"]
    admin_sales_df['Date'] = pd.to_datetime(admin_sales_df['Date'], errors='coerce')

    admin_view_daily_sales = admin_sales_df.groupby(["Date"])["Sales Amount (N)"].sum()
    admin_view_daily_sales = pd.DataFrame(admin_view_daily_sales).reset_index()
    admin_view_shift_sales = admin_sales_df.groupby(["Date", "Shift"])["Sales Amount (N)"].sum()
    admin_view_shift_sales = pd.DataFrame(admin_view_shift_sales).reset_index()

    while True:
        print("You can view the entire sales data, or view particular dates\n")
        print("1. To view the entire sales data")
        print("2. To view today's sales")
        print("3. To view particular dates\n")
        choice = input("Enter your choice: ")

        if choice == "1":
            entire_sales_data_choice = input("Do you want to view the dataset by Shift or Daily? ")
            entire_sales_data_matches = process.extractOne(entire_sales_data_choice, ["Shift", "Daily"])

            if entire_sales_data_matches[0] == "Shift":
                print(admin_view_shift_sales)
            elif entire_sales_data_matches[0] == "Daily":
                print(admin_view_daily_sales)
            else:
                print("Please, input the right option")
                break

        elif choice == "2":
            today_date = date.today()
            today_sales_filter = admin_view_daily_sales['Date'].dt.date == today_date

            while True:
                today_sales_data_choice = input("Do you want to view the dataset by Shift or Daily? ")
                today_sales_data_matches = process.extractOne(today_sales_data_choice, ["Shift", "Daily"])
                if today_sales_data_matches[0] == "Daily":
                    today_daily_sales = admin_view_daily_sales[today_sales_filter]
                    print(today_daily_sales)
                    break

                elif today_sales_data_matches[0] == "Shift":
                    today_shift_sales = admin_view_shift_sales[today_sales_filter]
                    print(today_shift_sales)
                    break

                else:
                    print("Please, input the right option")
            break

        elif choice == "3":
            # Define your date range
            start_date = pd.to_datetime(input("Input start date (format= DD/MM/YYYY): "), dayfirst= True)
            end_date = pd.to_datetime(input("Input end date (format= DD/MM/YYYY): "), dayfirst=True)
            date_sel_sales_filter = (admin_view_shift_sales['Date'] >= start_date) & (admin_view_shift_sales['Date'] <= end_date)

            date_sales_data_choice = input("Do you want to view the dataset by Shift or Daily? ")
            date_sel_sales_data_matches = process.extractOne(date_sales_data_choice, ["Shift", "Daily"])

            while True:
                if date_sel_sales_data_matches[0] == "Daily":
                    date_sel_daily_sales = admin_view_daily_sales[date_sel_sales_filter]
                    print(date_sel_daily_sales)
                    break

                elif date_sel_sales_data_matches[0] == "Shift":
                    today_shift_sales = admin_view_shift_sales[date_sel_sales_filter]
                    print(today_shift_sales)
                    break

                else:
                    print("Please, input the right option")
            break

def admin_employee_tips():
    """
    Calculate tips for a specific date.

    Args:
    None

    Returns:
    None (prints the tips information).
    """
    
    # Calling the dataset that houses the sales data
    try:
        admin_df = pd.read_csv("admin_sales_data.csv", index_col=False)

        # The date column is in str. Convert to datatime
        admin_df["Date"] = pd.to_datetime(admin_df["Date"], errors="coerce")

    except FileNotFoundError:
        print("ERROR! Make sales first")
        return

    # Collects and stores the date(in datetime format) the user wants to get
    selected_date = pd.to_datetime(input("Input the date (format= DD/MM/YYYY): "), dayfirst= True)
    
    # Accounts for empty dates
    if pd.notna(selected_date):

        # If the selected date is not null, then filter the dataset to show the selected date
        filtered_data = admin_df[admin_df["Date"] == selected_date]
        
        # If the filtered data is empty, tell the user no sales were made and exist
        if filtered_data.empty:
            print("No sales was made for that day!")
            return
        
        # Filter the dataset to show a particular shift
        morning_shift_data = filtered_data[filtered_data["Shift"] == "Morning"]
        afternoon_shift_data = filtered_data[filtered_data["Shift"]=="Afternoon"]

        # Calculate the tips for that shift
        morning_shift_tips = calculate_tips(morning_shift_data)
        afternoon_shift_tips = calculate_tips(afternoon_shift_data)
        
        # Calculate the total tips
        total_daily_tips = morning_shift_tips + afternoon_shift_tips

        print(f'\nTips for {selected_date.strftime("%d/%m/%Y")}:') # Convert the date back to str
        print(f'Morning Shift Tips: N{morning_shift_tips}')
        print(f'Afternoon Shift Tips: N{afternoon_shift_tips}')
        print(f'Total Tips for the Day: N{total_daily_tips}')
    else:
        print('Invalid date format. Please enter the date in the format DD/MM/YYYY.')

def calculate_tips(shift_data):
    """
    Calculates the tips gotten from the shift's sales (2% of shift sales)

    Arg: DataFrame

    Return: shift tips: floats
    """

    shift_sales = (shift_data['Quantity sold'] * shift_data['Selling Price per unit (N)']).sum()
    shift_tips = 0.02 * shift_sales
    return shift_tips

def admin_profit_or_loss():
    """
    Determines if sales were profitable or a loss

    Arg:
    None

    Return:
    None (prints a summary of the sales profitability and the entire dataset)
    """

    # Reading the dataset and selecting the necessary columns needed
    try:
        admin_sales_df = pd.read_csv("admin_sales_data.csv", index_col=None)
        admin_sales_df = admin_sales_df.iloc[:, 0:9]
        
        # The date column is in str. Convert to datatime
        admin_sales_df["Date"] = pd.to_datetime(admin_sales_df["Date"], errors="coerce")

    except FileNotFoundError:
        print("ERROR! Make sales first")
        return
    
    # Determine whether a P/L Value of each sales
    admin_sales_df["P/L Value (N)"] = ((admin_sales_df["Selling Price per unit (N)"] - admin_sales_df["Cost Price per unit (N)"]) * admin_sales_df["Quantity sold"]).astype(float)
    
    # Categorizing the P/L Value into Profit or Loss
    admin_sales_df["Profit/Loss"] = admin_sales_df["P/L Value (N)"].apply(P_or_L)

    while True:
        # Filtering it to show a particular date instead of the entire data
        selected_date = pd.to_datetime(input("Please, entered the date you are searching for (DD/MM/YYYY): "), dayfirst=True)
        if pd.notnull(selected_date):
            selected_sales_df = admin_sales_df[admin_sales_df["Date"] == selected_date]
            if selected_sales_df.empty:
                print("No sales were made")
            
            summarized_profit_or_loss = selected_sales_df.groupby(["Date"])["P/L Value (N)"].sum()
            print(f"\nSummary for {selected_date.strftime('%d/%m/%Y')} sales: ")
            print(f"\nWe made a {P_or_L(summarized_profit_or_loss[0])} of N{summarized_profit_or_loss[0]}")

            print(f"\nSee the full sales for {selected_date.strftime('%d/%m/%Y')}\n")
            print(selected_sales_df)
            break
        else:
            print('Invalid date format. Please enter the date in the format DD/MM/YYYY.')


def P_or_L(x):
    """
    Checks if sales was a profit or loss

    Arg:
    x -> numeric value (float|int)

    Return:
    str | (Profit, Loss or null)
    """
    if x < 0:
        return "Loss"
    elif x > 0:
        return "Profit"
    else:
        return
    
def admin_password():
    """
    Adds new admin users and passwords as well as update/change existing passwords
    Only Master Admins can access this section

    Args:
    None

    Return:
    None (Saves the encrypted version of admins' passwords to CSV)
    """
    input_password =input("Enter your master admin password: ")
    if check_master_password(input_password) is True:
        print("Welcome Master Admin")
    else:
        print("You do not have access to this portion of Admin Portal")
        return

    try:
        df = pd.read_csv("admin_password.csv", index_col=False)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Employee ID", "Encrypted Password"])


    employee_id = "E-" + input("Enter your ID: ")
    check_employee = df[df["Employee ID"] == employee_id]
    if not check_employee.empty:
        print("This employee already have a password.")
    
        change_password = input("Do you want to change the password? (y/n): ").title()

        if change_password in ["Yes", "Y"]:
            new_password = input("Enter your new password: ")
            confirm_new_password = input("Enter your new password again: ")
            
            if new_password == confirm_new_password:
                df.loc[df["Employee ID"]== employee_id, ["Encrypted Password"]] = encrypt_passcode(confirm_new_password)
                df.to_csv("admin_password.csv", index=False)
                print("Password has been changed")
                return
            else:
                print("Incorrect password, try again!")
                return
                      
        else:
            print("Password was not changed")
            return

    else:
        first_name = input("Enter your First Name: ").title()
        password = input("Enter your password: ")
        confirm_password = input("Enter your password again: ")

        if password == confirm_password:
            new_entry = pd.DataFrame([{"Employee ID": employee_id,
                                        "Encrypted Password": encrypt_passcode(confirm_password)}])
            df = pd.concat([df,new_entry], ignore_index=True)
            df.to_csv("admin_password.csv", index=False)
            print(f"({first_name} (Employee ID: {employee_id}), your password has been added)")
        else:
            print("The passwords you provided are not the same. Check it and try again!")


def encrypt_password(passcode):
    """
    Encrypts passwords using cryptography library

    Args:
    passcode: user/admin inputed passwords

    Return:
    encrypted passwords (in bytes)
    """

    # To get the encryption key, you need to generate the key. Do that by using "Fernet.generate_key()"
    # I noticed that it keeps changing whenever I ran it. So, I decided to stick to one encryption key through out
    encryption_key = b'NgsT2QKqjpwgbAFzfat2yvPEkWQuzRrtSV5DPEwlZRs=' # Keep safe. NB: It is in bytes format
    cipher = Fernet(encryption_key)

    # Encrypts the passcode. NB: .encrypt() only takes bytes dtypes. The .encode() changes the str to bytes
    encrypted_password = cipher.encrypt(passcode.encode())
    return encrypted_password

def decrypt_password(encrypted_password):
    """
    Decrypts 32-bytes encoded passwords

    Args:
    encrypted_password: bytes encrypted passwords

    Return:
    decrypted passwords (str)
    """
    encryption_key = b'NgsT2QKqjpwgbAFzfat2yvPEkWQuzRrtSV5DPEwlZRs='
    cipher = Fernet(encryption_key)

    # Decrypts the encrypted password and .decode() changes it from bytes to str
    decrypted_password = cipher.decrypt(encrypted_password)
    return decrypted_password.decode()


def check_master_password(password):
    """
    Checks if the user provided a master password.

    Args:
    password: User input password

    Return:
    Bool
    """
    master_password = b'gAAAAABljVQDrkEUJKOltUkA96YCuVXtxQqIgSMyZBxXmPwRUmaRhUn19lXGsElRX7cYGuB_8udJYeaJFLX_IBlSxMfudCuRpg=='
    if password == decrypt_password(master_password):
        return True
    return False


def check_admin_password(employee_id, input_password):
    """
    Checks if the user provided an admin password.

    Args:
    employee_id: Any (Employee ID of user)
    input_password: Any (User password inputs)

    Returns:
    Bool|None

    """

    df = pd.read_csv("admin_password.csv", index_col=False)
    for index, row in df.iterrows():
        if row['Employee ID'] == employee_id:
            decrypted_password = row['Encrypted Password']
            decrypted_password = decrypt_passcode(row['Encrypted Password'])
            if input_password == decrypted_password:
                return True
            else:
                return False


def get_key():
    """
    Generate or read stored encryption key used to cipher and decipher passwords

    Paramters:
    None:

    Return:
    tuple[list[str], list[str]]    
    """
    key_file = "secret.key"

    if os.path.exists(key_file):
        # Read the key from the file
        with open(key_file, "r") as file:
            key = file.read()
        
    else:
        # Generate key
        chars = " " + string.ascii_letters + string.punctuation + string.digits
        key = list(chars)
        random.shuffle(key) # Shuffles the characters 
        key = "".join(key)  # Convert the list to a string

        # Save key to the file
        with open(key_file, "w") as file:
            file.write(key)

    # Make key and chars lists to loop through the list
    key = list(key)
    chars = " " + string.ascii_letters + string.punctuation + string.digits
    chars = list(chars)
    return key, chars


def encrypt_passcode(confirm_password):
    """
    Encrypts passwords using strings and random

    Args:
    passcode: user/admin inputed passwords

    Return:
    encrypted passwords (str)
    """
    # Get the key and characters used in encrypting the 
    key, characters = get_key()
    encrypted_password = ""

    for letter in confirm_password:
        index = characters.index(letter)
        encrypted_password += key[index]
    return (encrypted_password)


def decrypt_passcode(encrypted_password):
    """
    Encrypts passwords using strings and random

    Args:
    encrypted passcode: admin encrypted passwords

    Return:
    decrypted passwords (str)
    """
    key, characters = get_key()
    decrypted_password = ""

    for letter in encrypted_password:
        index = key.index(letter)
        decrypted_password += characters[index]
    return (decrypted_password)



# Attendance Portal
# Whole attendance sub menu
def attendance_portal():
    '''
    This function enables employee to clock in and clock out only during operational hours.
    Employees can access it 30 mins before and after operational hours
    Failure to do that means that they were not available for their shift and they wont be paid for that day.
    '''
    current_time = datetime.now().strftime("%H:%M")
    # Using a real world scenario, can employee should only be able to clock in/out during office hours (in this case, from 8AM - 8PM)
    if "07:30" <= current_time <= "20:30":

        # Checking if there is a dataset that stores attendance data. If there isn't create one
        try:
            attendance_df = pd.read_csv("attendance_data.csv")
        except FileNotFoundError:
            columns = ["Date", "Employee ID", "First Name", "Last Name", 
                       "Sign In Time", 'Sign Out Time', "Shift", "Hours Worked"]
            attendance_df = pd.DataFrame(columns=columns)

        # Checking the previous logs of employees to know if they have an active or inactive session.
        # Active session means the employee has clocked in and inactive means the employee has clocked out.
        try:
            check_active_session_df = pd.read_csv("active_session.csv")

            # If the file exist, create a dict. The Employee ID will be the key Previous Session status will be the value
            check_active_session = dict(zip(check_active_session_df["Employee ID"], check_active_session_df["Previous Session"]))
        except FileNotFoundError:
            check_active_session = {} # If the file does not exist, create an empty dict
        

        while True:
            print("\nWelcome! Please, don't forget to clock in and clock out.\n")
            print("Select the options below")
            print("1. Clock In")
            print("2. Clock Out")
            print("3. Back")

            employee_attendance_choice = input('Enter your choice (1-3): ')
            if employee_attendance_choice == "1":
                clock_in(attendance_df, check_active_session)
                break
            elif employee_attendance_choice == "2":
                clock_out(attendance_df, check_active_session)
                break
            elif employee_attendance_choice == "3":
                break
            else:
                print("Select an option between 1 and 3")

    else:
        print("You cannot access the Attendance Portal outside working hours")

def clock_in(attendance_df, check_active_session):
    '''
    This function enables employees to clock in for their session.
    It checks if the employee has an active session, if they do, they will not be able to clock in
    The function asks the employee to input their ID, first name and last name
    '''
    current_date = date.today()
    current_time = datetime.now().strftime("%H:%M")

    if "08:00" <= current_time <= "14:00":
        shift = "Morning"
    elif "14:00" <= current_time <= "20:00":
        shift = "Afternoon"
    else:
        shift = "Outside Operation Time"

    employee_id = "E-" + input("Please, enter your Employee ID: ").strip()
    employee_first_name = input("Please, enter your First Name: ").title().strip()
    employee_last_name = input("Please, enter your Last Name(Surname): ").title().strip()

    # This loop through the check_active_session dict to search for the employee_id (dict key). Also, it checks the value assigned to that particular dict key
    # If the value is Active, it means that the user has not signed out from their previous session
    if employee_id in check_active_session and check_active_session[employee_id] == "Active":
        print(f"{employee_first_name}, you haven't clocked out from your previous session. Please clock out before clocking in again.")
        return

    # If it does not meet the criteria, then sign them in by populating the attendance dataset    
    else:
        new_entry = [str(current_date), employee_id, employee_first_name, employee_last_name, current_time, '', shift, '']
        attendance_df = pd.concat([attendance_df, pd.DataFrame([new_entry], columns=attendance_df.columns)], ignore_index=True)
                
        # After signing them in, their session is changed to Active
        check_active_session[employee_id] = 'Active'

        # Convert the dict into a df for it to be stored in a CSV file
        check_active_session_df = pd.DataFrame(list(check_active_session.items()), columns = ["Employee ID", "Previous Session"])
                              
        # Save attendance_data CSV file and active_session CSV files respectively
        try:
            attendance_df.to_csv("attendance_data.csv", index=False)
            check_active_session_df.to_csv("active_session.csv", index=False)
            print(f"{employee_first_name} (Employee ID: {employee_id}), you signed in at {current_time}.")
            return
        
        except PermissionError:     # I noticed that it gives this error whenever the dataset is open.
            print("Error: PermissionError. Please make sure the CSV files are not open and try again.")
            return

def clock_out(attendance_df, check_active_session):
    '''
    This enables employee to clock out.
    It checks if the employee has an active session and signs them out. 
    If they do, it clocks them out. Else, it tells them to sign in first

    Parameters:
    attendance_df: DataFrame
    check_active_session: DataFrame

    Return:
    None
    '''
    current_time = datetime.now().strftime("%H:%M")
    employee_id = "E-" + input("Please, enter your Employee ID: ").strip()
    employee_first_name = input("Please, enter your First Name: ").title().strip()

    # It checks if they have an active session, calculate the hours they worked (time diff) and signs them out
    if employee_id in check_active_session and check_active_session[employee_id] == "Active":
        last_entry = attendance_df[(attendance_df['Employee ID'] == employee_id)].tail(1)
        attendance_df.loc[last_entry.index, 'Sign Out Time'] = current_time
        timediff(attendance_df)

        # Changes their session to inactive to enable them sign out
        check_active_session[employee_id] = 'Inactive'
        check_active_session_df = pd.DataFrame(list(check_active_session.items()), columns = ["Employee ID", "Previous Session"])

        # Update attendance_data CSV file and active_session CSV files respectively        
        try:
            attendance_df.to_csv("attendance_data.csv", index=False)
            check_active_session_df.to_csv("active_session.csv", index=False)
            print(f"{employee_first_name}, thank you for your service! You signed out at {current_time}. Goodbye and enjoy the rest of your day!")
            return
            
        except PermissionError:     # I noticed that it gives this error whenever the dataset is open.
            print("Error: PermissionError. Please make sure the CSV files are not open and try again.")
            return

    else:
        print(f"{employee_first_name}, you need to sign in first!")
        return

def timediff(attendance_df):
    '''
    This function calculates the time difference between the clock in and clock out and return the difference in hours
    '''
    # The datatypes of the Sign In Time and Sign Out Time are str. In order to get the result, it needs to be changed to datetime
    attendance_df['Sign Out Time'] = pd.to_datetime(attendance_df['Sign Out Time'])
    attendance_df['Sign In Time'] = pd.to_datetime(attendance_df['Sign In Time'])

    # Populate the Hours worked columns with the hourly time diff in 2 decimal places
    attendance_df["Hours Worked"] = round((attendance_df['Sign Out Time'] - attendance_df['Sign In Time']).dt.total_seconds()/3600, 2)

    # For consistence and to remove the dates attached, change the format to HH:MM
    attendance_df['Sign Out Time'] = attendance_df['Sign Out Time'].dt.strftime("%H:%M")
    attendance_df['Sign In Time'] = attendance_df['Sign In Time'].dt.strftime("%H:%M")


# Sales Portal
def sales_portal():
    """
    A portal that calls values sales function.
    This portal can only be accessed within operation hours (8AM - 8PM)

    Parameter:
    None

    Return:
    None
    """
    current_time = datetime.now().strftime("%H:%M")
    
    # Using a real world scenario, can employee should only access it during office hours (in this case, from 8AM - 8PM)
    if "08:00" <= current_time <= "20:00":
        while True:
            print("\nWelcome to the sales portal!\n")
            print("Select the options below")
            print("1. Make Sales")
            print("2. View Product List")
            print("3. Back")
            
            employee_sales_choice = input('Enter your choice (1-3): ')
            if employee_sales_choice == "1":
                _sales()
                break
            elif employee_sales_choice == "2":
                employee_product()
                break
            elif employee_sales_choice == "3":
                break
            else:
                print("Select an option between 1 and 3")
    
    else:
        print("You can not access this portal outside working hours")

# Add sales
def _sales():
    """
    Populates the databases with the appropriate data.
    It prints the 'sales recipts' of what the customer bought

    Parameters:
    None

    Return
    None (Prints neccessary information)
    """
    # Every employee must clock in before they can attend to customers
    while True:
        clocked_in = input("Have you clocked in today? (yes/no) ").title()
        if clocked_in in ["Yes", "Y"]:
            print("You can proceed")
            break
        elif clocked_in in ["No", "N"]:
            print("You are being diverted to the Attendance Portal to clock in!")
            attendance_portal()
            break
        else:
            print("Please, input a valid response (yes/no)")
    

    sale_receipt = pd.DataFrame(columns=["Sales ID", "Product ID", "Quantity sold", "Date","Time", "Shift"])
    
    # Reading Product Data dataset into a DataFrame. If it does not exist, tell the admin to create one
    try: 
        product_data_df = pd.read_csv("product_data.csv")
    except FileNotFoundError:
        print("Contact admin to create a product database")
        return
    
    # Reading the CSV files and if they do not exist, create them.
    try: 
        sales_data_df = pd.read_csv("sales_data.csv")
        previous_admin_sales = pd.read_csv("admin_sales_data.csv")

    except FileNotFoundError:
        sales_data_df = pd.DataFrame(columns=["Sales ID", "Product ID", "Quantity sold", "Date","Time", "Shift"])
        previous_admin_sales = pd.DataFrame(columns=["Sales ID", "Product ID", "Quantity sold", "Date","Time", "Shift",
                                                     "Product Name",	"Selling Price per unit (N)", "Cost Price per unit (N)"])
        # I cut a code from here to fix a bug. Check cell above

    # A customer might have one than one product to buy. Keep on adding those products until you have scanned all
    while True:
        new_sale = new_sales(sales_data_df, product_data_df)
        sale_receipt = pd.concat([sale_receipt, new_sale], ignore_index=True)
        if not new_sale.empty:
            print("\nThe sales has been added")

        more_sales = input("Do you still have more product to scan? (y/n): ").title()

        # If they have more products, keep scanning them
        if more_sales in ["Y", "Yes"]:
            continue
        else:       # If there aren't more products, proceed to checkout
            # Since products' selling price are stored in a different dataset, get the selling price from that dataset
            customer_sale_receipt = pd.merge(sale_receipt, product_data_df, on= "Product ID", how= "left")
            
            # Saving it to a new dataset strickly for admins
            admin_sales_data_df = pd.concat([previous_admin_sales, customer_sale_receipt], ignore_index=True)
            admin_sales_data_df.to_csv("admin_sales_data.csv", index=False)

            # The customer needs a receipt and needs to know the amount they are to pay
            customer_sale_receipt = customer_sale_receipt[["Date", "Sales ID", "Product ID", "Quantity sold", "Selling Price per unit (N)"]]

            # Convert the 'Quantity sold' column to numeric
            customer_sale_receipt["Quantity sold"] = pd.to_numeric(customer_sale_receipt["Quantity sold"], errors='coerce')

            customer_sale_receipt["Amount (N)"] = customer_sale_receipt["Selling Price per unit (N)"] * customer_sale_receipt["Quantity sold"]
            
            if not new_sale.empty:
                # groupby can not work on empty DataFrame
                customer_sale_receipt_group = customer_sale_receipt.groupby(["Date"])["Amount (N)"].sum().values # .values Convert groupby series to np numbers
                customer_sale_receipt_group = float(customer_sale_receipt_group[0])
                print(customer_sale_receipt)
                print(f"Please, pay N{customer_sale_receipt_group}")
                print("Thank you and enjoy the rest of your day!")

            break # This terminates the loop
    sales_data_df = pd.concat([sales_data_df, sale_receipt], ignore_index=True)
    sales_data_df.to_csv("sales_data.csv", index=False)

def new_sales(sales_data_df, product_data_df):
    """
    This function checks if a product is in the Product database
    If it is in the database, it collects data about the quantity of goods the customer is buying.
    If it isn't, it returns an empty df

    Parameters:
    sales_data_df: A df that contains sales data
    product_data_df: A df that contains product data

    Return:
    DataFrame
    """
    new_product_id = "P" + (input("Please input the Product's ID: "))
    if new_product_id not in product_data_df["Product ID"].values:
        print(f"\nNo product with Product ID: {new_product_id} found. Product does not exist")
        print(f"Set Product ID: {new_product_id} aside and continue with other products in their cart.")
        print("Contact Admin to update the product list.")
        return pd.DataFrame()
    
    if sales_data_df.empty:
        new_sales_id = 1
    else:
        new_sales_id = (sales_data_df["Sales ID"].max() + 1)

    #new_product_id = "P" + (input("Please input the Product's ID: "))
    new_date = date.today()
    new_time = datetime.now().strftime("%H:%M")
    while True:
        try:
            new_quantity = int(input("What is the quantity? "))
            break
        except ValueError:
            print("Input numeric data only!")

    if "08:00" <= new_time <= "14:00" :
        new_shift = "Morning"
    elif "14:00" <= new_time <= "20:00":
        new_shift=  "Afternoon"
    else:
        new_shift = "Outside Operation Time"

    
    new_sale = pd.DataFrame({"Sales ID": new_sales_id,
                             "Product ID": new_product_id,
                             "Quantity sold": new_quantity,
                             "Date": new_date,
                             "Time": new_time,
                             "Shift": new_shift
                             }, index=[0])
    
    return new_sale

def employee_product():
    """
    Prints the Product database only

    Parameters:
    None

    Return
    None
    """
    try:
        employee_product_df = pd.read_csv("product_data.csv")
        print(employee_product_df)
    except FileNotFoundError:
        print("ERROR! Please, contact admin to create a product database")
        return
