from app.scripts.mockSellerData import fake_data_gen

try:
    amt = int(input("Enter Amount of Mock Data to be create and inserted to the db :- "))
    message = fake_data_gen(amt=amt)
    
    if message:
        print(f"Created {amt} amount of data and inserted into DB successfully!")

except Exception as e:
    print(f"Something went wrong: {type(e).__name__}: {e}")