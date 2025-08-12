import json
import math
from pathlib import Path
from wowool.annotation import Concept, Token
from wowool.document import Document
from wowool.document.analysis.document import AnalysisDocument
from wowool.document.document_interface import DocumentInterface
from wowool.native.core import Language, Domain, PipeLine
from wowool.native.core.engine import Engine
import copy
from wowool.topic_identifier.app_id import APP_ID
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.native.core.engine import Component
from wowool.native.core.pipeline_resolver import resolve
from wowool.annotation.sentence import Sentence


def calculate_bonus(topic):
    """
    Promote certain topics
    """
    bonus = 0
    # Promote first 2 topics in document
    if "sidx" in topic:
        bonus += 2

    # Promote longer topics
    words = topic["stem"].split()
    if len(words) > 1:
        bonus += 2

    if "relevancy" in topic:
        bonus += topic["relevancy"]

    topic["bonus"] = bonus


def organize_topic_info(sentences: list[Sentence], ignore_entities: bool):
    """
    Reads the results and organizes topics as follows

    documents = { topic_name: {'stem': value, 'freq': value, attname : value} }
    """
    topic_info = {}

    for sent_idx, sentence in enumerate(sentences):
        # we check the length of the sentence, because if the sentence is shorter than 5 tokens, the topics are not going to be promoted
        nr_token = len([t for t in Token.iter(sentence)])

        for concept in Concept.iter(sentence):
            uri = concept.uri
            if uri == "TopicCandidate":
                if ignore_entities and concept.head == "entity":
                    continue

                stem = concept.canonical
                if stem in topic_info:
                    topic_info[stem]["freq"] += 1
                else:
                    att = {"stem": stem, "freq": 1}
                    if sentence.is_header and nr_token > 4:
                        att["sidx"] = 0

                    if "relevancy" in concept.attributes:
                        if "relevancy" in att:
                            att["relevancy"] += int(concept.attributes["relevancy"][0])
                        else:
                            att["relevancy"] = int(concept.attributes["relevancy"][0])

                    topic_info[stem] = att

    return topic_info


def tfidf_calculus(current_topic, doc_nr_of_topics, model, debug=False):
    """
    Calculate tf * idf

    term frequency(t,d) = topic frequency in document / total number of topics in document
    inverse document frequency = log(total number of docs in model / term document freq in model)
    """
    # term frequency(t,d) = topic_frequency in document / total number of topics in document
    # Add bonus to frequency
    freq = current_topic["freq"] + current_topic["bonus"]
    topic_name = current_topic["stem"]
    tf = freq / doc_nr_of_topics
    if debug:
        print("docs/freq:", topic_name, model["nrof_docs"], (model["topics"][topic_name]))
    docs_per_topic = model["nrof_docs"] / (model["topics"][topic_name])
    if docs_per_topic == 1:
        docs_per_topic = 0.999
    idf = math.log(docs_per_topic)
    tfidf = tf * idf

    return tfidf


class LanguageModel:
    def __init__(self, language, analyzer, domains: list, model):
        self.language = language
        self.analyzer = None
        self.domains = domains
        self.model = model


class Model:
    def __init__(self, basic_model, ignore_entities):
        self.topic_per_document = {}
        self.model = copy.deepcopy(basic_model.model)
        self.domains = basic_model.domains
        self.analyzer = None
        self.language = basic_model.language
        self.topic_info = {}
        self.ignore_entities = ignore_entities

    def add_sentences(self, doc_id: str, sentences: list[Sentence]):
        self.topic_info[doc_id] = organize_topic_info(sentences, self.ignore_entities)

    def add(self, document: DocumentInterface) -> AnalysisDocument:
        if not isinstance(document, AnalysisDocument):
            if self.analyzer is None:
                self.analyzer = Language(self.language)
            document = self.analyzer(document)
        elif document.analysis is None:
            if self.analyzer is None:
                self.analyzer = Language(self.language)
            document = self.analyzer(document)
        for domain in self.domains:
            document = domain(document)

        sentences = document.analysis.sentences
        self.topic_info[document.id] = organize_topic_info(sentences, self.ignore_entities)
        return document

    def in_model(self, doc_id):
        return doc_id in self.topic_per_document

    def _get_topics(self, doc_id):
        if doc_id in self.topic_per_document:
            return self.topic_per_document[doc_id]
        return None

    def build(self):
        model = self.model
        # print(f"{model=}")
        documents = self.topic_info
        topic_per_document = self.topic_per_document
        for doc_id in self.topic_info:
            words = set()
            for concept in self.topic_info[doc_id]:
                words.add(concept)

            for word in words:
                # Add to model
                if word not in model["topics"]:
                    # print("unseen:", word)
                    model["topics"][word] = 1
                else:
                    # print("seen:", word, model[word])
                    model["topics"][word] += 1

            model["nrof_docs"] += len(self.topic_info)

        # ------------------------------------------
        # Final calculus - calculate tf*idf per topic in document
        # ------------------------------------------
        topic_per_document = self.topic_per_document
        for doc_id in documents:
            doc_topic_info = documents[doc_id]
            doc_nr_of_topics = len(doc_topic_info)
            topic_per_document[doc_id] = {}

            for doc_topic in doc_topic_info:
                topic = doc_topic_info[doc_topic]
                topic_name = topic["stem"]
                calculate_bonus(topic)
                tfidf = tfidf_calculus(topic, doc_nr_of_topics, model, False)
                topic_per_document[doc_id][topic_name] = tfidf


