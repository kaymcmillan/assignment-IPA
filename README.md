# assignment-IPA


A command-line Python program that lets a user create an order for an existing
customer, saves it to Supabase, and then retrieves it to verify it was saved.

## Setup
1. Install Python 3.10 or newer.
2. No packages need to be installed. The program uses only Python's standard library.
3. Copy `.env.example` to a new file named `.env` and fill in your Supabase URL and key:
```
    SUPABASE_URL=https://qoektngicmfbuznsjsux.supabase.co
    SUPABASE_KEY=sb_publishable_IWx3nOoZr9OR_9iuV8QB8w_4q5_UrfO
```
4. In Supabase, the `anon` role needs permission to read `customers` and `products`
   and to read and insert into `orders`.

## Run
```
python order_entry.py
```

## What the program does
1. Displays customers and products from Supabase.
2. Asks for a customer ID, product ID, and quantity, and validates each one.
3. Shows an order summary and asks for Y/N confirmation.
4. Saves the order (the database generates the order ID, and the unit price comes from the products table).
5. Runs a new query to retrieve the saved order and displays it.

## Testing
Screenshots of each scenario are below.

| Test | Expected behavior | Result |
|---|---|---|
| Enter text instead of a customer ID | Helpful message; asks again |
| Enter a customer ID that does not exist | Rejects the ID; asks again |
| Enter a product ID that does not exist | Rejects the ID; asks again |
| Enter quantity 0, -2, 1.5, or hello | Rejects each value; asks again |
| Cancel at the confirmation prompt | No order is inserted |
| Confirm a valid order | Exactly one order is inserted |
| Retrieve the newly created order | Saved order appears in the verification table |
