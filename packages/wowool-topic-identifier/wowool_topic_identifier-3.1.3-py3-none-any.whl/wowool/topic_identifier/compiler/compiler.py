import json
from wowool.error import Error
from wowool.native.core import Pipeline, Filter
from wowool.annotation import Entity, Token
from wowool.io.provider.factory import Factory
from pathlib import Path


def get_count(item):
    return item[1]


def cleanup_topic_model(model):
    return {k: v for k, v in model.items() if model[k] > 1}


def no_props(concept):
    for tk in Token.iter(concept):
        if tk.has_pos("Prop"):
            return False
    return True


def compile_model(
    file_description: Path,
    pipeline: Pipeline,
    output_file: str,
    stats: bool = False,
    existing_model: str | None = None,
):
    output_filter = Filter(["TopicCandidate"])
    if existing_model:
        try:
            with open(existing_model, "r") as f:
                tm = json.load(f)
                topic_document_count = tm["topics"]
                file_cnt = tm["nrof_docs"]
                print(f"Using existing model: {file_cnt}")
        except Exception as ex:
            print(f"Error reading existing model {existing_model}: {ex}")
            return False
    else:
        topic_document_count = {}
        file_cnt = 0
    for ip in Factory.glob(Path(file_description), "**/*.txt"):
        try:
            file_cnt += 1
            words = set()
            document = pipeline(ip.data)
            document = output_filter(document)
            words = set(concept.lemma for concept in Entity.iter(document, no_props))

            for word in words:
                if word not in topic_document_count:
                    topic_document_count[word] = 1
                else:
                    topic_document_count[word] += 1
        except Error as ex:
            print(f"Skipping {ip.id}", ex)

    if len(topic_document_count) == 0:
        return False

    topic_document_count = cleanup_topic_model(topic_document_count)
    print("## Nr of files: {}\n".format(file_cnt))
    with open(output_file, "w") as f:
        json.dump({"topics": topic_document_count, "nrof_docs": file_cnt}, f)

    if stats:
        with open("stats.md", "w") as of:
            of.write("# EyeOnText : Topic Model Tool\n")
            of.write("- Output file : {}\n".format(output_file))
            of.write("## Nr of files: {}\n".format(file_cnt))
            sorted_topics = sorted(topic_document_count.items(), key=get_count)
            of.write("|{word:30s} | {freq}\n".format(word="term", freq="freq"))
            of.write("|{word:30s} | {freq}\n".format(word="------------------------------", freq="----"))
            for item in sorted_topics:
                of.write("|{word:30s} | {freq}\n".format(word=item[0], freq=item[1]))
        print("## stats file : stats.md\n")

    return True
