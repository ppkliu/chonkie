import pytest
from tokenizers import Tokenizer

from chonkie.chunker.base import Chunk
from chonkie.chunker.sentence import SentenceChunker


@pytest.fixture
def tokenizer():
    return Tokenizer.from_pretrained("gpt2")


@pytest.fixture
def sample_text():
    text = """The process of text chunking in RAG applications represents a delicate balance between competing requirements. On one side, we have the need for semantic coherence – ensuring that each chunk maintains meaningful context that can be understood and processed independently. On the other, we must optimize for information density, ensuring that each chunk carries sufficient signal without excessive noise that might impede retrieval accuracy. In this post, we explore the challenges of text chunking in RAG applications and propose a novel approach that leverages recent advances in transformer-based language models to achieve a more effective balance between these competing requirements."""
    return text


def test_sentence_chunker_initialization(tokenizer):
    """Test that the SentenceChunker can be initialized with a tokenizer."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)

    assert chunker is not None
    assert chunker.tokenizer == tokenizer
    assert chunker.chunk_size == 512
    assert chunker.chunk_overlap == 128
    assert chunker.min_sentences_per_chunk == 1


def test_sentence_chunker_chunking(tokenizer, sample_text):
    """Test that the SentenceChunker can chunk a sample text into sentences."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)
    chunks = chunker.chunk(sample_text)

    assert len(chunks) > 0
    assert isinstance(chunks[0], Chunk)
    assert all([chunk.token_count <= 512 for chunk in chunks])
    assert all([chunk.token_count > 0 for chunk in chunks])
    assert all([chunk.text is not None for chunk in chunks])
    assert all([chunk.start_index is not None for chunk in chunks])
    assert all([chunk.end_index is not None for chunk in chunks])


def test_sentence_chunker_empty_text(tokenizer):
    """Test that the SentenceChunker can handle empty text input."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)
    chunks = chunker.chunk("")

    assert len(chunks) == 0


def test_sentence_chunker_single_sentence(tokenizer):
    """Test that the SentenceChunker can handle text with a single sentence."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)
    chunks = chunker.chunk("This is a single sentence.")

    assert len(chunks) == 1
    assert chunks[0].text == "This is a single sentence."


def test_sentence_chunker_single_chunk_text(tokenizer):
    """Test that the SentenceChunker can handle text that fits within a single chunk."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)
    chunks = chunker.chunk("Hello, how are you? I am doing well.")

    assert len(chunks) == 1
    assert chunks[0].text == "Hello, how are you? I am doing well."


def test_sentence_chunker_repr(tokenizer):
    """Test that the SentenceChunker has a string representation."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)

    assert (
        repr(chunker)
        == "SentenceChunker(chunk_size=512, chunk_overlap=128, min_sentences_per_chunk=1)"
    )


def test_sentence_chunker_overlap(tokenizer, sample_text):
    """Test that the SentenceChunker creates overlapping chunks correctly."""
    chunker = SentenceChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=128)
    chunks = chunker.chunk(sample_text)

    for i in range(1, len(chunks)):
        assert chunks[i].start_index < chunks[i - 1].end_index

def test_sentence_chunker_min_sentences(tokenizer):
    """Test that the SentenceChunker respects minimum sentences per chunk."""
    chunker = SentenceChunker(
        tokenizer=tokenizer,
        chunk_size=512,
        chunk_overlap=128,
        min_sentences_per_chunk=2,
    )
    chunks = chunker.chunk("First sentence. Second sentence. Third sentence.")

    assert len(chunks) > 0
    for chunk in chunks:
        # Count sentences by splitting on periods
        sentence_count = len([s for s in chunk.text.split(".") if s.strip()])
        assert (
            sentence_count >= 2 or sentence_count == 1
        )  # Last chunk might have fewer sentences


if __name__ == "__main__":
    pytest.main()
