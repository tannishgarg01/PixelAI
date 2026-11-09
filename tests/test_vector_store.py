from services.vector_store import cosine_similarity
def test_identical_vectors(): assert abs(cosine_similarity([1,0,0],[1,0,0])-1.0)<1e-9
def test_orthogonal_vectors(): assert abs(cosine_similarity([1,0],[0,1]))<1e-9
def test_invalid_dimensions(): assert cosine_similarity([1,0],[1])==0.0
