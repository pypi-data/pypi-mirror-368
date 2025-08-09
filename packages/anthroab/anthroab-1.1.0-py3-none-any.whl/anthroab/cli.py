#!/usr/bin/env python3
"""
AnthroAb CLI - Command Line Interface for Antibody Humanization

Usage:
    anthroab -i <input.fasta> -o <output.fasta> --humanize

Examples:
    anthroab -i input_example.fasta -o humanized_output.fasta --humanize

Input FASTA format:
    Sequences should be named as {seq_name}_VH and {seq_name}_VL
    Use '*' to mark positions for humanization
"""

import argparse
import sys
from tqdm import tqdm
from .predict import predict_masked


def display_logo():
    """Display the AnthroAb logo and welcome message"""
    logo = """
              █████  ███    ██ ████████ ██   ██ ██████   ██████      █████  ██████  
             ██   ██ ████   ██    ██    ██   ██ ██   ██ ██    ██    ██   ██ ██   ██ 
             ███████ ██ ██  ██    ██    ███████ ██████  ██    ██ ██ ███████ ██████  
             ██   ██ ██  ██ ██    ██    ██   ██ ██   ██ ██    ██    ██   ██ ██   ██ 
             ██   ██ ██   ████    ██    ██   ██ ██   ██  ██████     ██   ██ ██████  
    """
    print(logo)
    print("                               Antibody Humanization Model")
    print("                                     v1.1.0\n")





def parse_fasta(fasta_file):
    """Parse FASTA file and return list of (name, sequence) tuples"""
    sequences = []
    current_name = None
    current_seq = ""
    
    try:
        with open(fasta_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_name is not None:
                        sequences.append((current_name, current_seq))
                    current_name = line[1:]  # Remove '>' prefix
                    current_seq = ""
                elif line:
                    current_seq += line
            
            # Add the last sequence
            if current_name is not None:
                sequences.append((current_name, current_seq))
                
    except FileNotFoundError:
        print(f"Error: File '{fasta_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading FASTA file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return sequences


def write_fasta(sequences, output_file):
    """Write sequences to FASTA file"""
    try:
        with open(output_file, 'w') as f:
            for name, seq in sequences:
                f.write(f">{name}\n{seq}\n")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def process_fasta_batch(input_file, output_file):
    """Process FASTA file in batch mode with predict_masked"""
    print(f"Reading sequences from {input_file}...")
    sequences = parse_fasta(input_file)
    
    if not sequences:
        print("No sequences found in input file", file=sys.stderr)
        sys.exit(1)
    
    # Group sequences by antibody (VH and VL pairs)
    antibody_groups = {}
    for name, seq in sequences:
        if name.endswith('_VH'):
            ab_name = name[:-3]  # Remove '_VH'
            if ab_name not in antibody_groups:
                antibody_groups[ab_name] = {}
            antibody_groups[ab_name]['VH'] = (name, seq)
        elif name.endswith('_VL'):
            ab_name = name[:-3]  # Remove '_VL'
            if ab_name not in antibody_groups:
                antibody_groups[ab_name] = {}
            antibody_groups[ab_name]['VL'] = (name, seq)
        else:
            print(f"Warning: Sequence '{name}' does not follow the expected naming convention (should end with _VH or _VL)", file=sys.stderr)
    
    # Check for missing pairs and warn, but process all available sequences
    all_sequences_to_process = []
    for ab_name, chains in antibody_groups.items():
        missing = []
        if 'VH' not in chains:
            missing.append('VH')
        if 'VL' not in chains:
            missing.append('VL')
        
        if missing:
            print(f"Warning: Antibody '{ab_name}' is missing chain(s): {', '.join(missing)}", file=sys.stderr)
        
        # Add available chains to processing list
        if 'VH' in chains:
            all_sequences_to_process.append(('VH', chains['VH']))
        if 'VL' in chains:
            all_sequences_to_process.append(('VL', chains['VL']))
    
    if not all_sequences_to_process:
        print("No sequences found to process", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(all_sequences_to_process)} sequence(s) to process")
    
    # Process sequences with progress bar
    processed_sequences = []
    
    with tqdm(total=len(all_sequences_to_process), desc="Processing sequences", unit="sequence") as pbar:
        for chain_type, (seq_name, seq) in all_sequences_to_process:
            try:
                if chain_type == 'VH':
                    humanized = predict_masked(seq, 'H')
                else:  # VL
                    humanized = predict_masked(seq, 'L')
                processed_sequences.append((seq_name, humanized))
            except Exception as e:
                print(f"Error processing {chain_type} chain '{seq_name}': {e}", file=sys.stderr)
                processed_sequences.append((seq_name, seq))  # Keep original if error
            
            pbar.update(1)
    
    # Write output
    print(f"Writing humanized sequences to {output_file}...")
    write_fasta(processed_sequences, output_file)
    print(f"Successfully processed {len(processed_sequences)} sequences and saved to {output_file}")


def main():
    # Display logo first
    display_logo()
    
    parser = argparse.ArgumentParser(
        description="AnthroAb CLI - Antibody Humanization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Required arguments
    parser.add_argument('-i', '--input', required=True, help='Input FASTA file with sequences to humanize')
    parser.add_argument('-o', '--output', required=True, help='Output FASTA file for humanized sequences')
    parser.add_argument('--humanize', action='store_true', required=True, 
                       help='Enable humanization using predict_masked mode')
    
    # Version command
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    # Process the FASTA file
    if args.humanize:
        process_fasta_batch(args.input, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
