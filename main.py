from datetime import datetime,timedelta
import sqlite3

class Vehicle:

    def __init__(self,vehicle_id,name,price_per_day):

        self.vehicle_id = vehicle_id
        self.name = name
        self.price_per_day = price_per_day
        self.status = "Available"

    def display(self):
        print("VehicleId      :",self.vehicle_id)
        print("Name           :",self.name)
        print("VehicleType    :",self.vehicle_type)
        print("PricePerDay    :",self.price_per_day)
        print("Status         :",self.status)

class Car(Vehicle):

    def __init__(self, vehicle_id, name, price_per_day,seats):
        super().__init__(vehicle_id, name, price_per_day)

        self.seats = seats
        self.vehicle_type = "Car"
        self.extra = seats

    def display(self):
        super().display()
        print("Seats          :",self.seats)

class Bike(Vehicle):
    def __init__(self, vehicle_id, name, price_per_day, engine_cc):
        super().__init__(vehicle_id, name,price_per_day)

        self.engine_cc = engine_cc
        self.vehicle_type = "Bike"
        self.extra = engine_cc

    def display(self):
        super().display()
        print("Engine CC      :", self.engine_cc)


class Customer:
    def __init__(self,customer_id, name, phone_no,password):
        self.customer_id = customer_id
        self.name = name
        self.phone_no = phone_no
        self.password = password

    def display(self):
        print("Customer Details")
        print("CustomerID        :", self.customer_id)
        print("CustomerName      :", self.name)
        print("PhoneNo           :", self.phone_no)


