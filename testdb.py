from sqlalchemy import create_engine, text

# Replace 'yourpassword' with your actual PostgreSQL password
engine = create_engine("postgresql+psycopg2://postgres:harsha123@localhost:5432/floatchat")

with engine.connect() as conn:
    result = conn.execute(text("SELECT NOW()"))  # Execute a simple query
    print("Connected! Current time:", result.scalar())  # Fetch and print the result
