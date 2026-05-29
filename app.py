import sqlite3
import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public', static_url_path='')

DB_PATH = os.path.join(os.path.dirname(__file__), 'fooddelivery.db')
ADMIN_PASS = 'admin123'

# ─── DB helpers ──────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def query(sql, params=()):
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

def execute(sql, params=()):
    with get_db() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid

# ─── DB init + seed ──────────────────────────────────────────────────────────

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS Customer (
          CustomerID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR(50) NOT NULL,
          Email VARCHAR(100) UNIQUE, Phone VARCHAR(15), Address VARCHAR(150));
        CREATE TABLE IF NOT EXISTS Address (
          AddressID INTEGER PRIMARY KEY AUTOINCREMENT, CustomerID INT,
          City VARCHAR(50) NOT NULL, Street VARCHAR(100),
          FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID));
        CREATE TABLE IF NOT EXISTS Restaurant (
          RestaurantID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR(100) NOT NULL, Location VARCHAR(100));
        CREATE TABLE IF NOT EXISTS Category (
          CategoryID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR(50) NOT NULL);
        CREATE TABLE IF NOT EXISTS FoodItem (
          FoodItemID INTEGER PRIMARY KEY AUTOINCREMENT, RestaurantID INT, CategoryID INT,
          Name VARCHAR(100) NOT NULL, Price DECIMAL(10,2) NOT NULL,
          FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID),
          FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID));
        CREATE TABLE IF NOT EXISTS Cart (
          CartID INTEGER PRIMARY KEY AUTOINCREMENT, CustomerID INT,
          FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID));
        CREATE TABLE IF NOT EXISTS CartItem (
          CartItemID INTEGER PRIMARY KEY AUTOINCREMENT, CartID INT, FoodItemID INT, Quantity INT NOT NULL,
          FOREIGN KEY (CartID) REFERENCES Cart(CartID),
          FOREIGN KEY (FoodItemID) REFERENCES FoodItem(FoodItemID));
        CREATE TABLE IF NOT EXISTS Orders (
          OrderID INTEGER PRIMARY KEY AUTOINCREMENT, CustomerID INT, OrderDate DATE NOT NULL,
          TotalAmount DECIMAL(10,2), FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID));
        CREATE TABLE IF NOT EXISTS OrderItem (
          OrderItemID INTEGER PRIMARY KEY AUTOINCREMENT, OrderID INT, FoodItemID INT, Quantity INT NOT NULL,
          FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
          FOREIGN KEY (FoodItemID) REFERENCES FoodItem(FoodItemID));
        CREATE TABLE IF NOT EXISTS PaymentMethod (
          MethodID INTEGER PRIMARY KEY AUTOINCREMENT, MethodName VARCHAR(50) NOT NULL);
        CREATE TABLE IF NOT EXISTS Payment (
          PaymentID INTEGER PRIMARY KEY AUTOINCREMENT, OrderID INT, MethodID INT,
          PaymentStatus VARCHAR(50), Amount DECIMAL(10,2),
          FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
          FOREIGN KEY (MethodID) REFERENCES PaymentMethod(MethodID));
        CREATE TABLE IF NOT EXISTS DeliveryDriver (
          DriverID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR(50) NOT NULL, Phone VARCHAR(15));
        CREATE TABLE IF NOT EXISTS Delivery (
          DeliveryID INTEGER PRIMARY KEY AUTOINCREMENT, OrderID INT, DriverID INT,
          DeliveryStatus VARCHAR(50), DeliveryTime TIME,
          FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
          FOREIGN KEY (DriverID) REFERENCES DeliveryDriver(DriverID));
        CREATE TABLE IF NOT EXISTS Review (
          ReviewID INTEGER PRIMARY KEY AUTOINCREMENT, CustomerID INT, RestaurantID INT,
          Rating INT, Comment VARCHAR(255),
          FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
          FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID));
        CREATE TABLE IF NOT EXISTS Admin (
          AdminID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR(50) NOT NULL, Email VARCHAR(100) UNIQUE);
    ''')
    conn.commit()
    conn.close()

def seed_db():
    with get_db() as conn:
        if conn.execute('SELECT COUNT(*) FROM Customer').fetchone()[0] > 0:
            return
        conn.executescript('''
            INSERT INTO Customer VALUES (1,'Ali Khan','ali@gmail.com','03001111111','Lahore');
            INSERT INTO Customer VALUES (2,'Sara Malik','sara@gmail.com','03002222222','Karachi');
            INSERT INTO Customer VALUES (3,'Usman Ahmed','usman@gmail.com','03003333333','Islamabad');
            INSERT INTO Customer VALUES (4,'Fatima Noor','fatima@gmail.com','03004444444','Lahore');
            INSERT INTO Customer VALUES (5,'Hassan Ali','hassan@gmail.com','03005555555','Karachi');
            INSERT INTO Customer VALUES (6,'Ayesha Iqbal','ayesha@gmail.com','03006666666','Multan');
            INSERT INTO Customer VALUES (7,'Bilal Sheikh','bilal@gmail.com','03007777777','Faisalabad');
            INSERT INTO Customer VALUES (8,'Zara Khan','zara@gmail.com','03008888888','Lahore');
            INSERT INTO Customer VALUES (9,'Omar Farooq','omar@gmail.com','03009999999','Islamabad');
            INSERT INTO Customer VALUES (10,'Hira Baig','hira@gmail.com','03010000000','Karachi');
            INSERT INTO Customer VALUES (11,'Kamran Shah','kamran@gmail.com','03011111111','Lahore');
            INSERT INTO Customer VALUES (12,'Nadia Hussain','nadia@gmail.com','03012222222','Multan');
            INSERT INTO Customer VALUES (13,'Imran Qureshi','imran@gmail.com','03013333333','Peshawar');
            INSERT INTO Customer VALUES (14,'Sana Javed','sana@gmail.com','03014444444','Lahore');
            INSERT INTO Customer VALUES (15,'Rehan Malik','rehan@gmail.com','03015555555','Karachi');
            INSERT INTO Customer VALUES (16,'Hina Aslam','hina@gmail.com','03016666666','Islamabad');
            INSERT INTO Customer VALUES (17,'Daniyal Ahmed','daniyal@gmail.com','03017777777','Multan');
            INSERT INTO Customer VALUES (18,'Ammar Sohail','ammar@gmail.com','03018888888','Faisalabad');
            INSERT INTO Customer VALUES (19,'Mehwish Tariq','mehwish@gmail.com','03019999999','Lahore');
            INSERT INTO Customer VALUES (20,'Usama Khan','usama@gmail.com','03020000001','Karachi');
            INSERT INTO Customer VALUES (21,'Mariam Shah','mariam@gmail.com','03021111111','Islamabad');
            INSERT INTO Customer VALUES (22,'Saad Raza','saad@gmail.com','03022222222','Peshawar');
            INSERT INTO Customer VALUES (23,'Noor Fatima','noor@gmail.com','03023333333','Multan');
            INSERT INTO Customer VALUES (24,'Zain Ali','zain@gmail.com','03024444444','Lahore');
            INSERT INTO Customer VALUES (25,'Areeba Khan','areeba@gmail.com','03025555555','Karachi');
            INSERT INTO Customer VALUES (26,'Farhan Siddiqui','farhan@gmail.com','03026666666','Islamabad');
            INSERT INTO Customer VALUES (27,'Hassan Raza','hassanr@gmail.com','03027777777','Faisalabad');
            INSERT INTO Customer VALUES (28,'Iqra Noor','iqra@gmail.com','03028888888','Lahore');
            INSERT INTO Customer VALUES (29,'Shayan Ali','shayan@gmail.com','03029999999','Karachi');
            INSERT INTO Customer VALUES (30,'Aiza Malik','aiza@gmail.com','03030000001','Multan');

            INSERT INTO Restaurant VALUES (1,'Bundu Khan','Lahore');
            INSERT INTO Restaurant VALUES (2,'Bar BQ Tonight','Karachi');
            INSERT INTO Restaurant VALUES (3,'Monal','Islamabad');
            INSERT INTO Restaurant VALUES (4,'Salt n Pepper','Lahore');
            INSERT INTO Restaurant VALUES (5,'Student Biryani','Karachi');
            INSERT INTO Restaurant VALUES (6,'Charsi Tikka','Peshawar');
            INSERT INTO Restaurant VALUES (7,'Usmania','Faisalabad');
            INSERT INTO Restaurant VALUES (8,'Lahore Chargha','Lahore');
            INSERT INTO Restaurant VALUES (9,'Kabul Restaurant','Islamabad');
            INSERT INTO Restaurant VALUES (10,'Kolachi','Karachi');
            INSERT INTO Restaurant VALUES (11,'Haveli','Lahore');
            INSERT INTO Restaurant VALUES (12,'Savour Foods','Rawalpindi');
            INSERT INTO Restaurant VALUES (13,'Al Maida','Lahore');
            INSERT INTO Restaurant VALUES (14,'Savory Hub','Karachi');
            INSERT INTO Restaurant VALUES (15,'Food Street Cafe','Lahore');
            INSERT INTO Restaurant VALUES (16,'Spice Garden','Islamabad');
            INSERT INTO Restaurant VALUES (17,'Royal Tandoor','Faisalabad');
            INSERT INTO Restaurant VALUES (18,'Desi Delight','Multan');
            INSERT INTO Restaurant VALUES (19,'Hot N Spicy','Peshawar');
            INSERT INTO Restaurant VALUES (20,'Urban Grill','Lahore');
            INSERT INTO Restaurant VALUES (21,'Ocean Breeze','Karachi');
            INSERT INTO Restaurant VALUES (22,'Karachi Kitchen','Karachi');
            INSERT INTO Restaurant VALUES (23,'Punjab Dhaba','Lahore');
            INSERT INTO Restaurant VALUES (24,'Taste of Lahore','Lahore');
            INSERT INTO Restaurant VALUES (25,'Zaiqa Restaurant','Islamabad');
            INSERT INTO Restaurant VALUES (26,'BBQ House','Rawalpindi');
            INSERT INTO Restaurant VALUES (27,'Food Fiesta','Faisalabad');
            INSERT INTO Restaurant VALUES (28,'Hungry Point','Multan');
            INSERT INTO Restaurant VALUES (29,'Tandoori Hut','Peshawar');
            INSERT INTO Restaurant VALUES (30,'Cafe Fusion','Lahore');

            INSERT INTO Category VALUES (1,'Fast Food');
            INSERT INTO Category VALUES (2,'Desi');
            INSERT INTO Category VALUES (3,'BBQ');
            INSERT INTO Category VALUES (4,'Beverages');
            INSERT INTO Category VALUES (5,'Desserts');
            INSERT INTO Category VALUES (6,'Chinese');
            INSERT INTO Category VALUES (7,'Italian');
            INSERT INTO Category VALUES (8,'Continental');
            INSERT INTO Category VALUES (9,'Sea Food');
            INSERT INTO Category VALUES (10,'Snacks');
            INSERT INTO Category VALUES (11,'Breakfast');
            INSERT INTO Category VALUES (12,'Rice Items');
            INSERT INTO Category VALUES (13,'Soups');
            INSERT INTO Category VALUES (14,'Vegetarian');
            INSERT INTO Category VALUES (15,'Grill Items');

            INSERT INTO FoodItem VALUES (1,1,1,'Burger',350.00);
            INSERT INTO FoodItem VALUES (2,2,2,'Biryani',450.00);
            INSERT INTO FoodItem VALUES (3,3,3,'BBQ Platter',1200.00);
            INSERT INTO FoodItem VALUES (4,4,1,'Pizza',800.00);
            INSERT INTO FoodItem VALUES (5,5,2,'Karahi',950.00);
            INSERT INTO FoodItem VALUES (6,6,3,'Tikka',600.00);
            INSERT INTO FoodItem VALUES (7,7,2,'Nihari',400.00);
            INSERT INTO FoodItem VALUES (8,8,1,'Chargha',750.00);
            INSERT INTO FoodItem VALUES (9,9,3,'Seekh Kabab',500.00);
            INSERT INTO FoodItem VALUES (10,10,2,'Prawn Karahi',1100.00);
            INSERT INTO FoodItem VALUES (11,11,1,'Shawarma',250.00);
            INSERT INTO FoodItem VALUES (12,12,2,'Murgh Pulao',550.00);
            INSERT INTO FoodItem VALUES (13,1,1,'Zinger Burger',420.00);
            INSERT INTO FoodItem VALUES (14,2,2,'Chicken Biryani',400.00);
            INSERT INTO FoodItem VALUES (15,3,3,'Malai Boti',650.00);
            INSERT INTO FoodItem VALUES (16,4,1,'Margherita Pizza',750.00);
            INSERT INTO FoodItem VALUES (17,5,2,'Chicken Karahi (Full)',1400.00);
            INSERT INTO FoodItem VALUES (18,6,3,'Mutton Tikka',900.00);
            INSERT INTO FoodItem VALUES (19,7,2,'Haleem',380.00);
            INSERT INTO FoodItem VALUES (20,8,1,'Chicken Chargha',780.00);
            INSERT INTO FoodItem VALUES (21,9,3,'Chapli Kabab',550.00);
            INSERT INTO FoodItem VALUES (22,10,9,'Grilled Fish',1300.00);
            INSERT INTO FoodItem VALUES (23,11,1,'Chicken Shawarma Platter',600.00);
            INSERT INTO FoodItem VALUES (24,12,2,'Beef Pulao',650.00);
            INSERT INTO FoodItem VALUES (25,13,2,'Mutton Karahi',1600.00);
            INSERT INTO FoodItem VALUES (26,14,3,'Lamb Chops',1100.00);
            INSERT INTO FoodItem VALUES (27,15,2,'Chicken Handi',950.00);
            INSERT INTO FoodItem VALUES (28,16,2,'Dal Makhani',450.00);
            INSERT INTO FoodItem VALUES (29,17,1,'Pepperoni Pizza',850.00);
            INSERT INTO FoodItem VALUES (30,18,8,'Fresh Lime Soda',150.00);

            INSERT INTO PaymentMethod VALUES (1,'Cash');
            INSERT INTO PaymentMethod VALUES (2,'JazzCash');
            INSERT INTO PaymentMethod VALUES (3,'EasyPaisa');
            INSERT INTO PaymentMethod VALUES (4,'Credit Card');
            INSERT INTO PaymentMethod VALUES (5,'Debit Card');
            INSERT INTO PaymentMethod VALUES (6,'Bank Transfer');
            INSERT INTO PaymentMethod VALUES (7,'Google Pay');
            INSERT INTO PaymentMethod VALUES (8,'Apple Pay');
            INSERT INTO PaymentMethod VALUES (9,'PayPal');
            INSERT INTO PaymentMethod VALUES (10,'Cash on Delivery');
            INSERT INTO PaymentMethod VALUES (11,'UPaisa');
            INSERT INTO PaymentMethod VALUES (12,'SadaPay');
            INSERT INTO PaymentMethod VALUES (13,'NayaPay');
            INSERT INTO PaymentMethod VALUES (14,'Stripe');
            INSERT INTO PaymentMethod VALUES (15,'Online Banking');

            INSERT INTO DeliveryDriver VALUES (1,'Arif Hussain','03101111111');
            INSERT INTO DeliveryDriver VALUES (2,'Tariq Mehmood','03102222222');
            INSERT INTO DeliveryDriver VALUES (3,'Sajid Ali','03103333333');
            INSERT INTO DeliveryDriver VALUES (4,'Imran Butt','03104444444');
            INSERT INTO DeliveryDriver VALUES (5,'Naveed Iqbal','03105555555');
            INSERT INTO DeliveryDriver VALUES (6,'Kashif Raza','03106666666');
            INSERT INTO DeliveryDriver VALUES (7,'Waseem Shah','03107777777');
            INSERT INTO DeliveryDriver VALUES (8,'Adeel Awan','03108888888');
            INSERT INTO DeliveryDriver VALUES (9,'Rizwan Khan','03109999999');
            INSERT INTO DeliveryDriver VALUES (10,'Tanveer Ahmad','03110000000');
            INSERT INTO DeliveryDriver VALUES (11,'Faisal Noor','03111111111');
            INSERT INTO DeliveryDriver VALUES (12,'Zeeshan Qureshi','03112222222');
            INSERT INTO DeliveryDriver VALUES (13,'Nasir Mahmood','03113334444');
            INSERT INTO DeliveryDriver VALUES (14,'Javed Iqbal','03114445555');
            INSERT INTO DeliveryDriver VALUES (15,'Shahid Afridi','03115556666');
            INSERT INTO DeliveryDriver VALUES (16,'Mohsin Khan','03116667777');
            INSERT INTO DeliveryDriver VALUES (17,'Yasir Arafat','03117778888');
            INSERT INTO DeliveryDriver VALUES (18,'Abdul Razzaq','03118889999');
            INSERT INTO DeliveryDriver VALUES (19,'Shoaib Malik','03119990000');
            INSERT INTO DeliveryDriver VALUES (20,'Kamran Akmal','03120001111');
            INSERT INTO DeliveryDriver VALUES (21,'Umar Gul','03121112222');
            INSERT INTO DeliveryDriver VALUES (22,'Mohammad Amir','03122223333');
            INSERT INTO DeliveryDriver VALUES (23,'Wahab Riaz','03123334444');
            INSERT INTO DeliveryDriver VALUES (24,'Hasan Ali','03124445555');
            INSERT INTO DeliveryDriver VALUES (25,'Shaheen Afridi','03125556666');
            INSERT INTO DeliveryDriver VALUES (26,'Haris Rauf','03126667777');
            INSERT INTO DeliveryDriver VALUES (27,'Naseem Shah','03127778888');
            INSERT INTO DeliveryDriver VALUES (28,'Shadab Khan','03128889999');
            INSERT INTO DeliveryDriver VALUES (29,'Imad Wasim','03129990000');
            INSERT INTO DeliveryDriver VALUES (30,'Fakhar Zaman','03130001111');

            INSERT INTO Admin VALUES (1,'Muhammad Hafeez','hafeez@university.edu.pk');
            INSERT INTO Admin VALUES (2,'System Admin','admin@fooddelivery.com');
            INSERT INTO Admin VALUES (3,'Ali Raza','ali.raza@fooddelivery.com');
            INSERT INTO Admin VALUES (4,'Sana Ahmed','sana.ahmed@university.edu.pk');
            INSERT INTO Admin VALUES (5,'Usman Chaudhry','usman.ch@fooddelivery.com');

            INSERT INTO Address VALUES (1,1,'Lahore','Mall Road');
            INSERT INTO Address VALUES (2,2,'Karachi','Clifton');
            INSERT INTO Address VALUES (3,3,'Islamabad','F-6');
            INSERT INTO Address VALUES (4,4,'Lahore','DHA Phase 5');
            INSERT INTO Address VALUES (5,5,'Karachi','Gulshan');
            INSERT INTO Address VALUES (6,6,'Multan','Gulgasht');
            INSERT INTO Address VALUES (7,7,'Faisalabad','Peoples Colony');
            INSERT INTO Address VALUES (8,8,'Lahore','Johar Town');
            INSERT INTO Address VALUES (9,9,'Islamabad','G-11');
            INSERT INTO Address VALUES (10,10,'Karachi','Defence');

            INSERT INTO Orders VALUES (1,1,'2026-01-01',1000.00);
            INSERT INTO Orders VALUES (2,2,'2026-01-02',1200.00);
            INSERT INTO Orders VALUES (3,3,'2026-01-03',900.00);
            INSERT INTO Orders VALUES (4,4,'2026-01-04',1500.00);
            INSERT INTO Orders VALUES (5,5,'2026-01-05',800.00);
            INSERT INTO Orders VALUES (6,6,'2026-01-06',1100.00);
            INSERT INTO Orders VALUES (7,7,'2026-01-07',1300.00);
            INSERT INTO Orders VALUES (8,8,'2026-01-08',700.00);
            INSERT INTO Orders VALUES (9,9,'2026-01-09',1400.00);
            INSERT INTO Orders VALUES (10,10,'2026-01-10',1000.00);
            INSERT INTO Orders VALUES (11,11,'2026-01-11',900.00);
            INSERT INTO Orders VALUES (12,12,'2026-01-12',1600.00);
            INSERT INTO Orders VALUES (13,13,'2026-03-15',890.00);
            INSERT INTO Orders VALUES (14,14,'2026-03-16',1200.00);
            INSERT INTO Orders VALUES (15,15,'2026-03-17',650.00);
            INSERT INTO Orders VALUES (16,16,'2026-03-18',1500.00);
            INSERT INTO Orders VALUES (17,17,'2026-03-19',950.00);
            INSERT INTO Orders VALUES (18,18,'2026-03-20',1100.00);
            INSERT INTO Orders VALUES (19,19,'2026-03-21',780.00);
            INSERT INTO Orders VALUES (20,20,'2026-03-22',1350.00);
            INSERT INTO Orders VALUES (21,21,'2026-03-23',990.00);
            INSERT INTO Orders VALUES (22,22,'2026-03-24',1600.00);
            INSERT INTO Orders VALUES (23,23,'2026-03-25',420.00);
            INSERT INTO Orders VALUES (24,24,'2026-03-26',1120.00);
            INSERT INTO Orders VALUES (25,25,'2026-03-27',880.00);
            INSERT INTO Orders VALUES (26,1,'2026-03-28',1300.00);
            INSERT INTO Orders VALUES (27,2,'2026-03-29',550.00);
            INSERT INTO Orders VALUES (28,3,'2026-03-30',1450.00);
            INSERT INTO Orders VALUES (29,4,'2026-03-31',720.00);
            INSERT INTO Orders VALUES (30,5,'2026-04-01',1180.00);

            INSERT INTO Cart VALUES (1,1);
            INSERT INTO Cart VALUES (2,2);
            INSERT INTO Cart VALUES (3,3);
            INSERT INTO Cart VALUES (4,4);
            INSERT INTO Cart VALUES (5,5);
            INSERT INTO Cart VALUES (6,6);
            INSERT INTO Cart VALUES (7,7);
            INSERT INTO Cart VALUES (8,8);
            INSERT INTO Cart VALUES (9,9);
            INSERT INTO Cart VALUES (10,10);

            INSERT INTO CartItem VALUES (1,1,1,2);
            INSERT INTO CartItem VALUES (2,2,2,1);
            INSERT INTO CartItem VALUES (3,3,3,1);
            INSERT INTO CartItem VALUES (4,4,4,2);
            INSERT INTO CartItem VALUES (5,5,5,1);
            INSERT INTO CartItem VALUES (6,6,6,3);
            INSERT INTO CartItem VALUES (7,7,7,2);
            INSERT INTO CartItem VALUES (8,8,8,1);
            INSERT INTO CartItem VALUES (9,9,9,2);
            INSERT INTO CartItem VALUES (10,10,10,1);

            INSERT INTO OrderItem VALUES (1,1,1,2);
            INSERT INTO OrderItem VALUES (2,2,2,1);
            INSERT INTO OrderItem VALUES (3,3,3,1);
            INSERT INTO OrderItem VALUES (4,4,4,2);
            INSERT INTO OrderItem VALUES (5,5,5,1);
            INSERT INTO OrderItem VALUES (6,6,6,2);
            INSERT INTO OrderItem VALUES (7,7,7,1);
            INSERT INTO OrderItem VALUES (8,8,8,3);
            INSERT INTO OrderItem VALUES (9,9,9,2);
            INSERT INTO OrderItem VALUES (10,10,10,1);
            INSERT INTO OrderItem VALUES (11,11,11,2);
            INSERT INTO OrderItem VALUES (12,12,12,1);
            INSERT INTO OrderItem VALUES (13,13,13,1);
            INSERT INTO OrderItem VALUES (14,14,14,1);
            INSERT INTO OrderItem VALUES (15,15,15,2);
            INSERT INTO OrderItem VALUES (16,16,16,1);
            INSERT INTO OrderItem VALUES (17,17,17,2);
            INSERT INTO OrderItem VALUES (18,18,18,1);
            INSERT INTO OrderItem VALUES (19,19,19,2);
            INSERT INTO OrderItem VALUES (20,20,20,1);
            INSERT INTO OrderItem VALUES (21,21,21,3);
            INSERT INTO OrderItem VALUES (22,22,22,1);
            INSERT INTO OrderItem VALUES (23,23,23,2);
            INSERT INTO OrderItem VALUES (24,24,24,1);
            INSERT INTO OrderItem VALUES (25,25,25,2);
            INSERT INTO OrderItem VALUES (26,26,26,1);
            INSERT INTO OrderItem VALUES (27,27,27,2);
            INSERT INTO OrderItem VALUES (28,28,28,1);
            INSERT INTO OrderItem VALUES (29,29,29,2);
            INSERT INTO OrderItem VALUES (30,30,30,1);

            INSERT INTO Payment VALUES (1,1,1,'Paid',1000.00);
            INSERT INTO Payment VALUES (2,2,2,'Paid',1200.00);
            INSERT INTO Payment VALUES (3,3,3,'Pending',900.00);
            INSERT INTO Payment VALUES (4,4,4,'Paid',1500.00);
            INSERT INTO Payment VALUES (5,5,5,'Paid',800.00);
            INSERT INTO Payment VALUES (6,6,6,'Paid',1100.00);
            INSERT INTO Payment VALUES (7,7,1,'Pending',1300.00);
            INSERT INTO Payment VALUES (8,8,2,'Paid',700.00);
            INSERT INTO Payment VALUES (9,9,3,'Paid',1400.00);
            INSERT INTO Payment VALUES (10,10,4,'Paid',1000.00);
            INSERT INTO Payment VALUES (11,11,5,'Pending',900.00);
            INSERT INTO Payment VALUES (12,12,6,'Paid',1600.00);
            INSERT INTO Payment VALUES (13,13,7,'Paid',890.00);
            INSERT INTO Payment VALUES (14,14,8,'Paid',1200.00);
            INSERT INTO Payment VALUES (15,15,15,'Pending',650.00);
            INSERT INTO Payment VALUES (16,16,9,'Paid',1500.00);
            INSERT INTO Payment VALUES (17,17,10,'Paid',950.00);
            INSERT INTO Payment VALUES (18,18,11,'Paid',1100.00);
            INSERT INTO Payment VALUES (19,19,12,'Pending',780.00);
            INSERT INTO Payment VALUES (20,20,13,'Paid',1350.00);
            INSERT INTO Payment VALUES (21,21,14,'Paid',990.00);
            INSERT INTO Payment VALUES (22,22,1,'Paid',1600.00);
            INSERT INTO Payment VALUES (23,23,2,'Paid',420.00);
            INSERT INTO Payment VALUES (24,24,3,'Pending',1120.00);
            INSERT INTO Payment VALUES (25,25,4,'Paid',880.00);
            INSERT INTO Payment VALUES (26,26,5,'Paid',1300.00);
            INSERT INTO Payment VALUES (27,27,6,'Pending',550.00);
            INSERT INTO Payment VALUES (28,28,7,'Paid',1450.00);
            INSERT INTO Payment VALUES (29,29,8,'Paid',720.00);
            INSERT INTO Payment VALUES (30,30,15,'Paid',1180.00);

            INSERT INTO Delivery VALUES (1,1,1,'Delivered','12:00:00');
            INSERT INTO Delivery VALUES (2,2,2,'Pending','13:00:00');
            INSERT INTO Delivery VALUES (3,3,3,'Delivered','14:00:00');
            INSERT INTO Delivery VALUES (4,4,4,'Cancelled','15:00:00');
            INSERT INTO Delivery VALUES (5,5,5,'Delivered','16:00:00');
            INSERT INTO Delivery VALUES (6,6,6,'Pending','17:00:00');
            INSERT INTO Delivery VALUES (7,7,7,'Delivered','18:00:00');
            INSERT INTO Delivery VALUES (8,8,8,'Delivered','19:00:00');
            INSERT INTO Delivery VALUES (9,9,9,'Pending','20:00:00');
            INSERT INTO Delivery VALUES (10,10,10,'Delivered','21:00:00');
            INSERT INTO Delivery VALUES (11,11,11,'Pending','22:00:00');
            INSERT INTO Delivery VALUES (12,12,12,'Delivered','23:00:00');
            INSERT INTO Delivery VALUES (13,13,13,'Delivered','12:30:00');
            INSERT INTO Delivery VALUES (14,14,14,'Pending','13:15:00');
            INSERT INTO Delivery VALUES (15,15,15,'Delivered','14:45:00');
            INSERT INTO Delivery VALUES (16,16,16,'Delivered','15:20:00');
            INSERT INTO Delivery VALUES (17,17,17,'Cancelled','16:00:00');
            INSERT INTO Delivery VALUES (18,18,18,'Delivered','17:10:00');
            INSERT INTO Delivery VALUES (19,19,19,'Pending','18:30:00');
            INSERT INTO Delivery VALUES (20,20,20,'Delivered','19:05:00');
            INSERT INTO Delivery VALUES (21,21,21,'Delivered','20:15:00');
            INSERT INTO Delivery VALUES (22,22,22,'Pending','21:25:00');
            INSERT INTO Delivery VALUES (23,23,23,'Delivered','22:00:00');
            INSERT INTO Delivery VALUES (24,24,24,'Delivered','23:40:00');
            INSERT INTO Delivery VALUES (25,25,25,'Cancelled','09:15:00');
            INSERT INTO Delivery VALUES (26,26,1,'Delivered','10:30:00');
            INSERT INTO Delivery VALUES (27,27,2,'Pending','11:45:00');
            INSERT INTO Delivery VALUES (28,28,3,'Delivered','12:20:00');
            INSERT INTO Delivery VALUES (29,29,4,'Delivered','13:55:00');
            INSERT INTO Delivery VALUES (30,30,5,'Pending','14:40:00');

            INSERT INTO Review VALUES (1,1,1,5,'Excellent food and fast delivery!');
            INSERT INTO Review VALUES (2,2,2,4,'Good taste, will order again.');
            INSERT INTO Review VALUES (3,3,3,3,'Average experience.');
            INSERT INTO Review VALUES (4,4,4,5,'Best restaurant in Lahore!');
            INSERT INTO Review VALUES (5,5,5,2,'Food was cold on arrival.');
            INSERT INTO Review VALUES (6,6,6,4,'Nice BBQ, loved the tikka.');
            INSERT INTO Review VALUES (7,7,7,5,'Perfect biryani!');
            INSERT INTO Review VALUES (8,8,8,3,'Okay, nothing special.');
            INSERT INTO Review VALUES (9,9,9,4,'Good kababs.');
            INSERT INTO Review VALUES (10,10,10,5,'Excellent prawn karahi.');
            INSERT INTO Review VALUES (11,11,11,3,'Average quality.');
            INSERT INTO Review VALUES (12,12,12,4,'Nice pulao, good service.');
            INSERT INTO Review VALUES (13,13,13,5,'Amazing zinger burger!');
            INSERT INTO Review VALUES (14,14,14,4,'Biryani was good but could be spicier.');
            INSERT INTO Review VALUES (15,15,15,3,'Decent food, service slow.');
            INSERT INTO Review VALUES (16,16,16,5,'Best pizza in town!');
            INSERT INTO Review VALUES (17,17,17,2,'Karahi was too oily.');
            INSERT INTO Review VALUES (18,18,18,4,'Tikka was well cooked.');
            INSERT INTO Review VALUES (19,19,19,3,'Average experience.');
            INSERT INTO Review VALUES (20,20,20,5,'Chargha was delicious!');
            INSERT INTO Review VALUES (21,21,21,4,'Chapli kabab was tasty.');
            INSERT INTO Review VALUES (22,22,22,5,'Fresh fish, highly recommend.');
            INSERT INTO Review VALUES (23,23,23,4,'Shawarma platter was filling.');
            INSERT INTO Review VALUES (24,24,24,3,'Beef pulao was okay.');
            INSERT INTO Review VALUES (25,25,25,5,'Mutton karahi was excellent!');
            INSERT INTO Review VALUES (26,26,1,4,'Fast delivery and hot food.');
            INSERT INTO Review VALUES (27,27,2,5,'Best biryani in Karachi!');
            INSERT INTO Review VALUES (28,28,3,3,'Overpriced BBQ.');
            INSERT INTO Review VALUES (29,29,4,5,'Salt n Pepper never disappoints.');
            INSERT INTO Review VALUES (30,30,5,2,'Student Biryani quality dropped.');
        ''')
        conn.commit()

init_db()
seed_db()

# ─── Public dropdown APIs ─────────────────────────────────────────────────────

@app.route('/api/restaurants')
def get_restaurants():
    return jsonify(query('SELECT RestaurantID, Name FROM Restaurant ORDER BY Name'))

@app.route('/api/categories')
def get_categories():
    return jsonify(query('SELECT CategoryID, Name FROM Category ORDER BY Name'))

@app.route('/api/customers')
def get_customers():
    return jsonify(query('SELECT CustomerID, Name FROM Customer ORDER BY Name'))

@app.route('/api/fooditems')
def get_fooditems():
    return jsonify(query('''SELECT f.FoodItemID, f.Name, f.Price, r.Name AS Restaurant
        FROM FoodItem f JOIN Restaurant r ON f.RestaurantID = r.RestaurantID ORDER BY f.Name'''))

@app.route('/api/payment-methods')
def get_payment_methods():
    return jsonify(query('SELECT MethodID, MethodName FROM PaymentMethod ORDER BY MethodName'))

@app.route('/api/drivers')
def get_drivers():
    return jsonify(query('SELECT DriverID, Name FROM DeliveryDriver ORDER BY Name'))

@app.route('/api/orders')
def get_orders():
    return jsonify(query('SELECT OrderID, CustomerID, TotalAmount FROM Orders ORDER BY OrderID DESC'))

# ─── Public submit APIs ───────────────────────────────────────────────────────

@app.route('/api/customers', methods=['POST'])
def add_customer():
    d = request.get_json()
    if not d.get('Name'):
        return jsonify({'error': 'Name is required'}), 400
    try:
        rid = execute('INSERT INTO Customer (Name,Email,Phone,Address) VALUES (?,?,?,?)',
                      (d['Name'], d.get('Email'), d.get('Phone'), d.get('Address')))
        return jsonify({'success': True, 'id': rid})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/restaurants', methods=['POST'])
def add_restaurant():
    d = request.get_json()
    if not d.get('Name'):
        return jsonify({'error': 'Name is required'}), 400
    try:
        rid = execute('INSERT INTO Restaurant (Name,Location) VALUES (?,?)', (d['Name'], d.get('Location')))
        return jsonify({'success': True, 'id': rid})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/fooditems', methods=['POST'])
def add_fooditem():
    d = request.get_json()
    if not d.get('Name') or not d.get('Price'):
        return jsonify({'error': 'Name and Price are required'}), 400
    try:
        rid = execute('INSERT INTO FoodItem (RestaurantID,CategoryID,Name,Price) VALUES (?,?,?,?)',
                      (d.get('RestaurantID'), d.get('CategoryID'), d['Name'], d['Price']))
        return jsonify({'success': True, 'id': rid})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders', methods=['POST'])
def add_order():
    d = request.get_json()
    if not d.get('CustomerID') or not d.get('OrderDate'):
        return jsonify({'error': 'Customer and Date are required'}), 400
    try:
        conn = get_db()
        cur = conn.execute('INSERT INTO Orders (CustomerID,OrderDate,TotalAmount) VALUES (?,?,?)',
                           (d['CustomerID'], d['OrderDate'], d.get('TotalAmount', 0)))
        order_id = cur.lastrowid
        if d.get('FoodItemID') and d.get('Quantity'):
            conn.execute('INSERT INTO OrderItem (OrderID,FoodItemID,Quantity) VALUES (?,?,?)',
                         (order_id, d['FoodItemID'], d['Quantity']))
        if d.get('MethodID'):
            conn.execute('INSERT INTO Payment (OrderID,MethodID,PaymentStatus,Amount) VALUES (?,?,?,?)',
                         (order_id, d['MethodID'], 'Pending', d.get('TotalAmount', 0)))
        if d.get('DriverID'):
            conn.execute('INSERT INTO Delivery (OrderID,DriverID,DeliveryStatus) VALUES (?,?,?)',
                         (order_id, d['DriverID'], 'Pending'))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': order_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/reviews', methods=['POST'])
def add_review():
    d = request.get_json()
    if not d.get('CustomerID') or not d.get('RestaurantID') or not d.get('Rating'):
        return jsonify({'error': 'Customer, Restaurant, and Rating are required'}), 400
    try:
        rid = execute('INSERT INTO Review (CustomerID,RestaurantID,Rating,Comment) VALUES (?,?,?,?)',
                      (d['CustomerID'], d['RestaurantID'], d['Rating'], d.get('Comment')))
        return jsonify({'success': True, 'id': rid})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/drivers', methods=['POST'])
def add_driver():
    d = request.get_json()
    if not d.get('Name'):
        return jsonify({'error': 'Name is required'}), 400
    try:
        rid = execute('INSERT INTO DeliveryDriver (Name,Phone) VALUES (?,?)', (d['Name'], d.get('Phone')))
        return jsonify({'success': True, 'id': rid})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─── Admin APIs ───────────────────────────────────────────────────────────────

ALLOWED_TABLES = ['Customer','Address','Restaurant','Category','FoodItem','Cart','CartItem',
                  'Orders','OrderItem','PaymentMethod','Payment','DeliveryDriver','Delivery','Review','Admin']

@app.route('/api/admin-stats')
def admin_stats():
    if request.headers.get('X-Admin-Pass') != ADMIN_PASS:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'customers':  query('SELECT COUNT(*) as c FROM Customer')[0]['c'],
        'orders':     query('SELECT COUNT(*) as c FROM Orders')[0]['c'],
        'revenue':    query('SELECT COALESCE(SUM(TotalAmount),0) as s FROM Orders')[0]['s'],
        'restaurants':query('SELECT COUNT(*) as c FROM Restaurant')[0]['c'],
        'delivered':  query("SELECT COUNT(*) as c FROM Delivery WHERE DeliveryStatus='Delivered'")[0]['c'],
        'pending':    query("SELECT COUNT(*) as c FROM Delivery WHERE DeliveryStatus='Pending'")[0]['c'],
        'reviews':    query('SELECT COUNT(*) as c FROM Review')[0]['c'],
        'avgRating':  query('SELECT ROUND(AVG(Rating),1) as a FROM Review')[0]['a'] or 0,
    })

@app.route('/api/admin/<table_name>')
def admin_table(table_name):
    if request.headers.get('X-Admin-Pass') != ADMIN_PASS:
        return jsonify({'error': 'Unauthorized'}), 401
    match = next((t for t in ALLOWED_TABLES if t.lower() == table_name.lower()), None)
    if not match:
        return jsonify({'error': 'Table not found'}), 404
    try:
        return jsonify(query(f'SELECT * FROM {match} LIMIT 500'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── Page routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('public', 'admin.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'Server running on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=False)
