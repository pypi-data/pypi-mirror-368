import math

import torch
import torch.nn.functional as F


class BertEmbeddings(torch.nn.Module):
    def __init__(self, vocab_size, n_embed=3, max_seq_len=16):
        super().__init__()
        self.max_seq_len = max_seq_len
        self.word_embeddings = torch.nn.Embedding(vocab_size, n_embed)
        self.pos_embeddings = torch.nn.Embedding(max_seq_len, n_embed)
        self.layer_norm = torch.nn.LayerNorm(n_embed, eps=1e-12, elementwise_affine=True)
        self.dropout = torch.nn.Dropout(p=0.1, inplace=False)

    def forward(self, x):
        # Create position IDs based on actual sequence length, but ensure they don't exceed max_seq_len
        seq_len = x.size(1)
        position_ids = torch.arange(seq_len, dtype=torch.long, device=x.device)
        # Ensure position_ids don't exceed max_seq_len
        position_ids = torch.clamp(position_ids, 0, self.max_seq_len - 1)
        
        # Ensure input_ids don't exceed vocab_size
        vocab_size = self.word_embeddings.num_embeddings
        x = torch.clamp(x, 0, vocab_size - 1)
        
        words_embeddings = self.word_embeddings(x)
        position_embeddings = self.pos_embeddings(position_ids)
        embeddings = words_embeddings + position_embeddings
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings


class BertAttentionHead(torch.nn.Module):
    """
    A single attention head in MultiHeaded Self Attention layer.
    The idea is identical to the original paper ("Attention is all you need"),
    however instead of implementing multiple heads to be evaluated in parallel we matrix multiplication,
    separated in a distinct class for easier and clearer interpretability.
    n_embed=3 so that we can visualize the attention scores in 3D space.
    """

    def __init__(self, head_size, dropout=0.1, n_embed=3):
        super().__init__()

        self.head_size = head_size  # Store head_size for use in forward method
        self.query = torch.nn.Linear(in_features=n_embed, out_features=head_size)
        self.key = torch.nn.Linear(in_features=n_embed, out_features=head_size)
        self.values = torch.nn.Linear(in_features=n_embed, out_features=head_size)
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, x, mask):
        # B, Seq_len, N_embed
        B, seq_len, n_embed = x.shape
        q = self.query(x)
        k = self.key(x)
        v = self.values(x)
        weights = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_size)  # (B, Seq_len, Seq_len)
        
        # Handle case where mask might be None
        if mask is not None:
            # Ensure mask has the right shape and type
            if mask.dtype != torch.bool:
                mask = mask.bool()
            # Use a value compatible with float16 (Half) type
            neg_inf = torch.finfo(weights.dtype).min
            weights = weights.masked_fill(~mask, neg_inf)  # mask out not attended tokens
        
        scores = F.softmax(weights, dim=-1)
        scores = self.dropout(scores)
        context = scores @ v
        return context


class BertSelfAttention(torch.nn.Module):
    """
    MultiHeaded Self-Attention mechanism as described in "Attention is all you need"
    """
    def __init__(self, n_heads=1, dropout=0.1, n_embed=3):
        super().__init__()
        # Ensure n_embed is divisible by n_heads
        if n_embed % n_heads != 0:
            # Adjust n_embed to be divisible by n_heads
            n_embed = ((n_embed + n_heads - 1) // n_heads) * n_heads
            print(f"Warning: n_embed adjusted to {n_embed} to be divisible by n_heads {n_heads}")
        
        head_size = n_embed // n_heads
        # Ensure head_size is at least 1
        if head_size < 1:
            head_size = 1
        
        self.n_heads = n_heads
        self.head_size = head_size
        self.n_embed = n_embed
        
        self.heads = torch.nn.ModuleList([BertAttentionHead(head_size, dropout, n_embed) for _ in range(n_heads)])
        self.proj = torch.nn.Linear(head_size * n_heads, n_embed)  # project from multiple heads to the single space
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, x, mask):
        context = torch.cat([head(x, mask) for head in self.heads], dim=-1)
        proj = self.proj(context)
        out = self.dropout(proj)
        return out