class Rental:
    def __init__(self,customer, vehicle, days):
        self.customer = customer
        self.vehicle = vehicle
        self.days = days
        self.start_date = datetime.now()
        self.return_date = self.start_date + timedelta(days=days)
        self.status = "Active"
        self.payment_status = "Pending"
        self.fine = 0
        self.fine_payment_status = "Not Applicable"
        self.actual_return_date = None
    def calculate_amount(self):
        return self.vehicle.price_per_day * self.days

    def check_overdue(self):

        if self.status != "Active":
            return False

        current_date = datetime.now()

        if current_date > self.return_date:
            return True

        return False

    def rent(self):

        if self.vehicle.status != "Available":

            print("Vehicle is Not Available")
            return False

        payment_success = self.make_payment()

        if payment_success:

            self.vehicle.status = "Rented"
            self.status = "Active"

            # Update vehicle status in database
            connection = sqlite3.connect("vehicle_rental.db")
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE vehicles
                SET status = ?
                WHERE vehicle_id = ?
            """, (
                "Rented",
                self.vehicle.vehicle_id
            ))

            connection.commit()
            connection.close()

            print("\nVehicle Rented Successfully")

            return True

        else:

            print("\nRental Cancelled")

            return False

    def return_vehicle(self):

        actual_return_date = datetime.now()

        # IMPORTANT
        self.actual_return_date = actual_return_date

        self.vehicle.status = "Available"
        self.status = "Completed"

        if actual_return_date > self.return_date:

            late_days = (
                actual_return_date.date()
                - self.return_date.date()
            ).days

            fine_per_day = 500

            # ADD THESE LINES
            print("\n===== FINE PREVIEW =====")
            print("Expected Return :", self.return_date.strftime("%d-%m-%Y"))
            print("Actual Return   :", actual_return_date.strftime("%d-%m-%Y"))
            print("Late Days       :", late_days)
            print("Fine            :", late_days * fine_per_day)
            print("========================")

            self.fine = late_days * fine_per_day
            self.fine_payment_status = "Unpaid"
        else:

            self.fine = 0
            self.fine_payment_status = "Not Applicable"

            print("\nVehicle Returned On Time")
            print("Fine :", self.fine)

        # Database
        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE vehicles
            SET status = ?
            WHERE vehicle_id = ?
        """, (
            "Available",
            self.vehicle.vehicle_id
        ))

        cursor.execute("""
            UPDATE rentals
            SET status = ?,
                fine = ?,
                fine_payment_status = ?,
                actual_return_date = ?
            WHERE customer_id = ?
            AND vehicle_id = ?
            AND status = 'Active'
        """, (
            self.status,
            self.fine,
            self.fine_payment_status,
            self.actual_return_date.strftime("%Y-%m-%d %H:%M:%S"),
            self.customer.customer_id,
            self.vehicle.vehicle_id
        ))

        connection.commit()
        connection.close()

        print("Vehicle Returned Successfully")
        

    def display_receipt(self):

        print("\n========== RENTAL RECEIPT ==========")

        print("Customer ID         :", self.customer.customer_id)
        print("Customer            :", self.customer.name)

        print("Vehicle ID          :", self.vehicle.vehicle_id)
        print("Vehicle             :", self.vehicle.name)

        print("Price/Day           :", self.vehicle.price_per_day)
        print("Days                :", self.days)

        print("Start Date          :", self.start_date.strftime("%d-%m-%Y"))
        print("Expected Return     :", self.return_date.strftime("%d-%m-%Y"))
        
        if self.actual_return_date:
            print("Actual Return   :", self.actual_return_date.strftime("%d-%m-%Y"))
        else:
            print("Actual Return   : Not Returned")

        print("Total Amount        :", self.calculate_amount())

        print("Payment             :", self.payment_status)

        if self.status == "Active" and self.check_overdue():

            late_days = (datetime.now().date() - self.return_date.date()).days

            print("Status      : OVERDUE")
            print("Late Days   :", late_days)

        else:

            print("Status      :", self.status)

        print("Fine                :", self.fine)
        print("Fine Status         :", self.fine_payment_status)

        print("=====================================")

    def make_payment(self):

        amount = self.calculate_amount()

        print("\n===== PAYMENT =====")
        print("Amount:", amount)

        print("1. UPI")
        print("2. Card")
        print("3. Cash")

        choice = int(input("Choose Payment Method: "))

        if choice == 1:

            print("UPI Payment Successful")

        elif choice == 2:

            print("Card Payment Successful")

        elif choice == 3:

            print("Cash Payment Successful")

        else:

            print("Invalid Payment Method")
            return False

        self.payment_status = "Paid"

        return True

    def pay_fine(self):

        if self.fine == 0:

            print("No Fine To Pay")
            return

        if self.fine_payment_status == "Paid":

            print("Fine Already Paid")
            return

        print("\n===== FINE PAYMENT =====")
        print("Fine Amount :", self.fine)

        print("\n1. UPI")
        print("2. Card")
        print("3. Cash")

        choice = int(input("Choose Payment Method: "))

        if choice == 1:

            print("UPI Payment Successful")

        elif choice == 2:

            print("Card Payment Successful")

        elif choice == 3:

            print("Cash Payment Successful")

        else:

            print("Invalid Payment Method")
            return

        self.fine_payment_status = "Paid"

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE rentals
            SET fine_payment_status = ?
            WHERE customer_id = ?
            AND vehicle_id = ?
        """, (
            "Paid",
            self.customer.customer_id,
            self.vehicle.vehicle_id
        ))

        connection.commit()
        connection.close()

        print("Fine Paid Successfully")

class VehicleManager:

    def __init__(self):
        self.vehicles = []
        self.load_vehicles()

    def add_vehicle(self, vehicle):

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO vehicles
                (vehicle_id, name, price, status, vehicle_type, extra)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                vehicle.vehicle_id,
                vehicle.name,
                vehicle.price_per_day,
                vehicle.status,
                vehicle.vehicle_type,
                vehicle.extra
            ))

            connection.commit()

            self.vehicles.append(vehicle)

            print(vehicle.name, "Added Successfully")

        except sqlite3.IntegrityError:

            print("Vehicle ID Already Exists")

        finally:

            connection.close()

    def load_vehicles(self):

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT vehicle_id, name, price, status, vehicle_type, extra
            FROM vehicles
        """)

        rows = cursor.fetchall()

        connection.close()

        for row in rows:

            vehicle_id = row[0]
            name = row[1]
            price = row[2]
            status = row[3]
            vehicle_type = row[4]
            extra = row[5]

            if vehicle_type == "Car":

                vehicle = Car(
                    vehicle_id,
                    name,
                    price,
                    extra
                )

            else:

                vehicle = Bike(
                    vehicle_id,
                    name,
                    price,
                    extra
                )

            vehicle.status = status

            self.vehicles.append(vehicle)

    def view_vehicles(self):

        if len(self.vehicles) == 0:
            print("No Vehicles Available")
            return
        for vehicle in self.vehicles:
            vehicle.display()
            print("------------------------------")

    def search_vehicle(self, id):

        for vehicle in self.vehicles:
            if vehicle.vehicle_id == id:
                return vehicle
        return None

    def update_vehicle(self, vehicle_id):

        vehicle = self.search_vehicle(vehicle_id)

        if vehicle is None:

            print("Vehicle Not Found")
            return

        print("\nCurrent Vehicle Details:")
        vehicle.display()

        print("\nEnter New Details")

        new_name = input("Enter New Name: ")
        new_price = float(input("Enter New Price: "))

        vehicle.name = new_name
        vehicle.price = new_price

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE vehicles
            SET name = ?, price = ?
            WHERE vehicle_id = ?
        """, (
            vehicle.name,
            vehicle.price_per_day,
            vehicle.vehicle_id
        ))

        connection.commit()
        connection.close()

        print("Vehicle Updated Successfully")

    def delete_vehicle(self, vehicle_id):

        vehicle = self.search_vehicle(vehicle_id)

        if vehicle is None:
            print("Vehicle Not Found")
            return

        if vehicle.status == "Rented":
            print("Cannot Delete a Rented Vehicle")
            return

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        connection.commit()
        connection.close()

        self.vehicles.remove(vehicle)

        print(vehicle.name, "Deleted Successfully")
    def view_available_vehicles(self):

        found = False

        for vehicle in self.vehicles:

            if vehicle.status == "Available":

                vehicle.display()
                print("------------------------------")

                found = True

        if found == False:

            print("No Available Vehicles")

    def get_vehicle_statistics(self):

        total = len(self.vehicles)

        available = 0
        rented = 0

        for vehicle in self.vehicles:

            if vehicle.status == "Available":
                available += 1

            elif vehicle.status == "Rented":
                rented += 1

        return total, available, rented

    def search_vehicles(self):

        while True:

            print("\n===== SEARCH VEHICLE =====")
            print("1. Search by Name")
            print("2. Search by Type")
            print("3. Search by Maximum Price")
            print("4. Search Available Vehicles")
            print("5. Back")

            choice = int(input("Enter Your Choice: "))

            if choice == 1:

                name = input("Enter Vehicle Name: ").lower()

                found = False

                for vehicle in self.vehicles:

                    if name in vehicle.name.lower():

                        vehicle.display()
                        found = True

                if not found:
                    print("No Vehicle Found")

            elif choice == 2:

                vehicle_type = input("Enter Vehicle Type: ").lower()

                found = False

                for vehicle in self.vehicles:

                    if vehicle.vehicle_type.lower() == vehicle_type:

                        vehicle.display()
                        found = True

                if not found:
                    print("No Vehicle Found")

            elif choice == 3:

                max_price = float(
                    input("Enter Maximum Price Per Day: ")
                )

                found = False

                for vehicle in self.vehicles:

                    if vehicle.price_per_day <= max_price:

                        vehicle.display()
                        found = True

                if not found:
                    print("No Vehicle Found")

            elif choice == 4:

                found = False

                for vehicle in self.vehicles:

                    if vehicle.status == "Available":

                        vehicle.display()
                        found = True

                if not found:
                    print("No Available Vehicles")

            elif choice == 5:

                break

            else:

                print("Invalid Choice")

    def sort_vehicles_by_price(self):

        if len(self.vehicles) == 0:
            print("No Vehicles Found")
            return

        sorted_vehicles = sorted(
            self.vehicles,
            key=lambda vehicle: vehicle.price_per_day
        )

        print("\n===== VEHICLES BY PRICE =====")

        for vehicle in sorted_vehicles:

            print("Vehicle ID :", vehicle.vehicle_id)
            print("Name       :", vehicle.name)
            print("Price      :", vehicle.price_per_day)
            print("Status     :", vehicle.status)
            print("--------------------")

    def filter_by_type(self):

        vehicle_type = input("Enter Vehicle Type: ").lower()

        found = False

        print("\n===== VEHICLES =====")

        for vehicle in self.vehicles:

            if vehicle.vehicle_type.lower() == vehicle_type:

                print("Vehicle ID :", vehicle.vehicle_id)
                print("Name       :", vehicle.name)
                print("Type       :", vehicle.vehicle_type)
                print("Price      :", vehicle.price_per_day)
                print("Status     :", vehicle.status)
                print("--------------------")

                found = True

        if not found:
            print("No Vehicles Found")

    

class CustomerManager:

    def __init__(self):

        self.customers = []
        self.load_customers()

    def add_customer(self, customer):

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO customers
                (customer_id, name, phone, password)
                VALUES (?, ?, ?, ?)
            """, (
                customer.customer_id,
                customer.name,
                customer.phone_no,
                customer.password
            ))

            connection.commit()

            self.customers.append(customer)

            print(customer.name, "Registered Successfully")

        except sqlite3.IntegrityError:

            print("Customer ID Already Exists")

        finally:

            connection.close()

    def load_customers(self):

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT customer_id, name, phone, password
            FROM customers
        """)

        rows = cursor.fetchall()

        connection.close()

        for row in rows:

            customer = Customer(
                row[0],
                row[1],
                row[2],
                row[3]
            )

            self.customers.append(customer)
        
    def register_customer(self):

        customer_id = int(input("Enter Customer ID: "))
        name = input("Enter Customer Name: ")
        phone = input("Enter Phone Number: ")
        password = input("Create a Password:")

        customer = Customer(customer_id, name, phone,password)

        self.add_customer(customer)

    def view_customers(self):

        if len(self.customers) == 0:

            print("No Customers Available")
            return

        for customer in self.customers:

            customer.display()

            print("----------------")

    def search_customer(self, customer_id):

        for customer in self.customers:

            if customer.customer_id == customer_id:

                return customer

        return None
    

    def customer_login(self):

        customer_id = int(input("Enter Customer ID: "))
        password = input("Enter Password: ")

        customer = self.search_customer(customer_id)

        if customer is None:

            print("Customer Not Found")
            return None

        if customer.password == password:

            print("Login Successful")
            return customer

        else:

            print("Invalid Password")
            return None

    def get_customer_count(self):

        return len(self.customers)
        

class RentalManager:

    def __init__(self):

        self.rentals = []

    def add_rental(self, rental):

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO rentals
            (
                customer_id,
                vehicle_id,
                days,
                start_date,
                return_date,
                status,
                payment_status,
                fine
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rental.customer.customer_id,
            rental.vehicle.vehicle_id,
            rental.days,
            rental.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            rental.return_date.strftime("%Y-%m-%d %H:%M:%S"),
            rental.status,
            rental.payment_status,
            rental.fine
        ))

        connection.commit()
        connection.close()

        self.rentals.append(rental)

        print("Rental Added Successfully")

    def load_rentals(self, manager, customer_manager):

        connection = sqlite3.connect("vehicle_rental.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                rental_id,
                customer_id,
                vehicle_id,
                days,
                start_date,
                return_date,
                status,
                payment_status,
                fine,
                fine_payment_status
            FROM rentals
        """)

        rows = cursor.fetchall()

        connection.close()

        for row in rows:

            customer = customer_manager.search_customer(row[1])
            vehicle = manager.search_vehicle(row[2])

            if customer is None or vehicle is None:
                continue

            rental = Rental(customer, vehicle, row[3])

            rental.start_date = datetime.strptime(
                row[4],
                "%Y-%m-%d %H:%M:%S"
            )

            rental.return_date = datetime.strptime(
                row[5],
                "%Y-%m-%d %H:%M:%S"
            )

            rental.status = row[6]
            rental.payment_status = row[7]
            rental.fine = row[8]
            rental.fine_payment_status = row[9]

            self.rentals.append(rental)

    def find_rental(self, customer_id, vehicle_id):

        for rental in self.rentals:

            if (rental.customer.customer_id == customer_id
                    and rental.vehicle.vehicle_id == vehicle_id
                    and rental.status == "Active"):

                return rental

        return None

    def view_all_rentals(self):

        if len(self.rentals) == 0:

            print("No Rentals Found")
            return

        print("\n========== ALL RENTALS ==========")

        for rental in self.rentals:

            print("Customer :", rental.customer.name)
            print("Vehicle  :", rental.vehicle.name)
            print("Days     :", rental.days)
            print("Amount   :", rental.calculate_amount())
            print("Status   :", rental.status)
            print("Payment  :", rental.payment_status)
            print("Fine     :", rental.fine)

            print("--------------------------------")

    def view_rentals(self):

        if len(self.rentals) == 0:

            print("No Rentals Available")
            return

        for rental in self.rentals:

            print("Customer :", rental.customer.name)
            print("Vehicle  :", rental.vehicle.name)
            print("Days     :", rental.days)
            print("Amount   :", rental.calculate_amount())

            print("-------------------------")

    def return_vehicle(self, customer_id, vehicle_id):

        for rental in self.rentals:

            if (rental.customer.customer_id == customer_id
                    and rental.vehicle.vehicle_id == vehicle_id):

                if rental.status == "Active":

                    rental.return_vehicle()

                else:

                    print("Rental Already Completed")

                return

        print("Rental Not Found")

    def view_my_rentals(self, customer_id):

        found = False

        for rental in self.rentals:

            if rental.customer.customer_id == customer_id:

                print("\n===== MY RENTAL =====")
                print("Id      :", rental.vehicle.vehicle_id)
                print("Vehicle :", rental.vehicle.name)
                print("Days    :", rental.days)
                print("Amount  :", rental.calculate_amount())
                print("Status  :", rental.status)
                print("--------------------")

                found = True

        if found == False:

            print("No Rentals Found")

    def get_rental_count(self):

        return len(self.rentals)

    def calculate_total_revenue(self):

        total_revenue = 0

        for rental in self.rentals:

            # Rental payment
            if rental.payment_status == "Paid":
                total_revenue += rental.calculate_amount()

            # Fine payment
            if rental.fine_payment_status == "Paid":
                total_revenue += rental.fine

        return total_revenue

    def financial_report(self):

        rental_income = 0
        fine_collected = 0

        for rental in self.rentals:

            # Rental money actually paid
            if rental.payment_status == "Paid":
                rental_income += rental.calculate_amount()

            # Fine money actually paid
            if rental.fine_payment_status == "Paid":
                fine_collected += rental.fine

        total_revenue = rental_income + fine_collected

        print("\n========== FINANCIAL REPORT ==========")

        print("Rental Income  :", rental_income)
        print("Fine Collected :", fine_collected)
        print("Total Revenue  :", total_revenue)

        print("======================================")

    def view_overdue_rentals(self, customer_id):

        found = False

        print("\n===== OVERDUE RENTALS =====")

        for rental in self.rentals:

            if (rental.customer.customer_id == customer_id
                    and rental.status == "Active"
                    and rental.check_overdue()):

                late_days = (
                    datetime.now().date()
                    - rental.return_date.date()
                ).days

                print("Vehicle ID      :", rental.vehicle.vehicle_id)
                print("Vehicle         :", rental.vehicle.name)
                print("Expected Return :", rental.return_date.strftime("%d-%m-%Y"))
                print("Late Days       :", late_days)
                print("Status          : OVERDUE")
                print("--------------------")

                found = True

        if not found:
            print("No Overdue Rentals")
        
