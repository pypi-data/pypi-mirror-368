import asyncio
from smartfaker import Faker

# Initialize the Faker instance
fake = Faker()

async def generate_addresses():
    print("=== SmartFaker Tutorial ===")
    print("Welcome! This script generates fake addresses using the SmartFaker library.")
    print("Supported country codes can be found in the data/ directory (e.g., BD, US, UK).")

    # Get country code from user
    while True:
        country_code = input("Enter a country code (e.g., BD for Bangladesh) or 'quit' to exit: ").upper()
        if country_code == 'QUIT':
            print("Exiting tutorial. Goodbye!")
            return
        try:
            await fake.address(country_code, amount=1)  # Test if valid
            break
        except ValueError as e:
            print(f"Error: {e}. Please try again or enter 'quit' to exit.")

    # Get amount from user
    while True:
        amount_input = input("Enter the number of addresses to generate (press Enter for 1): ")
        amount = 1 if not amount_input else int(amount_input)
        if amount <= 0:
            print("Amount must be positive. Please try again.")
            continue
        if amount > 100:  # Arbitrary limit to prevent excessive output
            print("Amount too high. Limiting to 100. Proceed? (y/n): ")
            if input().lower() != 'y':
                continue
        break

    try:
        # Generate addresses
        addresses = await fake.address(country_code, amount)
        print(f"\nGenerated {amount} address(es) for {country_code}:")
        if amount == 1:
            print(addresses)
        else:
            for i, addr in enumerate(addresses, 1):
                print(f"Address {i}: {addr}")
        print("Tutorial complete! Explore more with different codes or amounts.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(generate_addresses())