import random
from typing import Any, List

from app.schema.allSchema import discount_tier
from app.db.sellerPolicies import insert_itemPolicy,sellerPolicies
from app.db.sellerDatabase import fetch_oneColumn

def main():
    """
        function to populate the seller policis for each 'sku' item in database.
    """
    all_sku = fetch_oneColumn("sku")
    min_quantity =  fetch_oneColumn("min_order_qty")

    min = [10,20,45]
    values = [5,8,15]
    
    dis_tiers:List[discount_tier] = []
    
    for m,v in zip(min,values):
        temp = discount_tier(min_qty=m,value=v)
        dis_tiers.append(temp)
    
    dis_tiers = [dis.model_dump() for dis in dis_tiers]
    
    for sku,min_qty in zip(all_sku,min_quantity,strict=True):
        insert_itemPolicy(sku=sku,min_order_qty=min_qty,
                          absolute_min_price=random.randint(15,130),
                          discount_tiers=dis_tiers)
        
        # print(sellerPolicies(sku=sku,min_order_qty=min_qty,
        #                   absolute_min_price=random.randint(15,130),
        #                   discount_tiers=dis_tiers).model_dump())
        
    print("Entered pollicies into db!")


if __name__=="__main__":
    main()
