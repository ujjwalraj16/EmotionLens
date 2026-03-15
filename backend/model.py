import tensorflow as tf
import keras
from keras import layers


def build_text_cnn(
    vocab_size: int,
    embed_dim: int       = 128,
    num_classes: int     = 28,
    num_filters: int     = 128,
    kernel_sizes: list   = None,
    dropout_rate: float  = 0.5,
    max_seq_len: int     = 64,
) -> keras.Model:
    """
    Build and return a compiled TextCNN Keras model.

    Args:
        vocab_size   : Total number of unique tokens (including <PAD> and <UNK>).
        embed_dim    : Size of each token's embedding vector.
        num_classes  : Number of emotion categories.
        num_filters  : Number of filters for EACH Conv1D kernel size.
        kernel_sizes : List of convolutional window sizes (n-gram sizes).
        dropout_rate : Fraction of units to drop before the output layer.
        max_seq_len  : Fixed sequence length (used to set input shape).

    Returns:
        A compiled keras.Model ready for .fit()
    """

    if kernel_sizes is None:
        kernel_sizes = [2, 3, 4]   # bigram, trigram, 4-gram

    inputs = keras.Input(shape=(max_seq_len,), dtype="int32", name="token_ids")
    x = layers.Embedding(
        input_dim=vocab_size,
        output_dim=embed_dim,
        mask_zero=True,
        name="embedding",
    )(inputs)

    branch_outputs = []
    for k in kernel_sizes:

        conv = layers.Conv1D(
            filters=num_filters,
            kernel_size=k,
            activation="relu",
            padding="valid",
            name=f"conv_k{k}",
        )(x)

        pooled = layers.GlobalMaxPooling1D(name=f"pool_k{k}")(conv)
        branch_outputs.append(pooled)

    merged = layers.Concatenate(name="concat")(branch_outputs)

    dropped = layers.Dropout(rate=dropout_rate, name="dropout")(merged)

    outputs = layers.Dense(
        units=num_classes,
        activation="softmax",
        name="emotion_probs",
    )(dropped)

    model = keras.Model(inputs=inputs, outputs=outputs, name="TextCNN_Emotions")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",   # labels are integer
        metrics=["accuracy"],
    )

    return model