customer_manager = CustomerManager()
manager = VehicleManager()
rental_manager = RentalManager()
manager = VehicleManager()
rental_manager.load_rentals(manager, customer_manager)



def admin_login():

    userName = input("Enter User Name:")
    password = input("Enter Password:")

    if userName == "sai" and password == "1234":
        print("Login Successful")
        return True
    else:
        print("Invalid Username or Password")
        return False

def admin_dashboard(manager, customer_manager, rental_manager):

    total_vehicles, available, rented = manager.get_vehicle_statistics()

    total_customers = customer_manager.get_customer_count()

    total_rentals = rental_manager.get_rental_count()

    total_revenue = rental_manager.calculate_total_revenue()

    print("\n========== ADMIN DASHBOARD ==========")

    print("Total Vehicles     :", total_vehicles)
    print("Available Vehicles :", available)
    print("Rented Vehicles    :", rented)
    print("Total Customers    :", total_customers)
    print("Total Rentals      :", total_rentals)
    print("Total Revenue      : ₹", total_revenue)

    print("=====================================")

def admin_menu():

    while True:

        print("\n===== ADMIN MENU =====")
        print("1. Add Vehicle")
        print("2. View Vehicles")
        print("3. Search Vehicle")
        print("4. Update Vehicle")
        print("5. Delete Vehicle")
        print("6. View Rentals")
        print("7. DashBoard")
        print("8. Finanacial Report")
        print("9. Logout")

        choice = int(input("Enter Your Choice: "))

        if choice == 1:

            print("\n===== ADD VEHICLE =====")
            print("1. Car")
            print("2. Bike")

            vehicle_type = int(input("Enter Vehicle Type: "))

            vehicle_id = int(input("Enter Vehicle ID: "))
            name = input("Enter Vehicle Name: ")
            price = float(input("Enter Price Per Day: "))

            if vehicle_type == 1:

                seats = int(input("Enter Number of Seats: "))

                vehicle = Car(
                    vehicle_id,
                    name,
                    price,
                    seats
                )

            elif vehicle_type == 2:

                engine_cc = int(input("Enter Engine CC: "))

                vehicle = Bike(
                    vehicle_id,
                    name,
                    price,
                    engine_cc
                )

            else:

                print("Invalid Vehicle Type")
                continue

            manager.add_vehicle(vehicle)
        elif choice == 2:

            manager.view_vehicles()

        elif choice == 3:

            vehicle_id = int(input("Enter Vehicle ID: "))

            vehicle = manager.search_vehicle(vehicle_id)

            if vehicle:
                vehicle.display()
            else:
                print("Vehicle Not Found")

        elif choice == 4:

            vehicle_id = int(input("Enter Vehicle ID: "))

            manager.update_vehicle(vehicle_id)

        elif choice == 5:

            vehicle_id = int(input("Enter Vehicle ID: "))

            manager.delete_vehicle(vehicle_id)

        elif choice == 6:

            rental_manager.view_all_rentals()

        elif choice == 7:

            admin_dashboard(
                manager,
                customer_manager,
                rental_manager
            )

        elif choice == 8:

             rental_manager.financial_report()
        
        elif choice == 9:

            print("Admin Logged Out")
            break

        else:

            print("Invalid Choice")

