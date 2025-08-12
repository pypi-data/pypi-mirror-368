#!/usr/bin/python3
import argparse
from wowool.topic_identifier.compiler import compile_model
from wowool.native.core import Pipeline, Engine
import sys
from os import pathsep
from pathlib import Path


# -------------------------------------------------------------------
# Read in Command line arguments
# Sample: python3 topic_preparation.py -l english -f movies -r movie.json
# -------------------------------------------------------------------
def parse_arguments(argv):
    """
    Build a topic model for topic identification from a given corpus folder.

    Example: toc -f ~/corpus/english -l english -o english.topic_model
    """
    parser = argparse.ArgumentParser(prog="toc", description=parse_arguments.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-f", "--file", help="input file", required=True)
    parser.add_argument("-l", "--language", required=True, help="language to build the topics pipeline ex: 'english,entity,topics'")
    parser.add_argument("-p", "--pipeline", help="pipeline to use to build the topic model")
    parser.add_argument("-o", "--output_file", required=True, help="topic model output filename, default: language.topic_model")
    parser.add_argument("--lxware", help="location of the language files")
    parser.add_argument("--stats", help="generate statistics", default=False, action="store_true")
    parser.add_argument("-m", "--existing_model", help="topic model to improve ex: english.topic_model")
    return parser.parse_args(argv)


def main(args=None):
    if args:
        args = parse_arguments(args)
    else:
        args = parse_arguments(sys.argv[1:])

    if args.language and not args.pipeline:
        language = args.language
        default_pipeline_components = [language, "entity", "topics"]
        pipeline_description = ",".join(default_pipeline_components)
    else:
        pipeline_description = args.pipeline
    output_file = args.output_file

    if args.lxware:
        engine = Engine(lxware=args.lxware)
        paths = args.lxware.split(pathsep)
    else:
        from wowool.native.core.engine import default_engine

        engine = default_engine()
        paths = engine.lxware

    pipeline = Pipeline(pipeline_description, paths=paths, engine=engine)
    if not compile_model(
        Path(args.file), pipeline=pipeline, output_file=args.output_file, stats=args.stats, existing_model=args.existing_model
    ):
        exit(-1)
    print("Model has been created:", output_file)


if __name__ == "__main__":
    main()
