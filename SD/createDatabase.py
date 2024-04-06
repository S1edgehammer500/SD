from Model.Database import *
from Model.DiscountDB import *
from Model.FoodDB import *
from Model.discountListDB import *
from Model.foodListDB import *
from Model.InventoryDB import *
from Model.ItemDB import *
from Model.MenuDB import *
from Model.offersDB import *
from Model.ordersDB import *
from Model.ReservationDB import *
from Model.RestaurantDB import *
from Model.userDB import *

create_user_table()
create_restaurant_table()
create_menu_table()
create_discounts_table()
create_offer_table()
create_food_table()
create_inventory_table()
create_item_table()
create_reservation_table()
create_orders_table()
create_discountList_table()
create_foodList_table()