def customer_menu(customer):

    while True:

        print("\n===== CUSTOMER MENU =====")
        print("1. View Available Vehicles")
        print("2. Search Vehicle")
        print("3. Sort Vehicles By Price")
        print("4. Filter Vehicle By Type")
        print("5. Rent Vehicle")
        print("6. View My Rentals")
        print("7. View Overdue Rentals")
        print("8. Return Vehicle")
        print("9. Pay Fine")
        print("10. Logout")

        choice = int(input("Enter Your Choice: "))

        if choice == 1:

            manager.view_available_vehicles()

        elif choice == 2:

           manager.search_vehicles()

        elif choice == 3:

            manager.sort_vehicles_by_price()

        elif choice == 4:

            manager.filter_by_type()

        elif choice == 5:

            vehicle_id = int(input("Enter Vehicle ID: "))

            vehicle = manager.search_vehicle(vehicle_id)

            if vehicle is None:

                print("Vehicle Not Found")
                continue

            if vehicle.status != "Available":

                print("Vehicle is Not Available")
                continue

            days = int(input("Enter Number of Days: "))

            if days <= 0:

                print("Days must be greater than 0")
                continue

            rental = Rental(customer, vehicle, days)

            if rental.rent():

                rental_manager.add_rental(rental)

                rental.display_receipt()
        

        elif choice == 6:

            rental_manager.view_my_rentals(customer.customer_id)

        elif choice == 7:

            rental_manager.view_overdue_rentals(
                customer.customer_id
            )

        elif choice == 8:

            vehicle_id = int(input("Enter Vehicle ID to Return: "))

            rental = rental_manager.find_rental(
                customer.customer_id,
                vehicle_id
            )

            if rental:
                rental.return_vehicle()
            else:
                print("No Active Rental Found")

        elif choice == 9:

            found = False

            for rental in rental_manager.rentals:

                if rental.customer.customer_id == customer.customer_id:

                    if rental.fine > 0 and rental.fine_payment_status == "Unpaid":

                        rental.pay_fine()

                        found = True
                        break

            if not found:

                print("No Unpaid Fine Found")

        elif choice == 10:

            print("Customer Logged Out")
            break

        else:

            print("Invalid Choice")

while True:

    print("\n===== VEHICLE RENTAL SYSTEM =====")
    print("1. Admin")
    print("2. Customer")
    print("3. Customer Registration")
    print("4. Exit")

    choice = int(input("Enter Your Choice: "))

    if choice == 1:

        if admin_login():
            admin_menu()

    elif choice == 2:

        customer = customer_manager.customer_login()

        if customer:

            customer_menu(customer)

    elif choice == 3:
        customer_manager.register_customer()

    elif choice == 4:

        print("Thank You for Using Vehicle Rental System")
        break

    else:

        print("Invalid Choice")

"""
                
v1 = Bike(101,"GT650",1500, 650)
v2 = Car(102, "Swift",1500, 5)

manager = VehicleManager()
manager.add_vehicle(v1)
manager.add_vehicle(v2)
manager.view_vehicles()
customer1 = Customer(1, "Sai", "9876543210")
customer2 = Customer(2, "Ganesh", "9123456789")
customer_manager = CustomerManager()
customer_manager.add_customer(customer1)
customer_manager.add_customer(customer2)
r1 = Rental(customer1, v1, 3)
renatl_manager = RentalManager()
renatl_manager.add_rental(r1)
renatl_manager.view_rentals()

"""