import asyncio
from mcp_server import query_cluster_health, rotate_service_token

async def main():
    print("[*] Executing real tool handlers through @traced...")
    
    # 1. Low-risk infrastructure queries
    print("-> Calling query_cluster_health('prod-us-east-1')...")
    res1 = await query_cluster_health("prod-us-east-1")
    print(f"   Output: {res1}")

    print("-> Calling query_cluster_health('staging-eu-central-1')...")
    res2 = await query_cluster_health("staging-eu-central-1")
    print(f"   Output: {res2}")

    # 2. High-risk token rotation
    print("-> Calling rotate_service_token('auth-gateway')...")
    res3 = await rotate_service_token("auth-gateway")
    print(f"   Output: {res3}")

    # 3. Subsequent query to provide multi-step diff data
    print("-> Calling query_cluster_health('prod-ap-southeast-1')...")
    res4 = await query_cluster_health("prod-ap-southeast-1")
    print(f"   Output: {res4}")

    print("\n[✔] Done! Check trace.jsonl for generated cards.")

if __name__ == "__main__":
    asyncio.run(main())