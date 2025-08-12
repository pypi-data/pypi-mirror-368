import argparse

from .agents import SUPPORTED_METHOD_NAMES
from .llm import DEFAULT_LLMS_RPM_TPM_CONFIG_FPATH, SUPPORTED_LLM_SERVERS


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PhantomWiki Evaluation")
    parser.add_argument(
        "--server",
        type=str.lower,
        default="together",
        choices=SUPPORTED_LLM_SERVERS,
        help="The server to use for the assistant. "
        "NOTE: to add a new server, please submit a PR with the implementation",
    )
    parser.add_argument(
        "--model_name",
        "-m",
        type=str,
        default="meta-llama/llama-vision-free",
        help="The model name or the path to the model, see suggestions in "
        "`src/phantom_eval/llm/api_llms_config.yaml`",
    )
    parser.add_argument(
        "--method",
        type=str.lower,
        default="zeroshot",
        help="Evaluation method. " "NOTE: to add a new method, please submit a PR with the implementation",
        # choices=SUPPORTED_METHOD_NAMES,
    )

    # Method params
    parser.add_argument(
        "--react_max_steps", type=int, default=50, help="Maximum number of steps for the ReAct/Act agent"
    )
    parser.add_argument(
        "--sc_num_votes",
        type=int,
        default=5,
        help="Number of votes for an agent implementing self-consistency (majority votes)",
    )
    parser.add_argument(
        "--embedding_model_name",
        type=str.lower,
        default="whereisai/uae-large-v1",
        help="Model used for RAG's embeddings",
    )
    parser.add_argument(
        "--retriever_num_documents", type=int, default=4, help="Number of documents retrieved"
    )
    parser.add_argument(
        "--retrieval_method",
        type=str,
        default="bm25",
        help="Method used for retrieval. "
        "bm25 and dense use the retriever from FlashRAG and expects a pre-computed index. "
        "vllm uses the retriever from LangChain and launches a vllm server for retrieval. "
        "NOTE: bm25 and dense can only evaluate one split at a time.",
        choices=["bm25", "dense", "vllm"],
    )
    parser.add_argument("--index_path", type=str, help="Path to the index for the retriever")
    parser.add_argument("--corpus_path", type=str, help="Path to the corpus for the retriever")
    parser.add_argument(
        "--prolog_query",
        action="store_true",
        help="Whether to convert LLM output to Prolog queries and execute them. "
        "NOTE: Only implemented for n-shot agents. "
        "NOTE: Can only evaluate one split at a time due to Prolog database limitations",
    )

    # LLM inference params
    parser.add_argument(
        "--inf_vllm_max_model_len",
        type=int,
        default=None,
        help="Maximum model length (vLLM param), if None, uses max model length specified in model config",
    )
    parser.add_argument(
        "--inf_vllm_tensor_parallel_size",
        type=int,
        default=None,
        help="number of gpus (vLLM param), if None, uses all available gpus",
    )
    parser.add_argument(
        "--inf_vllm_lora_path",
        type=str,
        default=None,
        help="Path to the LoRA weights (vLLM param), if None, no LoRA adapters are used",
    )
    parser.add_argument("--inf_vllm_port", type=int, default=8000, help="vllm server port number")
    parser.add_argument(
        "--inf_embedding_port", type=int, default=8001, help="embedding vllm server port number"
    )
    parser.add_argument(
        "--inf_max_tokens", type=int, default=4096, help="Maximum number of tokens to generate"
    )
    parser.add_argument("--inf_temperature", "-T", type=float, default=0.0, help="Temperature for sampling")
    parser.add_argument("--inf_top_p", "-p", type=float, default=0.7, help="Top-p for sampling")
    parser.add_argument("--inf_top_k", "-k", type=int, default=-1, help="Top-k for sampling")
    parser.add_argument(
        "--inf_repetition_penalty", "-r", type=float, default=1.0, help="Repetition penalty for sampling"
    )
    parser.add_argument("--inf_seed_list", type=int, nargs="+", default=[1], help="List of seeds to evaluate")
    parser.add_argument("--inf_max_retries", type=int, default=3, help="Number of tries to get response")
    parser.add_argument("--inf_wait_seconds", type=int, default=2, help="Seconds to wait between tries")
    parser.add_argument(
        "--inf_usage_tier",
        type=int,
        default=1,
        help="API usage tier (note: tier 0 corresponds to free versions)",
    )
    parser.add_argument(
        "--inf_relax_rate_limits",
        action="store_true",
        help="Flag to relax enforcing rate limits for the LLMs. "
        "By default, the LLMChat class enforces rate limits according to the specified usage tier "
        "(see --inf_usage_tier and --inf_llms_rpm_tpm_config_fpath). "
        "To determine your usage tier, you can check on the console page of your specific LLM provider. "
        "See README.md for links to the console pages.",
    )
    parser.add_argument(
        "--inf_llms_rpm_tpm_config_fpath",
        type=str,
        default=str(DEFAULT_LLMS_RPM_TPM_CONFIG_FPATH),
        help="Path to the config file with rate limits for the LLMs",
    )
    parser.add_argument(
        "--inf_is_deepseek_r1_model",
        action="store_true",
        help="Flag to specify if the model is DeepSeek-R1, "
        "for correctly parsing <think>...</think> tags, "
        "and determining the additional stop token in vllm",
    )
    parser.add_argument(
        "--inf_vllm_offline",
        action="store_true",
        help="Flag to use vLLM (batched) offline inference, "
        "which can be substantially faster than using the server when supported by the method",
    )

    # Dataset params
    parser.add_argument(
        "--dataset",
        type=str,
        default="kilian-group/phantom-wiki-v1",
        help="Dataset name if loading from HF or the path to local dataset",
    )
    parser.add_argument(
        "--split_list",
        default=["depth_20_size_50_seed_1"],
        type=str,
        nargs="+",
        help="List of dataset splits to evaluate",
    )
    parser.add_argument("--from_local", action="store_true", help="Load the dataset from a local folder")
    parser.add_argument(
        "--exclude_aggregation_questions",
        action="store_true",
        help="If set, the evaluation will skip aggregation questions (e.g., 'How many ...')",
    )
    parser.add_argument("--batch_size", "-bs", default=10, type=int, help="Batch size (>=1)")
    parser.add_argument(
        "--batch_number",
        "-bn",
        default=None,
        type=int,
        help="Batch number (>=1). For example, if batch_size=100 and batch_number=1, "
        "then the first 100 questions will be evaluated "
        "if None (default), all batches will be evaluated",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force to overwrite the output file"
        "Otherwise, it will skip the evaluation if the output file exists",
    )
    parser.add_argument(
        "--ignore_agent_interactions",
        action="store_true",
        help="If you don't want to save the agent interactions to the predictions JSON files, set this flag",
    )
    # Saving params
    parser.add_argument("--output_dir", "-od", default="out", help="Path to read/write the outputs")
    parser.add_argument(
        "--log_level",
        default="INFO",
        type=str.upper,
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    return parser
