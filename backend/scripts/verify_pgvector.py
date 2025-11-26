from sqlalchemy import text
from app.db.session import engine

print("Checking pgvector extension status...\n")

with engine.connect() as conn:
    # Check if extension exists
    result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
    ext = result.fetchone()
    
    if ext:
        print("✅ pgvector extension is ENABLED")
        print(f"   Extension OID: {ext[0]}")
        print(f"   Extension Name: {ext[1]}")
        print(f"   Schema: {ext[2]}")
    else:
        print("❌ pgvector extension is NOT enabled")
    
    print("\n" + "="*50)
    
    # List all extensions
    result = conn.execute(text("SELECT extname, extversion FROM pg_extension ORDER BY extname"))
    extensions = result.fetchall()
    
    print(f"\nAll installed extensions ({len(extensions)}):")
    for ext_name, ext_version in extensions:
        marker = "✅" if ext_name == 'vector' else "  "
        print(f"{marker} {ext_name} (version {ext_version})")
    
    print("\n" + "="*50)
    
    # Test vector functionality
    try:
        result = conn.execute(text("SELECT '[1,2,3]'::vector"))
        print("\n✅ Vector type is working!")
        print(f"   Test vector: {result.fetchone()[0]}")
    except Exception as e:
        print(f"\n❌ Vector type test failed: {e}")
