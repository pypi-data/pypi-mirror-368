#!/usr/bin/env python3
"""
Simple test for your HybridVectorizer.
Put this in the same folder as your HybridVectorizer code and run.
"""

import pandas as pd
import numpy as np
import tempfile
import os
import time
from hybrid_vectorizer import HybridVectorizer

# Paste your HybridVectorizer code here, OR import it
# For now, assuming your code is in the same file or imported somehow

def create_test_data():
    """Create simple test dataset."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'description': [
            'AI machine learning platform for enterprises',
            'Data analytics and business intelligence',
            'Computer vision technology for robots',
            'Natural language processing chatbots',
            'Predictive analytics for healthcare'
        ],
        'category': ['AI', 'Analytics', 'Vision', 'NLP', 'Healthcare'],
        'funding': [1000000, 2500000, 800000, 1200000, 1800000],
        'employees': [50, 150, 30, 80, 200]
    })

def run_basic_test():
    """Run basic functionality test."""
    print("🧪 Running Basic HybridVectorizer Test")
    print("=" * 45)
    
    try:
        # Create test data
        df = create_test_data()
        print(f"✓ Test data created: {df.shape}")
        
        # Initialize vectorizer
        hv = HybridVectorizer(index_column='id')
        print("✓ HybridVectorizer initialized")
        
        # Fit and transform
        start_time = time.time()
        vectors = hv.fit_transform(df)
        fit_time = time.time() - start_time
        print(f"✓ fit_transform completed in {fit_time:.2f}s")
        print(f"✓ Vector shape: {vectors.shape}")
        
        # Basic validation
        assert vectors.shape[0] == len(df), "Wrong number of rows"
        assert vectors.shape[1] > 0, "No features generated"
        assert not np.isnan(vectors).any(), "Vectors contain NaN"
        print("✓ Vector validation passed")
        
        # Test similarity search
        query = {
            'description': 'artificial intelligence platform',
            'category': 'AI',
            'employees': 100
        }
        
        print("\n--- Testing Similarity Search ---")
        start_time = time.time()
        results = hv.similarity_search(query, top_n=3)
        search_time = time.time() - start_time
        print(f"✓ Search completed in {search_time:.3f}s")
        
        # Display results
        print("\nTop 3 Results:")
        for i, row in results.iterrows():
            print(f"  {row['id']}: {row['description'][:50]}... (similarity: {row['similarity']:.4f})")
        
        # Validate results
        assert len(results) == 3, "Should return 3 results"
        assert 'similarity' in results.columns, "Missing similarity column"
        assert all(results['similarity'] >= 0), "Negative similarities"
        assert not all(results['similarity'] == 0), "All similarities are zero!"
        
        print(f"\n✓ Search validation passed")
        print(f"✓ Similarity range: {results['similarity'].min():.4f} - {results['similarity'].max():.4f}")
        
        # Test late fusion
        print("\n--- Testing Late Fusion ---")
        results2 = hv.similarity_search_late_fusion(
            query, 
            top_n=3,
            block_weights={'text': 2, 'categorical': 1, 'numerical': 1}
        )
        print("✓ Late fusion search works")
        
        # Test dimension consistency (the key bug we fixed)
        print("\n--- Testing Dimension Consistency ---")
        for block_type in ['text', 'categorical', 'numerical']:
            if hv.block_vectors[block_type].shape[1] > 0:
                query_vec = hv._transform_query_generic(query, block_filter=block_type)
                block_matrix = hv.block_vectors[block_type]
                
                print(f"  {block_type}: data={block_matrix.shape}, query={query_vec.shape}")
                
                if query_vec.shape[1] != block_matrix.shape[1]:
                    print(f"  ❌ DIMENSION MISMATCH in {block_type}!")
                    return False
                else:
                    print(f"  ✅ {block_type} dimensions match")
        
        # Test error handling
        print("\n--- Testing Error Handling ---")
        
        # Test unfitted model
        try:
            hv_new = HybridVectorizer()
            hv_new.similarity_search(query)
            print("❌ Should have failed on unfitted model")
            return False
        except RuntimeError:
            print("✓ Properly rejects unfitted model")
        
        # Test empty query
        try:
            hv.similarity_search({})
            print("❌ Should have failed on empty query")
            return False
        except ValueError:
            print("✓ Properly rejects empty query")
        
        # Performance check
        if fit_time > 10:
            print(f"⚠️  fit_transform is slow: {fit_time:.2f}s")
        if search_time > 0.5:
            print(f"⚠️  search is slow: {search_time:.3f}s")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your HybridVectorizer is working correctly")
        print("✅ Dimension bug is fixed")  
        print("✅ Error handling is working")
        print("✅ Ready for Phase 2!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # You need to make sure HybridVectorizer is available
    # Option 1: Copy your class code above this line
    # Option 2: Put this file in same folder as your code and add:
    # exec(open('your_hybrid_vectorizer_file.py').read())
    # Option 3: If you have it as a proper module: from your_module import HybridVectorizer
    
    print("IMPORTANT: Make sure HybridVectorizer class is available!")
    print("Either copy your class code into this file, or import it.\n")
    
    try:
        # Test if HybridVectorizer is available
        test_hv = HybridVectorizer()
        print("✓ HybridVectorizer class found")
        
        # Run the test
        success = run_basic_test()
        
        if success:
            print("\n🚀 READY FOR BETA RELEASE!")
        else:
            print("\n🔧 NEEDS MORE WORK")
            
    except NameError:
        print("❌ HybridVectorizer class not found!")
        print("Please add your class code to this file or import it properly.")
    except Exception as e:
        print(f"❌ Setup error: {e}")