class TopicIdentifier(Component):
    """
    The model contains information about topic candidates and in how many documents in the collection they appear.
    """

    ID = APP_ID

    def __init__(
        self,
        language: str,
        count: int = 5,
        threshold: int = 0,
        topic_model: str = "",
        domains: list[str | Domain] | None = None,
        ignore_entities: bool = False,
        engine: Engine | None = None,
    ):
        """
        :param language: Language to process the input document.
        :type language: str
        :param count: The number of topics to be returned. default = 5
        :type count: str
        :param threshold: The lower threshold in percentage. [0-100]
        :type threshold: str
        :param topic_model: The reference file created with create_topic_model.
        :type topic_model: str
        :param domains: List of domains you want to process before generating topics
        :type domains: list[str, Domain]
        :param engine: The engine that will cache the domains and models.
        :type engine: wowool.native.core.Engine

        .. literalinclude:: english_topic_init.py
            :caption: topic_init.py
        """
        super(TopicIdentifier, self).__init__(engine)

        if not (0 <= threshold <= 100):
            raise ValueError("threshold argument should be from 0-100")

        if count <= 0:
            raise ValueError("count argument should bigger then 0")

        self.threshold = threshold
        self.nrof_topics = count
        self.lxware = self.engine.lxware
        self.topic_data = self.lxware
        self.lxware_paths = self.lxware
        self.language = language if language.endswith(".language") else f"{language}.language"
        self.language = Path(resolve(self.language, self.engine.lxware, engine=self.engine)[0]["filename"]).stem
        self.basic_model = self._load_model(self.language, topic_model, domains)
        self.model = None
        self.ignore_entities = ignore_entities

    def create_model(self, ignore_entities: bool = False) -> Model:
        return Model(self.basic_model, ignore_entities)

    def add_sentences(self, doc_id: str, sentences: list[Sentence]):
        if self.model is None:
            self.model = self.create_model(self.ignore_entities)
            self.model.add_sentences(doc_id, sentences)

    def add(self, input_provider: str | DocumentInterface):
        if self.model == None:
            self.model = self.create_model(self.ignore_entities)
        if isinstance(input_provider, AnalysisDocument):
            pass
        elif isinstance(input_provider, str):
            input_provider = Document.create(input_provider)
        elif isinstance(input_provider, DocumentInterface):
            input_provider = AnalysisDocument(input_provider)
        self.model.add(input_provider)

    def build(self):
        if self.model != None:
            self.model.build()

    def __call__(self, document: DocumentInterface, model: Model | None = None) -> AnalysisDocument:
        """
        Add topics to a given :ref:`Document <py_wowool_document>` object
        """
        if isinstance(document, AnalysisDocument):
            analysis_document = document
        elif isinstance(document, DocumentInterface):
            analysis_document = AnalysisDocument(document)
        else:
            raise ValueError("input type not supported.")

        diagnostics = Diagnostics()
        try:
            self.model = None
            return self.add_topics(analysis_document, diagnostics, model)
        except Exception as ex:
            diagnostics.add(Diagnostic(document.id, f"{APP_ID} : {ex}", DiagnosticType.Critical))

        if diagnostics:
            analysis_document.add_diagnostics(APP_ID, diagnostics)

        return analysis_document

    def _get_data_file_location(self, filename):
        # check domain file."
        fn = Path(filename)
        if fn.is_file():
            return str(fn)

        # try default model data. wowool.package.lware
        default_topic_data = f"{Path(__file__).parent.parent.resolve()/ 'package' / 'lxware' }"
        fn = Path(default_topic_data, filename)
        if fn.is_file():
            return str(fn)

        # try eot_root environment
        for pth in self.lxware_paths:
            fn = Path(pth, filename)
            if fn.is_file():
                return str(fn)

        raise FileNotFoundError(filename)

    def _load_model(self, language, topic_model, domains) -> LanguageModel:
        version = ""
        language, *rest = language.split("@")
        if len(rest) == 1:
            version = f"@{rest[0]}"

        topic_model_name = f"{language}{version}.topic_model" if not topic_model else topic_model
        if "topic_data" not in self.engine.data:
            self.engine.data["topic_data"] = {}

        topic_data = self.engine.data["topic_data"]

        if topic_model_name in topic_data:
            return topic_data[topic_model_name]

        topic_model_fn = self._get_data_file_location(topic_model_name)
        with open(topic_model_fn, "r") as fh:
            model = json.load(fh)

        if domains is None:
            domains_fn = []
            fn = Path(f"{language}-topics{version}.dom")
            language_topic_filename = self._get_data_file_location(fn)
            if language_topic_filename:
                domains_fn.append(language_topic_filename)
            else:
                raise ResourceWarning(f"Could not find {fn}")
        else:
            domains_fn = domains

        domain_objects = []
        for domain in domains_fn:
            if isinstance(domain, Domain):
                domain_objects.append(domain)
            else:
                pipeline = PipeLine(domain, engine=self.engine, paths=self.lxware_paths, allow_dev_version=True)
                if pipeline.domains:
                    domain_objects.append(pipeline.domains[0])
                else:
                    raise RuntimeError(f"Could not load Domain {domain}")

        topic_data[topic_model_name] = LanguageModel(language, None, domain_objects, model)
        return topic_data[topic_model_name]

    #  ----------------------------------------
    #  X    Trump            1
    #  -->> Donald Trump     0.5
    #  ----------------------------------------
    #  -->> True Fans
    #  X    True Fan Thesis Build
    #  X    Thousand of True Fans
    #  ----------------------------------------
    # Disney: 1.0
    # Disney Parks Chairman Josh D: 0.8233217397150749
    #  - Disney: 1.0
    #  - Disney Parks Chairman Josh D: 0.8233217397150749
    #  - Star Wars - themed land: 0.8233217397150749
    #  - revealed sample cabin rate: 0.6861014497625625
    #  - World - base hotel: 0.6861014497625625
    #  - Star Wars hotel: 0.6861014497625625
    #  - month of closure: 0.5488811598100499
    #  - Star Wars experience: 0.5488811598100499
    #  - number of guest: 0.5488811598100499
    #  - voyage departure date: 0.5488811598100499
    # def cleanup_filter(topic):
    #     pass

    def get_topics(self, document_id: str, sentences: list[Sentence], model: Model | None = None) -> list[dict[str, int]]:
        if model is None:
            model = self.model
        if model is None:
            self.model = self.create_model(self.ignore_entities)
            model = self.model

        if not model.in_model(document_id):
            model.add_sentences(document_id, sentences)
            model.build()

        topics = model._get_topics(document_id)
        if not topics:
            return []

        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        # take the first n topics.
        subset_topics = sorted_topics[: self.nrof_topics]

        # normalize to percentages.
        def normalize(name_relevancy, max_value: float) -> dict[str, int]:
            return {"name": name_relevancy[0], "relevancy": int(round(name_relevancy[1] / max_value, 2) * 100)}

        max_value = subset_topics[0][1]
        subset_topics = [
            item for item in list(map(lambda vp: normalize(vp, max_value), subset_topics)) if item["relevancy"] >= self.threshold
        ]
        return subset_topics

    def add_topics(self, document: AnalysisDocument, diagnostics, model: Model | None = None) -> AnalysisDocument:
        if model is None:
            model = self.model
        if model is None:
            self.model = self.create_model(self.ignore_entities)
            model = self.model

        document_id = None
        if isinstance(document, AnalysisDocument):
            document_id = document.id
        else:
            raise ValueError("input type not supported.")

        if not model.in_model(document_id):
            document = model.add(document)
            model.build()

        topics = model._get_topics(document.id)
        if not topics:
            document.add_results(self.ID, [])
            diagnostics.add(Diagnostic(document.id, f"{self.ID} No topics have been found !", DiagnosticType.Warning))
            return document

        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        # take the first n topics.
        subset_topics = sorted_topics[: self.nrof_topics]

        # normalize to percentages.
        def normalize(name_relevancy, max_value: float) -> dict[str, int]:
            return {"name": name_relevancy[0], "relevancy": int(round(name_relevancy[1] / max_value, 2) * 100)}

        max_value = subset_topics[0][1]
        subset_topics = [
            item for item in list(map(lambda vp: normalize(vp, max_value), subset_topics)) if item["relevancy"] >= self.threshold
        ]
        document.add_results(self.ID, subset_topics)
        return document