class FeedForward(torch.nn.Module):
    def __init__(self, dropout=0.1, n_embed=3):
        super().__init__()

        self.ffwd = torch.nn.Sequential(
            torch.nn.Linear(n_embed, 4 * n_embed),
            torch.nn.GELU(),
            torch.nn.Linear(4 * n_embed, n_embed),
            torch.nn.Dropout(dropout),
        )

    def forward(self, x):
        out = self.ffwd(x)

        return out


class BertLayer(torch.nn.Module):
    """
    Single layer of BERT transformer model
    """

    def __init__(self, n_heads=1, dropout=0.1, n_embed=3):
        super().__init__()

        # unlike in the original paper, today in transformers it is more common to apply layer norm before other layers
        # this idea is borrowed from Andrej Karpathy's series on transformers implementation
        self.layer_norm1 = torch.nn.LayerNorm(n_embed)
        self.self_attention = BertSelfAttention(n_heads, dropout, n_embed)

        self.layer_norm2 = torch.nn.LayerNorm(n_embed)
        self.feed_forward = FeedForward(dropout, n_embed)

    def forward(self, x, mask):
        x = self.layer_norm1(x)
        x = x + self.self_attention(x, mask)
        x = self.layer_norm2(x)
        out = x + self.feed_forward(x)
        return out


class BertEncoder(torch.nn.Module):
    def __init__(self, n_layers=2, n_heads=1, dropout=0.1, n_embed=3):
        super().__init__()

        self.layers = torch.nn.ModuleList([BertLayer(n_heads, dropout, n_embed) for _ in range(n_layers)])

    def forward(self, x, mask):
        for layer in self.layers:
            x = layer(x, mask)

        return x


class BertPooler(torch.nn.Module):
    def __init__(self, dropout=0.1, n_embed=3):
        super().__init__()

        self.dense = torch.nn.Linear(in_features=n_embed, out_features=n_embed)
        self.activation = torch.nn.GELU()

    def forward(self, x):
        pooled = self.dense(x)
        out = self.activation(pooled)

        return out


class MicroBERT(torch.nn.Module):
    """
    MicroBERT is an almost an exact copy of a transformer encoder part described in the paper "Attention is all you need"
    This is a base model that can be used for various purposes such as Masked Language Modelling, Classification,
    Or any other kind of NLP tasks.
    This implementation does not cover the Seq2Seq problem, but can be easily extended to that.
    """

    def __init__(self, vocab_size, n_layers=2, n_heads=1, dropout=0.1, n_embed=3, max_seq_len=16):
        """

        :param vocab_size: size of the vocabulary that tokenizer is using
        :param n_layers: number of BERT layer in the model (default=2)
        :param n_heads: number of heads in the MultiHeaded Self Attention Mechanism (default=1)
        :param dropout: hidden dropout of the BERT model (default=0.1)
        :param n_embed: hidden embeddings dimensionality (default=3)
        :param max_seq_len: max length of the input sequence (default=16)
        """
        super().__init__()
        self.embedding = BertEmbeddings(vocab_size, n_embed, max_seq_len)
        self.encoder = BertEncoder(n_layers, n_heads, dropout, n_embed)
        self.pooler = BertPooler(dropout, n_embed)

    def forward(self, x):
        # attention masking for padded token
        # (batch_size, seq_len, seq_len)
        mask = (x > 0).unsqueeze(1).repeat(1, x.size(1), 1)
        embeddings = self.embedding(x)
        encoded = self.encoder(embeddings, mask)
        pooled = self.pooler(encoded)
        return pooled


class MicroBERTForClassification(torch.nn.Module):
    """
    This is a wrapper on the base MicroBERT that is used for classification task
    One can use this as an example of how to extend and apply nano-BERT to similar custom tasks
    This layer simply adds one additional dense layer for classification
    """
    def __init__(self, vocab_size, n_layers=2, n_heads=1, dropout=0.1, n_embed=3, max_seq_len=16, n_classes=2):
        super().__init__()
        self.micro_bert = MicroBERT(vocab_size, n_layers, n_heads, dropout, n_embed, max_seq_len)
        self.classifier = torch.nn.Linear(in_features=n_embed, out_features=n_classes)

    def forward(self, input_ids):
        embeddings = self.micro_bert(input_ids)
        logits = self.classifier(embeddings)
        return logits
