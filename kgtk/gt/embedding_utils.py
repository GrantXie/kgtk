import logging
import re
import redis
import typing
import hashlib
import pandas as pd  # type: ignore
import numpy as np
import math
import pickle
import os
import time

from pyrallel import ParallelProcessor
from sklearn.manifold import TSNE  # type: ignore
from tqdm import tqdm  # type: ignore
from ast import literal_eval
from sentence_transformers import SentenceTransformer, SentencesDataset, LoggingHandler, losses, models  # type: ignore
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON, POST, URLENCODED  # type: ignore
from kgtk.exceptions import KGTKException


class EmbeddingVector:
    def __init__(self, model_name=None, query_server=None, cache_config: dict = None, parallel_count=1):
        self._logger = logging.getLogger(__name__)
        if model_name is None:
            self.model_name = 'bert-base-nli-mean-tokens'
        # xlnet need to be trained before using, we can't use this for now
        # elif model_name == "xlnet-base-cased":
        #     word_embedding_model = models.XLNet('xlnet-base-cased')
        # # Apply mean pooling to get one fixed sized sentence vector
        #     pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
        #                                pooling_mode_mean_tokens=True,
        #                                pooling_mode_cls_token=False,
        #                                pooling_mode_max_tokens=False)
        #     self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
        else:
            self.model_name = model_name
        self._logger.info("Using model {}".format(self.model_name))
        self.model = SentenceTransformer(self.model_name)
        # setup redis cache server
        if query_server is None or query_server == "":
            self.wikidata_server = "https://query.wikidata.org/sparql"
        else:
            self.wikidata_server = query_server
        if cache_config and cache_config.get("use_cache", False):
            host = cache_config.get("host", "dsbox01.isi.edu")
            port = cache_config.get("port", 6379)
            self.redis_server = redis.Redis(host=host, port=port, db=0)
            try:
                _ = self.redis_server.get("foo")
                self._logger.debug("Cache server {}:{} connected!".format(host, port))
            except:
                self._logger.error("Cache server {}:{} is not able to be connected! Will not use cache!".format(host, port))
                self.redis_server = None
        else:
            self.redis_server = None
        self._parallel_count = int(parallel_count)
        self._logger.debug("Running with {} processes.".format(parallel_count))
        self.qnodes_descriptions = dict()
        self.vectors_map = dict()
        self.property_labels_dict = dict()
        self.q_node_to_label = dict()
        self.node_labels = dict()
        self.vectors_2D = None
        self.vector_dump_file = None
        self.gt_nodes = set()
        self.candidates = defaultdict(dict)
        self.metadata = []
        self.gt_indexes = set()
        self.input_format = ""
        self.token_pattern = re.compile(r"(?u)\b\w\w+\b")

    def get_sentences_embedding(self, sentences: typing.List[str], qnodes: typing.List[str]):
        """
            transform a list of sentences to embedding vectors
        """

        if self.redis_server is not None:
            sentence_embeddings = []
            for each_node, each_sentence in zip(qnodes, sentences):
                query_cache_key = each_node + each_sentence
                if self.model_name != "bert-base-wikipedia-sections-mean-tokens":
                    query_cache_key += self.model_name
                cache_res = self.redis_server.get(query_cache_key)
                if cache_res is not None:
                    sentence_embeddings.append(literal_eval(cache_res.decode("utf-8")))
                    # self._logger.error("{} hit!".format(each_node+each_sentence))
                else:
                    each_embedding = self.model.encode([each_sentence], show_progress_bar=False)
                    sentence_embeddings.extend(each_embedding)
                    self.redis_server.set(query_cache_key, str(each_embedding[0].tolist()))
        else:
            sentence_embeddings = self.model.encode(sentences, show_progress_bar=False)
        return sentence_embeddings

    def send_sparql_query(self, query_body: str):
        """
            a simple wrap to send the query and return the returned results
        """
        qm = SPARQLWrapper(self.wikidata_server)
        qm.setReturnFormat(JSON)
        qm.setMethod(POST)
        qm.setRequestMethod(URLENCODED)
        self._logger.debug("Sent query is:")
        self._logger.debug(str(query_body))
        qm.setQuery(query_body)
        try:
            results = qm.query().convert()['results']['bindings']
            return results
        except Exception as e:
            error_message = ("Sending Sparql query to {} failed!".format(self.wikidata_server))
            self._logger.error(error_message)
            self._logger.debug(e, exc_info=True)
            raise KGTKException(error_message)

    def _get_labels(self, nodes: typing.List[str]):
        query_nodes = " ".join(["wd:{}".format(each) for each in nodes])
        query = """
        select ?item ?nodeLabel
        where { 
          values ?item {""" + query_nodes + """}
          ?item rdfs:label ?nodeLabel.
          FILTER(LANG(?nodeLabel) = "en").
        }
        """
        results2 = self.send_sparql_query(query)
        for each_res in results2:
            node_id = each_res['item']['value'].split("/")[-1]
            value = each_res['nodeLabel']['value']
            self.node_labels[node_id] = value

    def _get_labels_and_descriptions(self, query_qnodes: str, need_find_label: bool, need_find_description: bool):
        query_body = """
            select ?item ?itemDescription ?itemLabel
            where {
              values ?item {""" + query_qnodes + """ }
                 SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """
        results = self.send_sparql_query(query_body)
        for each in results:
            each_node = each['item']['value'].split("/")[-1]
            if 'itemDescription' in each:
                description = each['itemDescription']['value']
            else:
                description = ""
            if "itemLabel" in each:
                label = each['itemLabel']['value']
            else:
                label = ""
            if need_find_label:
                self.candidates[each_node]["label_properties"] = [label]
            if need_find_description:
                self.candidates[each_node]["description_properties"] = [description]

    def _get_property_values(self, query_qnodes, query_part_names, query_part_properties):
        used_p_node_ids = set()
        for part_name, part in zip(query_part_names, query_part_properties):
            if part_name == "isa_properties":
                self._get_labels(part)
            for i, each in enumerate(part):
                if each not in {"label", "description", "all"}:
                    query_body2 = """
                    select ?item ?eachPropertyLabel
                    where {{
                      values ?item {{{all_nodes}}}
                    ?item wdt:{qnode} ?eachProperty.
                      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                    }}
                    """.format(all_nodes=query_qnodes, qnode=each)
                    results2 = self.send_sparql_query(query_body2)

                    for each_res in results2:
                        node_id = each_res['item']['value'].split("/")[-1]
                        value = each_res['eachPropertyLabel']['value']
                        if part_name == "isa_properties" and self.node_labels[each].endswith("of"):
                            value = self.node_labels[each] + "||" + value
                        used_p_node_ids.add(node_id)
                        if part_name in self.candidates[node_id]:
                            self.candidates[node_id][part_name].add(value)
                        else:
                            self.candidates[node_id][part_name] = {value}
        return used_p_node_ids

    def _get_all_properties(self, query_qnodes, used_p_node_ids, properties_list):
        has_properties_set = set(properties_list[3])
        query_body3 = """
                            select DISTINCT ?item ?p_entity ?p_entityLabel
                            where {
                              values ?item {""" + query_qnodes + """}
                              ?item ?p ?o.
                              FILTER regex(str(?p), "^http://www.wikidata.org/prop/P", "i")
                              BIND (IRI(REPLACE(STR(?p), "http://www.wikidata.org/prop", "http://www.wikidata.org/entity")) AS ?p_entity) .
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                            }
                        """
        results3 = self.send_sparql_query(query_body3)
        for each in results3:
            node_name = each['item']['value'].split("/")[-1]
            p_node_id = each['p_entity']['value'].split("/")[-1]
            p_node_label = each['p_entityLabel']['value']
            if p_node_id not in used_p_node_ids:
                if properties_list[3] == ["all"] or p_node_id in has_properties_set:
                    if "has_properties" in self.candidates[node_name]:
                        self.candidates[node_name]["has_properties"].add(p_node_label)
                    else:
                        self.candidates[node_name]["has_properties"] = {p_node_label}

    def get_item_description(self, qnodes: typing.List[str] = None, target_properties: dict = {}):
        """
            use sparql query to get the descriptions of given Q nodes
        """
        if qnodes is None:
            qnodes = self.candidates
        if "all" in target_properties:
            find_all_properties = True
        else:
            find_all_properties = False
        properties_list = [[] for _ in range(4)]
        names = ["labels", "descriptions", "isa_properties", "has_properties"]
        for k, v in target_properties.items():
            if v == "label_properties":
                properties_list[0].append(k)
            elif v == "description_properties":
                properties_list[1].append(k)
            elif v == "isa_properties":
                properties_list[2].append(k)
            elif v == "has_properties":
                properties_list[3].append(k)

        hash_generator = hashlib.md5()
        hash_generator.update(str(properties_list).encode('utf-8'))
        properties_list_hash = "||" + str(hash_generator.hexdigest())

        sentences_cache_dict = {}
        if self.redis_server is not None:
            for each_node in qnodes:
                cache_key = each_node + properties_list_hash
                cache_res = self.redis_server.get(cache_key)
                self._logger.debug("Cached key is: {}".format(cache_key))
                if cache_res is not None:
                    self._logger.debug("Cache hitted {}".format(cache_key))
                    sentences_cache_dict[each_node] = cache_res.decode("utf-8")

        self._logger.debug("Cached for those nodes {} / {}".format(len(sentences_cache_dict), len(qnodes)))
        self._logger.debug(str(set(sentences_cache_dict.keys())))
        self._logger.debug("Need run query for those nodes {} / {}:".format(len(qnodes) - len(sentences_cache_dict), len(qnodes)))

        # we do not need to get those node again
        if len(sentences_cache_dict) > 0:
            qnodes = set(qnodes) - set(sentences_cache_dict.keys())
        self._logger.debug(str(qnodes))

        # only need to do query when we still have remained nodes
        if len(qnodes) > 0:
            need_find_label = "label" in properties_list[0]
            need_find_description = "description" in properties_list[1]
            query_qnodes = ""
            for each in qnodes:
                query_qnodes += "wd:{} ".format(each)

            # this is used to get corresponding labels / descriptions
            if need_find_label or need_find_description:
                self._get_labels_and_descriptions(query_qnodes, need_find_label, need_find_description)

            if len(properties_list[3]) > len(qnodes):
                # in this condition, we have too many properties need to be queried, it will waste time
                # query to get all properties then filtering would save more times
                find_all_properties = True
                query_part2_names = names[:3]
                query_part2_properties = properties_list[:3]
            else:
                query_part2_names = names
                query_part2_properties = properties_list
            # this is used to get corresponding labels of properties values
            used_p_node_ids = self._get_property_values(query_qnodes, query_part2_names, query_part2_properties)

            # if need get all properties, we need to run extra query
            if find_all_properties:
                self._get_all_properties(query_qnodes, used_p_node_ids, properties_list)

        for each_node_id in qnodes:
            each_sentence = self.attribute_to_sentence(self.candidates[each_node_id], each_node_id)
            self.candidates[each_node_id]["sentence"] = each_sentence
            # add to cache
            if self.redis_server is not None:
                response = self.redis_server.set(each_node_id + properties_list_hash, each_sentence)
                if response:
                    self._logger.debug("Pushed cache for {} success.".format(each_node_id + properties_list_hash))

        for each_node_id, sentence in sentences_cache_dict.items():
            self.candidates[each_node_id]["sentence"] = sentence

    def _process_one(self, args):
        """
        one process for multiprocess calling
        :param args:
        :return:
        """
        node_id = args["node_id"]
        each_node_attributes = args["attribute"]
        concated_sentence = self.attribute_to_sentence(each_node_attributes, node_id)
        vectors = self.get_sentences_embedding([concated_sentence], [node_id])[0]
        return {"v_" + node_id: vectors, "c_" + node_id: each_node_attributes}

    def _multiprocess_collector(self, data):
        for k, v in data.items():
            if k.startswith("v_"):
                k = k.replace("v_", "")
                self.vectors_map[k] = v
            else:
                k = k.replace("c_", "")
                self.candidates[k] = v

    def read_input(self, file_path: str, skip_nodes_set: set = None,
                   input_format: str = "kgtk_format", target_properties: dict = {},
                   property_labels_dict: dict = {}, black_list_set: set = set()
                   ):
        """
            load the input candidates files
        """
        self.property_labels_dict = property_labels_dict

        if input_format == "test_format":
            self.input_format = input_format
            input_df = pd.read_csv(file_path)
            gt = {}
            count = 0
            if "GT_kg_id" in input_df.columns:
                gt_column_id = "GT_kg_id"
            elif "kg_id" in input_df.columns:
                gt_column_id = "kg_id"
            else:
                raise KGTKException("Can't find ground truth id column! It should either named as `GT_kg_id` or `kg_id`")

            for _, each in input_df.iterrows():
                if isinstance(each["candidates"], str):
                    temp = str(each['candidates']).split("|")
                elif each['candidates'] is np.nan or math.isnan(each['candidates']):
                    temp = []

                to_remove_q = set()
                if each[gt_column_id] is np.nan:
                    self._logger.warning("Ignore NaN gt value form {}".format(str(each)))
                    each[gt_column_id] = ""
                gt_nodes = each[gt_column_id].split(" ")
                label = str(each["label"])
                if len(gt_nodes) == 0:
                    self._logger.error("Skip a row with no ground truth node given: as {}".format(str(each)))
                    continue
                if label == "":
                    self._logger.error("Skip a row with no label given: as {}".format(str(each)))
                    continue
                temp.extend(gt_nodes)

                for each_q in temp:
                    self.q_node_to_label[each_q] = label
                    if skip_nodes_set is not None and each_q in skip_nodes_set:
                        to_remove_q.add(each_q)
                temp = set(temp) - to_remove_q
                count += len(temp)
                self.gt_nodes.add(each[gt_column_id])
                self.get_item_description(temp, target_properties)

            self._logger.info("Totally {} rows with {} candidates loaded.".format(str(len(gt)), str(count)))

        elif input_format == "kgtk_format":
            # assume the input edge file is sorted
            if "all" in target_properties:
                _ = target_properties.pop("all")
                add_all_properties = True
            else:
                add_all_properties = False

            self.input_format = input_format
            with open(file_path, "r") as f:
                # get header
                headers = f.readline().replace("\n", "").split("\t")
                if len(headers) < 3:
                    raise KGTKException(
                        "No enough columns found on given input file. Only {} columns given but at least 3 needed.".format(
                            len(headers)))
                elif "node" in headers and "property" in headers and "value" in headers:
                    column_references = {"node": headers.index("node"),
                                         "property": headers.index("property"),
                                         "value": headers.index("value")}
                elif len(headers) == 3:
                    column_references = {"node": 0,
                                         "property": 1,
                                         "value": 2}
                else:
                    missing_column = {"node", "property", "value"} - set(headers)
                    raise KGTKException("Missing column {}".format(missing_column))
                self._logger.debug("column index information: ")
                self._logger.debug(str(column_references))
                # read contents
                each_node_attributes = {"has_properties": [], "isa_properties": [], "label_properties": [],
                                        "description_properties": []}
                current_process_node_id = None

                if self._parallel_count > 1:
                    pp = ParallelProcessor(self._parallel_count, self._process_one, collector=self._multiprocess_collector)
                    pp.start()

                for each_line in f:
                    each_line = each_line.replace("\n", "").split("\t")
                    node_id = each_line[column_references["node"]]
                    node_property = each_line[column_references["property"]]
                    node_value = each_line[column_references["value"]]
                    # remove @ mark
                    if "@" in node_value and node_value[0] != "@":
                        node_value_org = node_value
                        node_value = node_value[:node_value.index("@")]

                    # remove extra double quote " and single quote '
                    if node_value[0] == '"' and node_value[-1] == '"':
                        node_value = node_value[1:-1]
                    if node_value[0] == "'" and node_value[-1] == "'":
                        node_value = node_value[1:-1]

                    if current_process_node_id != node_id:
                        if current_process_node_id is None:
                            current_process_node_id = node_id
                        else:
                            # if we get to next id, concate all properties into one sentence to represent the Q node

                            # for multi process
                            if self._parallel_count > 1:
                                each_arg = {"node_id": current_process_node_id, "attribute": each_node_attributes}
                                pp.add_task(each_arg)
                            # for single process
                            else:
                                concated_sentence = self.attribute_to_sentence(each_node_attributes, current_process_node_id)
                                each_node_attributes["sentence"] = concated_sentence
                                self.candidates[current_process_node_id] = each_node_attributes

                            # after write down finish, we can cleaer and start parsing next one
                            each_node_attributes = {"has_properties": [], "isa_properties": [], "label_properties": [],
                                                    "description_properties": []}
                            # update to new id
                            current_process_node_id = node_id

                    if node_property in target_properties:
                        each_node_attributes[target_properties[node_property]].append(node_value)
                    if add_all_properties and each_line[column_references["value"]][0] == "P":
                        each_node_attributes["has_properties"].append(node_value)

                # close multiprocess pool
                if self._parallel_count > 1:
                    pp.task_done()
                    pp.join()
        else:
            raise KGTKException("Unkonwn input format {}".format(input_format))

        self._logger.info("Totally {} Q nodes loaded.".format(len(self.candidates)))
        self.vector_dump_file = "dump_vectors_{}_{}.pkl".format(file_path[:file_path.rfind(".")], self.model_name)
        # self._logger.debug("The cache file name will be {}".format(self.vector_dump_file))

    def get_real_label_name(self, node):
        if node in self.property_labels_dict:
            return self.property_labels_dict[node]
        else:
            return node

    def attribute_to_sentence(self, attribute_dict: dict, node_id=None):
        concated_sentence = ""
        have_isa_properties = False
        # sort the properties to ensure the sentence always same
        attribute_dict = {key: sorted(list(value)) for key, value in attribute_dict.items() if len(value) > 0}
        if "label_properties" in attribute_dict and len(attribute_dict["label_properties"]) > 0:
            concated_sentence += self.get_real_label_name(attribute_dict["label_properties"][0])
        if "description_properties" in attribute_dict and len(attribute_dict["description_properties"]) > 0:
            if concated_sentence != "" and attribute_dict["description_properties"][0] != "":
                concated_sentence += ", "
            concated_sentence += self.get_real_label_name(attribute_dict["description_properties"][0])
        if "isa_properties" in attribute_dict and len(attribute_dict["isa_properties"]) > 0:
            have_isa_properties = True
            temp = ""
            for each in attribute_dict["isa_properties"]:
                each = self.get_real_label_name(each)
                if "||" in each:
                    if "instance of" in each:
                        each = each.split("||")[1]
                    else:
                        each = each.replace("||", " ")
                temp += each + ", "
            if concated_sentence != "" and temp != "":
                concated_sentence += " is a "
            elif concated_sentence == "":
                concated_sentence += "It is a "
            concated_sentence += temp[:-2]
        if "has_properties" in attribute_dict and len(attribute_dict["has_properties"]) > 0:
            temp = [self.get_real_label_name(each) for each in attribute_dict["has_properties"]]
            if concated_sentence != "" and temp[0] != "":
                if have_isa_properties:
                    concated_sentence += ", and has "
                else:
                    concated_sentence += " has "
            elif temp[0] != "":
                concated_sentence += "It has "
            concated_sentence += " and ".join(temp)
        self._logger.debug("Transform node {} --> {}".format(node_id, concated_sentence))
        return concated_sentence

    def get_vectors(self):
        """
            main function to get the vector representations of the descriptions
        """
        if self._parallel_count == 1:
            start_all = time.time()
            self._logger.info("Now generating embedding vector.")
            for q_node, each_item in tqdm(self.candidates.items()):
                # do process for each row(one target)
                sentence = each_item["sentence"]
                if isinstance(sentence, bytes):
                    sentence = sentence.decode("utf-8")
                vectors = self.get_sentences_embedding([sentence], [q_node])
                self.vectors_map[q_node] = vectors[0]
            self._logger.info("Totally used {} seconds.".format(str(time.time() - start_all)))
        else:
            # Skip get vector function because we already get them
            pass

    def dump_vectors(self, file_name, type_=None):
        if file_name.endswith(".pkl"):
            file_name = file_name.replace(".pkl", "")
        if type_ == "2D":
            with open(file_name + ".pkl", "wb") as f:
                pickle.dump(self.vectors_2D, f)
            dimension = len(self.vectors_2D[0])
            with open(file_name + ".tsv", "w") as f:
                for each in self.vectors_2D:
                    for i, each_val in enumerate(each):
                        _ = f.write(str(each_val))
                        if i != dimension - 1:
                            _ = f.write("\t")
                    _ = f.write("\n")
        elif type_ == "metadata":
            with open(file_name + "_metadata.tsv", "w") as f:
                for each in self.metadata:
                    _ = f.write(each + "\n")
        else:
            with open(file_name + ".pkl", "wb") as f:
                pickle.dump(self.vectors_map, f)
            with open(file_name + ".tsv", "w") as f:
                for each in self.vectors_map.values():
                    for i in each:
                        _ = f.write(str(i) + "\t")
                    _ = f.write("\n")

    def print_vector(self, vectors, output_properties: str = "text_embedding", output_format="kgtk_format"):
        if output_format == "kgtk_format":
            print("node\tproperty\tvalue\n", end="")
            if self.input_format == "kgtk_format":
                for i, each_vector in enumerate(vectors):
                    print(str(list(self.candidates.keys())[i]) + "\t", end="")
                    print(output_properties + "\t", end="")
                    for j, each_dimension in enumerate(each_vector):
                        if j != len(each_vector) - 1:
                            print(str(each_dimension) + ",", end="")
                        else:
                            print(str(each_dimension) + "\n", end="")
            elif self.input_format == "test_format":
                all_nodes = list(self.vectors_map.keys())
                for i, each_vector in enumerate(vectors):
                    print(all_nodes[i] + "\t", end="")
                    print(output_properties + "\t", end="")
                    for j, each_dimension in enumerate(each_vector):
                        if j != len(each_vector) - 1:
                            print(str(each_dimension) + ",", end="")
                        else:
                            print(str(each_dimension) + "\n", end="")

        elif output_format == "tsv_format":
            for each_vector in vectors:
                for i, each_dimension in enumerate(each_vector):
                    if i != len(each_vector) - 1:
                        print(str(each_dimension) + "\t", end="")
                    else:
                        print(str(each_dimension) + "\n", end="")

    def plot_result(self, output_properties={}, input_format="kgtk_format",
                    output_uri: str = "", output_format="kgtk_format",
                    run_TSNE=True
                    ):
        """
            transfer the vectors to lower dimension so that we can plot
            Then save the 2D vector file for further purpose
        """
        self.vectors_map = {k: v for k, v in sorted(self.vectors_map.items(), key=lambda item: item[0], reverse=True)}
        vectors = list(self.vectors_map.values())
        # use TSNE to reduce dimension
        if run_TSNE:
            self._logger.warning("Start running TSNE to reduce dimension. It will take a long time.")
            start = time.time()
            self.vectors_2D = TSNE(n_components=2, random_state=0).fit_transform(vectors)
            self._logger.info("Totally used {} seconds.".format(time.time() - start))

        if input_format == "test_format":
            gt_indexes = set()
            vector_map_keys = list(self.vectors_map.keys())
            for each_node in self.gt_nodes:
                gt_indexes.add(vector_map_keys.index(each_node))

            self.metadata.append("Q_nodes\tType\tLabel\tDescription")
            for i, each in enumerate(self.vectors_map.keys()):
                label = self.q_node_to_label[each]
                description = self.candidates[each]["sentence"]
                if i in gt_indexes:
                    self.metadata.append("{}\tground_truth_node\t{}\t{}".format(each, label, description))
                else:
                    self.metadata.append("{}\tcandidates\t{}\t{}".format(each, label, description))
            self.gt_indexes = gt_indexes

        elif input_format == "kgtk_format":
            if len(output_properties.get("metatada_properties", [])) == 0:
                for k, v in self.candidates.items():
                    label = v.get("label_properties", "")
                    if len(label) > 0 and isinstance(label, list):
                        label = label[0]
                    description = v.get("description_properties", "")
                    if len(description) > 0 and isinstance(description, list):
                        description = description[0]
                    self.metadata.append("{}\t\t{}\t{}".format(k, label, description))
            else:
                required_properties = output_properties["metatada_properties"]
                self.metadata.append("node\t" + "\t".join(required_properties))
                for k, v in self.candidates.items():
                    each_metadata = k + "\t"
                    for each in required_properties:
                        each_metadata += v.get(each, " ") + "\t"
                    self.metadata.append(each_metadata)

        metadata_output_path = os.path.join(output_uri, self.vector_dump_file.split("/")[-1])
        if run_TSNE:
            self.print_vector(self.vectors_2D, output_properties.get("output_properties"), output_format)
        else:
            self.print_vector(vectors, output_properties.get("output_properties"), output_format)
        if output_uri != "none":
            self.dump_vectors(metadata_output_path, "metadata")

    def evaluate_result(self):
        """
        for the ground truth nodes, evaluate the average distance to the centroid, the lower the average distance,
        the better clustering results should be
        """
        centroid = None
        gt_nodes_vectors = []
        if len(self.gt_indexes) == 0:
            points = set(range(len(self.vectors_map)))
        else:
            points = self.gt_indexes
        for i, each in enumerate(self.vectors_map.keys()):
            if i in points:
                if centroid is None:
                    centroid = np.array(self.vectors_map[each])
                else:
                    centroid += np.array(self.vectors_map[each])
                gt_nodes_vectors.append(self.vectors_map[each])
        centroid = centroid / len(points)

        distance_sum = 0
        for each in gt_nodes_vectors:
            distance_sum += self.calculate_distance(each, centroid)
        self._logger.info("The average distance for the ground truth nodes to centroid is {}".format(distance_sum / len(points)))

    @staticmethod
    def calculate_distance(a, b):
        if len(a) != len(b):
            raise KGTKException("Vector dimension are different!")
        dist = 0
        for v1, v2 in zip(a, b):
            dist += (v1 - v2) ** 2
        dist = dist ** 0.5
        return dist
