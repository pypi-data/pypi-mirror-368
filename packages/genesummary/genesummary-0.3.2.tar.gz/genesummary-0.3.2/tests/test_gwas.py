#!/usr/bin/env python3

print("Starting GWAS test...")

try:
    from geneinfo.fetchers import GwasFetcher

    print("✅ GwasFetcher imported successfully")

    gwas = GwasFetcher()
    print("✅ GwasFetcher created successfully")

    # Test with a quick call - just one gene, minimal output
    print("Testing GWAS data retrieval for TP53...")
    data = gwas.get_gwas_data("TP53")

    if data:
        print("✅ GWAS data retrieved successfully!")
        print(f"Keys: {list(data.keys())}")
        print(f"Total SNPs: {data.get('total_snps', 0)}")
        print(f"Associations: {len(data.get('associations', []))}")
    else:
        print("❌ No GWAS data returned")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
