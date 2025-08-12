#!/usr/bin/env python3

"""
TranscriptFormer CLI

A command-line interface for TranscriptFormer model inference, artifact downloads, and data downloads.

Usage:
    transcriptformer inference --checkpoint-path PATH --data-file PATH [OPTIONS]
    transcriptformer download MODEL [--checkpoint-dir DIR]
    transcriptformer download-data --species SPECIES [OPTIONS]

Commands:
    inference      Run inference with a TranscriptFormer model
    download       Download and extract TranscriptFormer model artifacts
    download-data  Download CellxGene Discover datasets by species

Common Options for Inference:
    --checkpoint-path      Path to model checkpoint directory (required)
    --data-file            Path to input AnnData file (required)
    --output-path          Directory for saving results
    --output-filename      Filename for the output embeddings
    --batch-size           Batch size for inference
    --gene-col-name        Column in AnnData.var with gene identifiers
    --precision            Numerical precision (16-mixed or 32)
    --pretrained-embedding Path to embedding file for out-of-distribution species

Advanced Configuration:
    Use --config-override for any configuration options not exposed as arguments above.
    These directly modify values in the inference_config.yaml configuration.

Examples
--------
    # Run inference with basic options
    transcriptformer inference --checkpoint-path ./checkpoints/tf_sapiens --data-file ./data/my_data.h5ad

    # Run inference with additional options
    transcriptformer inference --checkpoint-path ./checkpoints/tf_sapiens --data-file ./data/my_data.h5ad \
      --output-path ./custom_output_dir --output-filename custom_output.h5ad \
      --batch-size 16 --gene-col-name gene_id --precision 32

    # Run inference with advanced configuration overrides
    transcriptformer inference --checkpoint-path ./checkpoints/tf_sapiens --data-file ./data/my_data.h5ad \
      --config-override model.data_config.normalize_to_scale=10000 \
      --config-override model.inference_config.obs_keys.0=cell_type

    # Download the sapiens model
    transcriptformer download tf-sapiens

    # Download all models and embeddings
    transcriptformer download all
"""

import argparse
import logging
import sys
import warnings

# Suppress annoying warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="anndata")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*read_.*from.*anndata.*deprecated.*")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# TranscriptFormer logo
TF_LOGO = """
\033[38;2;138;43;226m ___________  ___   _   _  _____           _       _  ______ ______________  ___ ___________
\033[38;2;138;43;226m|_   _| ___ \\/ _ \\ | \\ | |/  ___|         (_)     | | |  ___|  _  | ___ \\  \\/  ||  ___| ___ \\
\033[38;2;132;57;207m  | | | |_/ / /_\\ \\|  \\| |\\ `--.  ___ _ __ _ _ __ | |_| |_  | | | | |_/ / .  . || |__ | |_/ /
\033[38;2;126;71;188m  | | |    /|  _  || . ` | `--. \\/ __| '__| | '_ \\| __|  _| | | | |    /| |\\/| ||  __||    /
\033[38;2;120;85;169m  | | | |\\ \\| | | || |\\  |/\\__/ / (__| |  | | |_) | |_| |   \\ \\_/ / |\\ \\| |  | || |___| |\\ \\
\033[38;2;114;99;150m  \\_/ \\_| \\_\\_| |_/\\_| \\_/\\____/ \\___|_|  |_| .__/ \\__\\_|    \\___/\\_| \\_\\_|  |_/\\____/\\_| \\_|
\033[38;2;108;113;131m                                            | |
\033[38;2;108;113;131m                                            |_|
\033[0m"""


