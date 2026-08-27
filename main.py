from app.scripts.mockSellerData import fake_data_gen

if __name__=="__main__":
    fake_data_gen(85)
    
# from app.db.sellerDatabase import insertDatabase, simple_fetchAll

# import pandas as pd

# def main():
#     print("hello")
    
# def insert(amt:int):
#     entries = genFakeEntries(amt=amt)
#     for entry in entries:
#         insertDatabase(**entry)

# def search():
#     # result = simpleVector_search(query="electronics")
#     result = simple_fetchAll()
#     return result

# ## fill the database with mock data ###

# try:
#     insert(75)
#     print("Inserted Mock Datasets!")
# except Exception as e:
#     print(f"error - {e}")

# ## Get all mock data from the db ##
# result = search()
# rows_list= []

# for entry in result:    
    
#     entry_df = {"sku":entry.sku,
#                 "item":entry.item,
#                 "price_base":entry.price_base,
#                 "description":entry.description,
#                 "min_order_qty":entry.min_order_qty,
#                 "stock_quantity":entry.stock_quantity,
#                 "category":entry.category,
#                 "company":entry.company,
#                 "location_availability":entry.location_availability} # not include the vector embeddings 
    
#     rows_list.append(entry_df)
    
#     print(entry.sku)
#     print(entry.item)
#     print(entry.category)
#     print(entry.company)
#     print(entry.location_availability)
#     print(".................................")

# # storing to .csv file ##
# try:
#     df = pd.DataFrame(data=rows_list)
#     df.to_csv("mock_data.csv",index=False)
# except Exception as e:
#     print(f"error :- {e}")

