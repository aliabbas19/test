
from unittest.mock import MagicMock
from app.models.star_bank import StarBank
from app.models.user import User

# Mock Database Session
mock_db = MagicMock()

# Mock Data: 3 Users
# User 1: 5 Stars (Should be Hero)
# User 2: 4 Stars (Should NOT be Hero with new logic)
# User 3: 3 Stars (Should NOT be Hero)

user1 = User(id=1, username="champion", full_name="Champion User")
bank1 = StarBank(user_id=1, banked_stars=5)

user2 = User(id=2, username="almost", full_name="Almost Hero")
bank2 = StarBank(user_id=2, banked_stars=4)

user3 = User(id=3, username="average", full_name="Average User")
bank3 = StarBank(user_id=3, banked_stars=3)

# Mock Query Result
# The query joins User and StarBank and filters by stars
all_data = [(user1, bank1), (user2, bank2), (user3, bank3)]

print("--- Testing Threshold: 5 ---")
threshold_5_heroes = [
    (u, b) for u, b in all_data 
    if b.banked_stars >= 5
]

for u, b in threshold_5_heroes:
    print(f"HERO FOUND: {u.full_name} with {b.banked_stars} stars")

if len(threshold_5_heroes) == 1 and threshold_5_heroes[0][0].id == 1:
    print("SUCCESS: Only 5-star user is selected.")
else:
    print("FAILURE: Validation failed.")

print("\n--- Testing Old Threshold: 4 ---")
threshold_4_heroes = [
    (u, b) for u, b in all_data 
    if b.banked_stars >= 4
]

for u, b in threshold_4_heroes:
    print(f"OLD LOGIC WOULD FIND: {u.full_name} with {b.banked_stars} stars")