def setup_inference_parser(subparsers):
    """Setup the parser for the inference command."""
    parser = subparsers.add_parser(
        "inference",
        help="Run inference with a TranscriptFormer model",
        description="Run inference with a TranscriptFormer model on scRNA-seq data.",
    )

    # Required arguments
    parser.add_argument(
        "--checkpoint-path",
        required=True,
        help="Path to the model checkpoint directory",
    )
    parser.add_argument(
        "--data-file",
        required=True,
        help="Path to input AnnData file to run inference on",
    )
    parser.add_argument(
        "--output-path",
        default="./inference_results",
        help="Directory where results will be saved (default: ./inference_results)",
    )
    parser.add_argument(
        "--output-filename",
        default="embeddings.h5ad",
        help="Filename for the output embeddings (default: embeddings.h5ad)",
    )

    # Optional arguments
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Number of samples to process in each batch (default: 8)",
    )
    parser.add_argument(
        "--gene-col-name",
        default="ensembl_id",
        help="Column name in AnnData.var containing gene identifiers (default: ensembl_id)",
    )
    parser.add_argument(
        "--precision",
        default="16-mixed",
        choices=["16-mixed", "32"],
        help="Numerical precision for inference (default: 16-mixed)",
    )
    parser.add_argument(
        "--pretrained-embedding",
        help="Path to pretrained embeddings for out-of-distribution species",
    )
    parser.add_argument(
        "--clip-counts",
        type=int,
        default=30,
        help="Maximum count value (higher values will be clipped) (default: 30)",
    )
    parser.add_argument(
        "--filter-to-vocabs",
        action="store_true",
        default=True,
        help="Whether to filter genes to only those in the vocabulary (default: True)",
    )
    parser.add_argument(
        "--model-type",
        default="transcriptformer",
        choices=["transcriptformer", "esm2ce"],
        help="Type of model to use for inference (default: transcriptformer)",
    )
    parser.add_argument(
        "--use-raw",
        type=lambda x: None if x.lower() == "auto" else x.lower() == "true",
        default=None,
        help="Whether to use raw counts from AnnData.raw.X (True), adata.X (False), or auto-detect (None/auto) (default: None)",
    )
    parser.add_argument(
        "--emb-type",
        default="cell",
        choices=["cell", "cge"],
        help="Type of embeddings to extract: 'cell' for mean-pooled cell embeddings or 'cge' for contextual gene embeddings (default: cell)",
    )
    parser.add_argument(
        "--remove-duplicate-genes",
        action="store_true",
        default=False,
        help="Remove duplicate genes if found instead of raising an error (default: False)",
    )

    # Allow arbitrary config overrides
    parser.add_argument(
        "--config-override",
        action="append",
        default=[],
        help="Override any configuration value not covered by the explicit arguments above. "
        "Format: key.path=value (e.g., model.data_config.normalize_to_scale=10000). "
        "Can be specified multiple times for different config keys.",
    )


def setup_download_parser(subparsers):
    """Setup the parser for the download command."""
    parser = subparsers.add_parser(
        "download",
        help="Download and extract TranscriptFormer model artifacts",
        description="Download and extract TranscriptFormer model artifacts from a public S3 bucket.",
    )

    parser.add_argument(
        "model",
        choices=["tf-sapiens", "tf-exemplar", "tf-metazoa", "all", "all-embeddings"],
        help="Model to download ('all' for all models and embeddings, 'all-embeddings' for just embeddings)",
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="./checkpoints",
        help="Directory to store the downloaded checkpoints (default: ./checkpoints)",
    )


def setup_download_data_parser(subparsers):
    """Setup the parser for the download-data command."""
    parser = subparsers.add_parser(
        "download-data",
        help="Download CellxGene Discover datasets by species",
        description="Download single-cell RNA sequencing datasets from the CellxGene Discover portal filtered by species.",
    )

    # Required arguments
    parser.add_argument(
        "--species",
        help="Comma-separated list of species to download (e.g., 'homo sapiens,mus musculus'). Required unless using --test-only.",
    )

    # Optional arguments
    parser.add_argument(
        "--output-dir",
        default="./data/cellxgene",
        help="Directory where datasets will be saved (default: ./data/cellxgene)",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=4,
        help="Number of parallel processes for downloading (default: 4)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Maximum number of retry attempts per dataset (default: 5)",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip saving dataset metadata to JSON file",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Only test API connectivity, don't download datasets",
    )


