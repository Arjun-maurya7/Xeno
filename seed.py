from datetime import date, timedelta
from database import SessionLocal, engine, Base
from model import Customer, Order, Campaign

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    print("Clearing existing data...")
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
    
    db.add_all([c1, c2, c3, c4, c5])
    db.commit() # Commit to generate IDs
    
    print("Seeding orders...")
    today = date.today()
    
    # Arjun: High spender, active (orders totaling $7200, last order 5 days ago)
    o1 = Order(customer_id=c1.id, amount=4500.0, order_date=today - timedelta(days=45))
    o2 = Order(customer_id=c1.id, amount=2700.0, order_date=today - timedelta(days=5))
    
    # Rahul: High spender, inactive (total $8500, last order 75 days ago)
    o3 = Order(customer_id=c2.id, amount=5000.0, order_date=today - timedelta(days=120))
    o4 = Order(customer_id=c2.id, amount=3500.0, order_date=today - timedelta(days=75))
    
    # Priya: Low spender, active (total $1200, last order 12 days ago)
    o5 = Order(customer_id=c3.id, amount=1200.0, order_date=today - timedelta(days=12))
    
    # Sneha: Moderate spender, inactive (total $4500, last order 65 days ago)
    o6 = Order(customer_id=c5.id, amount=4500.0, order_date=today - timedelta(days=65))
    
    # Amit (c4) has never placed an order! (Used to test null checks)
    
    db.add_all([o1, o2, o3, o4, o5, o6])
    
    print("Seeding campaigns...")
    cp1 = Campaign(
        name="Summer Grand Sale",
        audience="High Value Customers",
        channel="Email",
        message="Get 20% off all products today with coupon SUMMER20!",
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
        sent=500,
        delivered=490,
        opened=420,
        clicked=195,
        conversions=38,
        revenue=4560.00
    )
    
    db.add_all([cp1, cp2, cp3])
    db.commit() # Commit to generate IDs

    # Attribute some seeded orders to campaigns
    o2.campaign_id = cp1.id
    o5.campaign_id = cp2.id
    o6.campaign_id = cp3.id
    db.commit()

    print("Seeding customer communication history logs...")
    from model import CommunicationLog
    cl1 = CommunicationLog(campaign_id=cp1.id, customer_id=c1.id, status="converted")
    cl2 = CommunicationLog(campaign_id=cp2.id, customer_id=c2.id, status="opened")
    cl3 = CommunicationLog(campaign_id=cp2.id, customer_id=c3.id, status="converted")
    cl4 = CommunicationLog(campaign_id=cp3.id, customer_id=c5.id, status="converted")
    cl5 = CommunicationLog(campaign_id=cp3.id, customer_id=c1.id, status="clicked")
    
    db.add_all([cl1, cl2, cl3, cl4, cl5])
    db.commit()
    print("Database successfully seeded with test data and history logs!")
    
except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
finally:
    db.close()
