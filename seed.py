from datetime import date, timedelta
from database import SessionLocal, engine, Base
from model import Customer, Order, Campaign, CommunicationLog

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    print("Clearing existing data...")
    db.query(CommunicationLog).delete()
    db.query(Order).delete()
    db.query(Customer).delete()
    db.query(Campaign).delete()
    db.commit()

    print("Seeding customers...")
    c1 = Customer(name="Arjun Maurya", email="arjun@example.com", phone="9876543210", city="Pune")
    c2 = Customer(name="Rahul Sharma", email="rahul@example.com", phone="9876543211", city="Mumbai")
    c3 = Customer(name="Priya Patel", email="priya@example.com", phone="9876543212", city="Bangalore")
    c4 = Customer(name="Amit Singh", email="amit@example.com", phone="9876543213", city="Delhi")
    c5 = Customer(name="Sneha Reddy", email="sneha@example.com", phone="9876543214", city="Pune")
    c6 = Customer(name="Vikram Aditya", email="vikram@example.com", phone="9876543215", city="Bangalore")
    c7 = Customer(name="Ananya Sen", email="ananya@example.com", phone="9876543216", city="Kolkata")
    c8 = Customer(name="Rohan Mehta", email="rohan@example.com", phone="9876543217", city="Mumbai")
    c9 = Customer(name="Pooja Rao", email="pooja@example.com", phone="9876543218", city="Hyderabad")
    c10 = Customer(name="Deepak Verma", email="deepak@example.com", phone="9876543219", city="Delhi")
    
    db.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
    db.commit() # Commit to generate IDs
    
    print("Seeding orders...")
    today = date.today()
    
    orders = [
        # Arjun (Total Spend: $7,200)
        Order(customer_id=c1.id, amount=4500.0, order_date=today - timedelta(days=45)),
        Order(customer_id=c1.id, amount=2700.0, order_date=today - timedelta(days=5)),
        
        # Rahul (Total Spend: $8,500)
        Order(customer_id=c2.id, amount=5000.0, order_date=today - timedelta(days=120)),
        Order(customer_id=c2.id, amount=3500.0, order_date=today - timedelta(days=75)),
        
        # Priya (Total Spend: $1,200)
        Order(customer_id=c3.id, amount=1200.0, order_date=today - timedelta(days=12)),
        
        # Sneha (Total Spend: $4,500)
        Order(customer_id=c5.id, amount=4500.0, order_date=today - timedelta(days=65)),
        
        # Vikram (Total Spend: $1,800)
        Order(customer_id=c6.id, amount=1500.0, order_date=today - timedelta(days=20)),
        Order(customer_id=c6.id, amount=300.0, order_date=today - timedelta(days=8)),
        
        # Ananya (Total Spend: $2,700)
        Order(customer_id=c7.id, amount=900.0, order_date=today - timedelta(days=40)),
        Order(customer_id=c7.id, amount=1200.0, order_date=today - timedelta(days=22)),
        Order(customer_id=c7.id, amount=600.0, order_date=today - timedelta(days=14)),
        
        # Rohan (Total Spend: $8,750 - New Top Spender!)
        Order(customer_id=c8.id, amount=2500.0, order_date=today - timedelta(days=90)),
        Order(customer_id=c8.id, amount=1800.0, order_date=today - timedelta(days=50)),
        Order(customer_id=c8.id, amount=350.0, order_date=today - timedelta(days=30)),
        Order(customer_id=c8.id, amount=4100.0, order_date=today - timedelta(days=4)),
        
        # Pooja (Total Spend: $450)
        Order(customer_id=c9.id, amount=450.0, order_date=today - timedelta(days=18)),
        
        # Deepak (Total Spend: $230)
        Order(customer_id=c10.id, amount=80.0, order_date=today - timedelta(days=35)),
        Order(customer_id=c10.id, amount=150.0, order_date=today - timedelta(days=2))
        
        # Amit (c4) has never placed an order
    ]
    
    db.add_all(orders)
    db.commit() # Commit to generate IDs
    
    print("Seeding campaigns...")
    cp1 = Campaign(
        name="Summer Grand Sale",
        audience="High Value Customers",
        channel="Email",
        message="Get 20% off all products today with coupon SUMMER20!",
        status="completed",
        sent=250,
        delivered=240,
        opened=180,
        clicked=75,
        conversions=15,
        revenue=1240.50
    )
    cp2 = Campaign(
        name="Win-Back Discount",
        audience="Inactive Customers",
        channel="SMS",
        message="We miss you! Here is a special 15% discount code: WELCOMEBACK.",
        status="completed",
        sent=150,
        delivered=145,
        opened=90,
        clicked=22,
        conversions=4,
        revenue=320.00
    )
    cp3 = Campaign(
        name="Weekend Flash Deal",
        audience="All Customers",
        channel="WhatsApp",
        message="Flash sale alert! Buy 1 Get 1 free only for this weekend.",
        status="completed",
        sent=500,
        delivered=490,
        opened=420,
        clicked=195,
        conversions=38,
        revenue=4560.00
    )
    cp4 = Campaign(
        name="Festive Season Sparkle",
        audience="Top Spenders Segment",
        channel="Email",
        message="Celebrate the festive season with exclusive access to premium collections!",
        status="completed",
        sent=800,
        delivered=780,
        opened=750,
        clicked=480,
        conversions=95,
        revenue=11200.00
    )
    cp5 = Campaign(
        name="App Launch Campaign",
        audience="New Users",
        channel="SMS",
        message="Download our brand new mobile app and get instant cashback on your first purchase!",
        status="draft",
        sent=0,
        delivered=0,
        opened=0,
        clicked=0,
        conversions=0,
        revenue=0.0
    )
    
    db.add_all([cp1, cp2, cp3, cp4, cp5])
    db.commit() # Commit to generate IDs

    # Attribute some orders to campaigns
    orders[1].campaign_id = cp1.id  # Arjun's recent order
    orders[4].campaign_id = cp2.id  # Priya's order
    orders[5].campaign_id = cp3.id  # Sneha's order
    orders[7].campaign_id = cp1.id  # Vikram's recent order
    orders[10].campaign_id = cp3.id # Ananya's recent order
    orders[13].campaign_id = cp4.id # Rohan's recent big order
    db.commit()

    print("Seeding customer communication history logs...")
    cl1 = CommunicationLog(campaign_id=cp1.id, customer_id=c1.id, status="converted")
    cl2 = CommunicationLog(campaign_id=cp2.id, customer_id=c2.id, status="opened")
    cl3 = CommunicationLog(campaign_id=cp2.id, customer_id=c3.id, status="converted")
    cl4 = CommunicationLog(campaign_id=cp3.id, customer_id=c5.id, status="converted")
    cl5 = CommunicationLog(campaign_id=cp3.id, customer_id=c1.id, status="clicked")
    cl6 = CommunicationLog(campaign_id=cp4.id, customer_id=c8.id, status="converted")
    cl7 = CommunicationLog(campaign_id=cp4.id, customer_id=c6.id, status="opened")
    cl8 = CommunicationLog(campaign_id=cp4.id, customer_id=c7.id, status="clicked")
    
    db.add_all([cl1, cl2, cl3, cl4, cl5, cl6, cl7, cl8])
    db.commit()
    print("Database successfully seeded with test data and history logs!")
except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
finally:
    db.close()