def run_inference_cli(args):
    """Run inference using command line arguments."""
    # Import the inference module directly
    from transcriptformer.cli.inference import main as inference_main

    # Create a hydra-compatible config dictionary for direct use with inference.py
    cmd = [
        "--config-name=inference_config.yaml",
        f"model.checkpoint_path={args.checkpoint_path}",
        f"model.inference_config.data_files.0={args.data_file}",
        f"model.inference_config.batch_size={args.batch_size}",
        f"model.data_config.gene_col_name={args.gene_col_name}",
        f"model.inference_config.output_path={args.output_path}",
        f"model.inference_config.output_filename={args.output_filename}",
        f"model.inference_config.precision={args.precision}",
        f"model.model_type={args.model_type}",
        f"model.inference_config.emb_type={args.emb_type}",
        f"model.data_config.remove_duplicate_genes={args.remove_duplicate_genes}",
    ]

    # Add pretrained embedding if specified
    if args.pretrained_embedding:
        cmd.append(f"model.inference_config.pretrained_embedding={args.pretrained_embedding}")

    # Add any arbitrary config overrides
    for override in args.config_override:
        cmd.append(override)

    # Print logo
    print(TF_LOGO)

    # Override sys.argv for Hydra to pick up
    saved_argv = sys.argv
    sys.argv = [sys.argv[0]] + cmd

    try:
        # Call the main function directly
        inference_main()
    finally:
        # Restore original sys.argv
        sys.argv = saved_argv


def run_download_cli(args):
    """Run download using command line arguments."""
    # Import the download_artifacts module directly
    from transcriptformer.cli.download_artifacts import download_and_extract

    models = {
        "tf-sapiens": "tf_sapiens",
        "tf-exemplar": "tf_exemplar",
        "tf-metazoa": "tf_metazoa",
        "all-embeddings": "all_embeddings",
    }

    if args.model == "all":
        # Download all models and embeddings
        for model in ["tf_sapiens", "tf_exemplar", "tf_metazoa", "all_embeddings"]:
            download_and_extract(model, args.checkpoint_dir)
    elif args.model == "all-embeddings":
        # Download only embeddings
        download_and_extract("all_embeddings", args.checkpoint_dir)
    else:
        download_and_extract(models[args.model], args.checkpoint_dir)


def run_download_data_cli(args):
    """Run download-data using command line arguments."""
    # Import the download_data module
    from transcriptformer.cli.download_data import main as download_data_main

    # Validate arguments
    if not args.test_only and not args.species:
        print("❌ Error: --species is required unless using --test-only")
        sys.exit(1)

    # Parse species list
    species_list = [s.strip() for s in args.species.split(",")] if args.species else []

    # Print logo
    print(TF_LOGO)

    # Run the download
    try:
        successful_downloads = download_data_main(
            species=species_list,
            output_dir=args.output_dir,
            n_processes=args.processes,
            max_retries=args.max_retries,
            save_metadata=not args.no_metadata,
            test_only=args.test_only,
        )

        if args.test_only:
            if successful_downloads:
                print("\n✅ API connectivity test passed!")
            else:
                print("\n❌ API connectivity test failed.")
        else:
            if successful_downloads > 0:
                print(f"\n✅ Successfully downloaded {successful_downloads} datasets to {args.output_dir}")
            else:
                print("\n⚠️  No datasets were downloaded. Check the species names and try again.")

    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        if not args.test_only:
            print("💡 Try running with --test-only to check API connectivity first")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="TranscriptFormer command-line interface",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Set up parsers for each command
    setup_inference_parser(subparsers)
    setup_download_parser(subparsers)
    setup_download_data_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Run the appropriate command
    if args.command == "inference":
        run_inference_cli(args)
    elif args.command == "download":
        run_download_cli(args)
    elif args.command == "download-data":
        run_download_data_cli(args)


if __name__ == "__main__":
    main()
