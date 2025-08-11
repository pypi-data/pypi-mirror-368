"""
This algorithm proposes a new paradigm in language model architecture, aiming to revolutionize natural language processing through direct weights adjustment and automatic parameter configuration.
The Hur-Model is a development module that implements this concept, enabling the training, retraining, tuning, and inference of language models in a groundbreaking way.
It reduces dependence on backpropagation through an initial weight adjustment using a HurNet network and accelerates model parameterization through optimization calculations and self-configuration.
This code was architected, developed, and programmed by Ben-Hur Varriano for Sapiens Technology®️.
Any use, modification, disclosure, or public commentary without prior authorization from Sapiens Technology®️ will be subject to legal action by our legal team.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
class HurModel:
    def __init__(self, embedding_dim=None, block_size=None, batch_size=None, number_heads=None, number_layers=None, dropout=None, learning_rate=None, eval_interval=None, epochs=None, use_bit_net_quantization=None, device=None):
        self.EMBEDDING_DIM = max((1, int(embedding_dim))) if type(embedding_dim) in (bool, int, float) else None
        self.BLOCK_SIZE = max((1, int(block_size))) if type(block_size) in (bool, int, float) else None
        self.BATCH_SIZE = max((1, int(batch_size))) if type(batch_size) in (bool, int, float) else None
        self.NUMBER_HEADS = max((1, int(number_heads))) if type(number_heads) in (bool, int, float) else None
        self.NUMBER_LAYERS = max((1, int(number_layers))) if type(number_layers) in (bool, int, float) else None
        self.DROPOUT = max((0, float(dropout))) if type(dropout) in (bool, int, float) else 0.1
        self.LEARNING_RATE = max((0, float(learning_rate))) if type(learning_rate) in (bool, int, float) else 3e-4
        self.EVAL_INTERVAL = max((1, int(eval_interval))) if type(eval_interval) in (bool, int, float) else None
        self.EPOCHS = max((1, int(epochs))) if type(epochs) in (bool, int, float) else None
        self.USE_BIT_NET_QUANTIZATION = bool(use_bit_net_quantization) if type(use_bit_net_quantization) in (bool, int, float) else False
        from hurnet_torch._device_detection import DeviceDetection
        self.DEVICE = DeviceDetection().getDevice(device=device)
        self.END_TAG, self.SYSTEM_TAG, self.USER_TAG, self.ASSISTANT_TAG = '', 'System:', 'User:', 'Assistant:'
        self.TOKENS_NUMBER = 0
        self.PARAMETERS_NUMBER = 0
        self.PERPLEXITY = 100.0
        self.WEIGHT_DECAY = None
        self.USER_ID = 0
        self.HURNET_EMBEDDING_LENGTH = 25
        self.HURNET_DIVISION_METHOD = 0
        self.INCLUDE_VOCABULARY_IN_MODEL = True
        self.USE_SCHEDULER = False
        self.HURNET_DTYPE = None
        self.SHOW_ERROR = False
        self.SHOW_ERROR_DETAILS = False
        import warnings; warnings.filterwarnings('ignore')
        from hurnet_torch import HurNetTorch, HurNetTransformer, TransformerHurNet
        from sapiens_infinite_context_window import SapiensInfiniteContextWindow
        from sapiens_generalization import SapiensGeneralization
        from sapiens_tokenizer import SapiensTokenizer
        from sapiens_embedding import SapiensEmbedding
        from sapiens_attention import SapiensAttention
        if not self.HURNET_DTYPE:
            from torch import float32
            self.HURNET_DTYPE = float32
        self.__DeviceDetection = DeviceDetection
        self.__HurNet = HurNetTorch
        self.__HurNetTorch = HurNetTorch(device=self.DEVICE, dtype=self.HURNET_DTYPE, show_errors=False)
        self.__HurNetTransformer = HurNetTransformer
        self.__TransformerHurNet = TransformerHurNet
        self.__sapiens_infinite_context_window = SapiensInfiniteContextWindow()
        self.__sapiens_generalization = SapiensGeneralization()
        self.__sapiens_tokenizer = SapiensTokenizer()
        self.__sapiens_embedding = SapiensEmbedding()
        self.__SapiensAttention = SapiensAttention
        from torch.utils.data import IterableDataset, Dataset, DataLoader
        from torch import tensor, triu, ones, int64, no_grad, multinomial, cat, cuda, optim, zeros, float16, save, load
        from torch.nn import Module, Parameter, Dropout, Embedding, TransformerDecoder, TransformerDecoderLayer, Linear, functional as Function, utils
        from os.path import join, exists, getsize, isdir, basename
        from tempfile import gettempdir
        from scn import SCN
        from math import sqrt, exp
        from time import sleep, time
        from tqdm import tqdm
        from random import sample
        from statistics import mean
        from urllib.request import urlopen
        from json import loads, load as json_load, dump
        from inspect import signature
        from ijson import items
        from datetime import datetime
        from requests import head, get
        from torch.optim.lr_scheduler import StepLR as scheduled
        from io import TextIOWrapper
        from os import remove, path as os_path, makedirs as os_makedirs
        from random import randint
        from pathlib import Path
        from gc import collect
        from torch.autograd import Function as autograd_function
        self.__error_position = 1
        self.__string = ''
        self.__IterableDataset = IterableDataset
        self.__attention_words = []
        self.__tensor = tensor
        self.__Dataset = Dataset
        self.__Module = Module
        self.__Parameter = Parameter
        self.__Dropout = Dropout
        self.__Embedding = Embedding
        self.__TransformerDecoder = TransformerDecoder
        self.__TransformerDecoderLayer = TransformerDecoderLayer
        self.__Linear = Linear
        self.__triu = triu
        self.__ones = ones
        self.__join = join
        self.__gettempdir = gettempdir
        self.__tokenizer = 'gpt-4'
        self.__token_to_index = {}
        self.__SCN = SCN(show_errors=False)
        self.__exists = exists
        self.__sqrt = sqrt
        self.__fine_tuning = []
        self.__model = None
        self.__hurnet_parameters = {}
        self.__generalization_direction = -1
        self.__output_indexing = []
        self.__hurnet_fit_configuration = []
        self.__interval = 0
        self.__tokens_count = 0
        self.__sleep = sleep
        self.__encode = None
        self.__int64 = int64
        self.__no_grad = no_grad
        self.__Function = Function
        self.__multinomial = multinomial
        self.__cat = cat
        self.__decode = None
        self.__exp = exp
        self.__cuda = cuda
        self.__inputs_targets = []
        self.__tqdm = tqdm
        self.__sample = sample
        self.__optimizer = None
        self.__utils = utils
        self.__scheduler = None
        self.__mean = mean
        self.__prompts = []
        self.__answers = []
        self.__encoding_length = 500
        self.__time = time
        self.__urlopen = urlopen
        self.__loads = loads
        self.__signature = signature
        self.__items = items
        self.__quantization_epsilon = 1e-5
        self.__datetime = datetime
        self.__head = head
        self.__get = get
        self.__getsize = getsize
        self.__adjustment_data = False
        self.__json_load = json_load
        self.__loaded_vocabulary = False
        self.__vocabulary_size = 0
        self.__index_to_token = {}
        self.__pad_token_id = [0]
        self.__DataLoader = DataLoader
        self.__optim = optim
        self.SCHEDULED = scheduled
        self.__loaded_model = False
        self.__zeros = zeros
        self.__hidden_layers = []
        self.__experts_training = False
        self.__quantization = False
        self.__train = False
        self.__infinite_context_window = 0
        self.__quantization_type = 'FP32'
        self.__date_and_time_of_creation = ''
        self.__date_and_time_of_the_last_update = ''
        self.__experts = []
        self.__TextIOWrapper = TextIOWrapper
        self.__dump = dump
        self.__float16 = float16
        self.__remove = remove
        self.__randint = randint
        self.__attention_list = []
        self.__checkpoint = {}
        self.__add_semantic_fit = False
        self.__add_hur_net_fit = False
        self.__input_layer = []
        self.__output_layer = []
        self.__os_path = os_path
        self.__os_makedirs = os_makedirs
        self.__save = save
        self.__load = load
        self.__isdir = isdir
        self.__Path = Path
        self.__collect = collect
        self.__basename = basename
        class AbsoluteMeanQuantizationFunction(autograd_function):
            @staticmethod
            def forward(context=None, weights=[], epsilon=1):
                gamma = weights.abs().mean()
                context.save_for_backward(gamma)
                context.eps = epsilon
                return weights.div(gamma + epsilon).round().clamp(-1, 1)
            @staticmethod
            def backward(context, output_gradient=[]): return output_gradient, None
        class TextIterableDataset(self.__IterableDataset):
            def __init__(self, dataset_path='', string='', coding_function=None, tensor_function=None, int_dtype=None, block_size=1, end_tag=None):
                self.__dataset_path, self.__string = str(dataset_path).strip(), str(string).strip()
                self.__coding_function, self.__tensor_function, self.__int_dtype = coding_function, tensor_function, int_dtype
                self.BLOCK_SIZE = max((1, int(block_size))) if type(block_size) in (bool, int, float) else 1
                self.__attention_words = []
            def __iter__(self):
                from requests import get
                from sapiens_attention import SapiensAttention
                sapiens_attention = SapiensAttention()
                buffer, maximum_words, accumulation = [], 5, ''
                def _open_stream(dataset_path=''):
                    if dataset_path.startswith(('https://', 'http://', 'www.')):
                        response = get(dataset_path, stream=True)
                        response.raise_for_status()
                        return response.iter_lines(decode_unicode=True)
                    else: return open(dataset_path, 'r', encoding='utf-8')
                if self.__dataset_path:
                    file = _open_stream(dataset_path=self.__dataset_path)
                    for chunk in file:
                        chunk = rf'{chunk}'
                        buffer.extend(self.__coding_function(chunk))
                        if len(self.__attention_words) < maximum_words:
                            accumulation += chr(32)+chunk
                            attention_words = sapiens_attention.get_attention_words(text=accumulation.strip(), maximum_length=maximum_words)
                            for item in attention_words:
                                length_of_attention_words = len(self.__attention_words)
                                if length_of_attention_words < maximum_words and item not in self.__attention_words: self.__attention_words.append(item)
                                elif length_of_attention_words >= maximum_words: break
                        else: accumulation = ''
                        while len(buffer) > self.BLOCK_SIZE:
                            sequence, buffer = buffer[:self.BLOCK_SIZE + 1], buffer[1:]
                            yield (self.__tensor_function(sequence[:-1], dtype=self.__int_dtype), self.__tensor_function(sequence[1:], dtype=self.__int_dtype))
                if self.__string:
                    buffer.extend(self.__coding_function('\n\n'+self.__string))
                    def _read_start_of_string(string='', maximum_words=10):
                        word, words = '', []
                        for character in string:
                            if character.isspace():
                                if word:
                                    words.append(word)
                                    if len(words) >= maximum_words: break
                                    word = ''
                            else: word += character
                        if word and len(words) < maximum_words: words.append(word)
                        return ' '.join(words)
                    accumulation = _read_start_of_string(string=self.__string, maximum_words=maximum_words*10)
                    attention_words = sapiens_attention.get_attention_words(text=accumulation.strip(), maximum_length=maximum_words)
                    for item in attention_words:
                        if item not in self.__attention_words: self.__attention_words.append(item)
                    while len(buffer) > self.BLOCK_SIZE:
                        sequence, buffer = buffer[:self.BLOCK_SIZE + 1], buffer[1:]
                        yield (self.__tensor_function(sequence[:-1], dtype=self.__int_dtype), self.__tensor_function(sequence[1:], dtype=self.__int_dtype))
            def get_attention_words(self): return self.__attention_words
        class JSONIterableDataset(self.__IterableDataset):
            def __init__(self, dataset_path='', string='', coding_function=None, tensor_function=None, int_dtype=None, block_size=1, end_tag=None):
                self.__dataset_path, self.__string = str(dataset_path).strip(), str(string).strip()
                self.__coding_function, self.__tensor_function, self.__int_dtype = coding_function, tensor_function, int_dtype
                self.BLOCK_SIZE, self.END_TAG = max((1, int(block_size))) if type(block_size) in (bool, int, float) else 1, end_tag
                if not self.END_TAG: self.END_TAG = '<|end|>'
                self.__attention_words = []
            def __iter__(self):
                from requests import get
                from sapiens_attention import SapiensAttention
                sapiens_attention = SapiensAttention()
                buffer, maximum_words, accumulation = [], 5, ''
                def _open_stream(dataset_path=''):
                    if dataset_path.startswith(('https://', 'http://', 'www.')):
                        response = get(dataset_path, stream=True)
                        response.raise_for_status()
                        return response.iter_lines(decode_unicode=True)
                    else: return open(dataset_path, 'r', encoding='utf-8')
                stream = _open_stream(dataset_path=self.__dataset_path)
                if isinstance(stream, list) or hasattr(stream, '__iter__'):
                    from io import StringIO
                    content = '\n'.join(stream) if isinstance(stream, list) else '\n'.join(list(stream))
                    stream = StringIO(content)
                with stream as file:
                    from ijson import items
                    for item in items(file, 'data.item'):
                        if not isinstance(item, dict) or len(item) < 1: continue
                        keys = list(item.keys())
                        input_text = rf"{item.get('input', item[keys[0]] if len(keys) >= 1 else '')}"
                        output_text = rf"{item.get('output', item[keys[1]] if len(keys) >= 2 else '')}"
                        input_text, output_text = rf'{input_text}'.strip(), rf'{output_text}'.strip()
                        coded = self.__coding_function(str(input_text+'\n'+output_text).replace(self.END_TAG, '')+self.END_TAG+'\n\n')
                        buffer.extend(coded)
                        if len(self.__attention_words) < maximum_words:
                            accumulation += chr(32)+input_text+chr(32)+output_text
                            attention_words = sapiens_attention.get_attention_words(text=accumulation.strip(), maximum_length=maximum_words)
                            for item in attention_words:
                                length_of_attention_words = len(self.__attention_words)
                                if length_of_attention_words < maximum_words and item not in self.__attention_words: self.__attention_words.append(item)
                                elif length_of_attention_words >= maximum_words: break
                        else: accumulation = ''
                        while len(buffer) > self.BLOCK_SIZE:
                            sequence, buffer = buffer[:self.BLOCK_SIZE + 1], buffer[1:]
                            yield (self.__tensor_function(sequence[:-1], dtype=self.__int_dtype), self.__tensor_function(sequence[1:], dtype=self.__int_dtype))
                if self.__string:
                    buffer.extend(self.__coding_function('\n\n'+self.__string))
                    def _read_start_of_string(string='', maximum_words=10):
                        word, words = '', []
                        for character in string:
                            if character.isspace():
                                if word:
                                    words.append(word)
                                    if len(words) >= maximum_words: break
                                    word = ''
                            else: word += character
                        if word and len(words) < maximum_words: words.append(word)
                        return ' '.join(words)
                    accumulation = _read_start_of_string(string=self.__string, maximum_words=maximum_words*10)
                    attention_words = sapiens_attention.get_attention_words(text=accumulation.strip(), maximum_length=maximum_words)
                    for item in attention_words:
                        if item not in self.__attention_words: self.__attention_words.append(item)
                    while len(buffer) > self.BLOCK_SIZE:
                        sequence, buffer = buffer[:self.BLOCK_SIZE + 1], buffer[1:]
                        yield (self.__tensor_function(sequence[:-1], dtype=self.__int_dtype), self.__tensor_function(sequence[1:], dtype=self.__int_dtype))
            def get_attention_words(self): return self.__attention_words
        class TextDataset(self.__Dataset):
            def __init__(self, data=[], block_size=0): self.__data, self.BLOCK_SIZE = data, block_size
            def __len__(self): return max(0, len(self.__data) - self.BLOCK_SIZE)
            def __getitem__(self, index=0): return self.__data[index:index + self.BLOCK_SIZE], self.__data[index + 1:index + self.BLOCK_SIZE + 1]
        class Transformer(self.__Module):
            def __init__(self, embedding_dim=0, block_size=0, number_heads=0, number_layers=0, dropout=None, vocab_size=0, outer=None):
                super().__init__()
                self.positional_encoding = outer._HurModel__Parameter(outer._HurModel__tensor([]).new_zeros(1, block_size, embedding_dim))
                self.__outer = outer
                self.BLOCK_SIZE = block_size
                self.DROPOUT = outer._HurModel__Dropout(dropout)
                self.embedding = outer._HurModel__Embedding(vocab_size, embedding_dim)
                self.multi_head_attention = outer._HurModel__TransformerDecoder(outer._HurModel__TransformerDecoderLayer(d_model=embedding_dim, nhead=number_heads, dropout=dropout, batch_first=True), num_layers=number_layers)
                self.__add_and_norm = outer._HurModel__Linear(embedding_dim, vocab_size)
                self.output_layer = self.__add_and_norm
            def forward(self, input_tensor=[]):
                batch_size, sequence_length = input_tensor.size()
                positions = self.positional_encoding[:, :sequence_length, :].to(input_tensor.device)
                outer = self.__outer
                input_embedding = self.DROPOUT(self.embedding(input_tensor) + positions)
                masked_multi_head_attention = outer._HurModel__triu(outer._HurModel__ones(sequence_length, sequence_length, device=input_tensor.device) * float('-inf'), diagonal=1)
                output_embedding = self.multi_head_attention(input_embedding, memory=input_embedding, tgt_mask=masked_multi_head_attention)
                return self.__add_and_norm(output_embedding)
        self.__AbsoluteMeanQuantizationFunction = AbsoluteMeanQuantizationFunction
        self.__TextIterableDataset = TextIterableDataset
        self.__JSONIterableDataset = JSONIterableDataset
        self.__TextDataset = TextDataset
        self.__Transformer = Transformer
    def __is_web_address(self, url_path=''): return str(url_path).lower().strip().startswith(('https://', 'http://', 'www.'))
    def __get_user_id_file_path(self):
        user_id = int(float(self.USER_ID)) if type(self.USER_ID) in (str, bool, int, float) else 0
        file_path = self.__join(self.__gettempdir(), f'last_user_id_{user_id}.txt')
        return user_id, file_path
    def __convert_to_nearest_tokens(self, text=''):
        if self.__tokenizer == 'sapi-1': tokens_length = 2
        elif self.__tokenizer == 'sapi-2': tokens_length = 3
        elif self.__tokenizer == 'sapi-3': tokens_length = 4
        elif self.__tokenizer == 'sapi-4': tokens_length = 5
        elif self.__tokenizer == 'sapi-5': tokens_length = 0
        else: tokens_length = 1
        if tokens_length >= 1: text_to_list = self.__sapiens_tokenizer._SapiensTokenizer__text_to_list
        else: text_to_list = self.__sapiens_tokenizer._SapiensTokenizer__text_to_list_sapi5
        tokens = text_to_list(text=text, tokens_length=tokens_length, is_sorted=False)
        keys = list(self.__token_to_index.keys())
        for token_index, token in enumerate(tokens):
            if token not in keys:
                maximum_probability, maximum_key = 0.0, keys[-1]
                for key in keys:
                    probability = self.__SCN.textualComparison(text1=token, text2=key, consider_length=False)
                    if probability > maximum_probability and len(key.strip()) > 0: maximum_probability, maximum_key = probability, key
                tokens[token_index] = maximum_key
        return ''.join(tokens)
    def __get_last_user_id(self):
        user_id, file_path = self.__get_user_id_file_path()
        if self.__exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as opened_file: return int(str(opened_file.read()).strip())
        return 0
    def __set_last_user_id(self, id=0):
        user_id, file_path = self.__get_user_id_file_path()
        with open(file_path, 'w', encoding='utf-8') as opened_file: opened_file.write(str(id).strip())
    def __adjust_hyperparameters_sapi(self, dataset_size=0, context_window=None):
        if self.BLOCK_SIZE is None:
            if context_window == float('inf'): self.BLOCK_SIZE = min(20480000, max(1024, int(0.7 * (dataset_size ** 0.3) + 0.5 * (dataset_size ** 0.5))))
            elif context_window is not None: self.BLOCK_SIZE = max(8, int(context_window))
            else: self.BLOCK_SIZE = min(1024, max(8, int(0.7 * (dataset_size ** 0.3) + 0.5 * (dataset_size ** 0.5))))
        if self.BATCH_SIZE is None: self.BATCH_SIZE = min(128, max(4, int(self.__sqrt(dataset_size * self.BLOCK_SIZE) / 8)))
        if self.EMBEDDING_DIM is None: self.EMBEDDING_DIM = min(512, max(128, int(128 * (dataset_size * self.BLOCK_SIZE) ** 0.15)))
        if self.NUMBER_HEADS is None: self.NUMBER_HEADS = min(16, max(4, int((dataset_size ** 0.2 + self.BLOCK_SIZE ** 0.2) / 1.5)))
        if self.EMBEDDING_DIM % self.NUMBER_HEADS != 0: self.EMBEDDING_DIM += (self.NUMBER_HEADS - (self.EMBEDDING_DIM % self.NUMBER_HEADS))
        if self.NUMBER_LAYERS is None: self.NUMBER_LAYERS = min(8, max(2, int((dataset_size ** 0.15 + self.BLOCK_SIZE ** 0.15) / 2)))
        if self.EPOCHS is None:
            self.EPOCHS = min(3000 if context_window == float('inf') else 300, max(50, int(20000 / dataset_size + 200 / self.BLOCK_SIZE + 20)))
            if context_window == float('inf'): self.EPOCHS += (self.BLOCK_SIZE * 2)
    def __adjust_hyperparameters_gpt(self, dataset_size=0, context_window=None):
        if self.BLOCK_SIZE is None:
            if context_window == float('inf'): self.BLOCK_SIZE = min(20480000, max(1024, int(0.5 * (dataset_size ** 0.3) + 0.3 * (dataset_size ** 0.5))))
            elif context_window is not None: self.BLOCK_SIZE = max(8, int(context_window))
            else: self.BLOCK_SIZE = min(1024, max(8, int(0.5 * (dataset_size ** 0.3) + 0.3 * (dataset_size ** 0.5))))
        if self.BATCH_SIZE is None: self.BATCH_SIZE = min(64, max(4, int(self.__sqrt(dataset_size * self.BLOCK_SIZE) / 10)))
        if self.EMBEDDING_DIM is None: self.EMBEDDING_DIM = min(256, max(64, int(64 * (dataset_size * self.BLOCK_SIZE) ** 0.1)))
        if self.NUMBER_HEADS is None: self.NUMBER_HEADS = min(8, max(2, int((dataset_size ** 0.2 + self.BLOCK_SIZE ** 0.2) / 2)))
        if self.EMBEDDING_DIM % self.NUMBER_HEADS != 0: self.EMBEDDING_DIM += (self.NUMBER_HEADS - (self.EMBEDDING_DIM % self.NUMBER_HEADS))
        if self.NUMBER_LAYERS is None: self.NUMBER_LAYERS = min(4, max(1, int((dataset_size ** 0.15 + self.BLOCK_SIZE ** 0.15) / 3)))
        if self.EPOCHS is None:
            self.EPOCHS = min(1000 if context_window == float('inf') else 100, max(10, int(10000 / dataset_size + 100 / self.BLOCK_SIZE + 10)))
            if context_window == float('inf'): self.EPOCHS += (self.BLOCK_SIZE * 2)
    def __SHOW_ERROR_DETAILS(self):
        try: raise
        except:
            try:
                from sys import exc_info
                from traceback import format_exception, extract_tb
                error_type, error_value, traceback_obj = exc_info()
                details = format_exception(error_type, error_value, traceback_obj)
                traceback_list = extract_tb(traceback_obj)
                last_trace = traceback_list[-1]
                file_name = last_trace.filename
                line_number = last_trace.lineno
                function_name = last_trace.name
                code_line = last_trace.line
                print(f'[{self.__error_position}º ERROR]')
                print('ERROR TYPE:', error_type.__name__)
                print('ERROR VALUE:', error_value)
                print('LAST TRACE:', last_trace)
                print('FILE NAME:', file_name)
                print('LINE NUMBER:', line_number)
                print('FUNCTION NAME:', function_name)
                print('CODE LINE:', code_line)
                print()
                self.__error_position += 1
            except: pass
    def __generate_tokens_x(self, prompt='', max_tokens=500, temperature=0.5, top_k=50, top_p=0.9, end_tag=None):
        try:
            if self.__tokenizer.startswith('sapi'): prompt = self.__convert_to_nearest_tokens(text=prompt)
            user_prompt, user_answer, id, self.__tokens_count = prompt, '', 0, 0
            if self.__fine_tuning:
                only_adjustment, original_input = False, ''
                if not self.__model and not self.__hurnet_parameters: only_adjustment, precision = True, 0.0
                last_id = self.__get_last_user_id()
                highest_probability, best_index, probable_answers = 0.0, -1, []
                for index, fine_tuning in enumerate(self.__fine_tuning):
                    prompt_embedding = list(fine_tuning.get('prompt_embedding', []))
                    relationship_id = int(fine_tuning.get('relationship_id', 0))
                    if not only_adjustment: precision = float(fine_tuning.get('precision', 0.5))
                    fit_prompt = self.__sapiens_embedding.embedding_to_text(embedding=prompt_embedding, pattern=self.__tokenizer)
                    probability = self.__SCN.textualComparison(text1=user_prompt, text2=fit_prompt, consider_length=True)
                    if relationship_id > 0 and relationship_id == last_id and probability >= precision:
                        probable_answers.append({'probability': probability, 'index': index})
                        original_input = fit_prompt
                    elif probability >= precision and probability > highest_probability: highest_probability, best_index, original_input = probability, index, fit_prompt
                def _get_user_answer_id(index_found=0):
                    answer_embedding = list(self.__fine_tuning[index_found].get('answer_embedding', []))
                    user_answer = self.__sapiens_embedding.embedding_to_text(embedding=answer_embedding, pattern=self.__tokenizer, strip=True)
                    id = int(self.__fine_tuning[index_found].get('id', 0))
                    return user_answer, id
                if probable_answers:
                    maximum_probability, maximum_index = 0.0, 0
                    for probable_answer in probable_answers:
                        probability = float(probable_answer.get('probability', 0.0))
                        index = int(probable_answer.get('index', 0))
                        if probability > maximum_probability: maximum_probability, maximum_index = probability, index
                    user_answer, id = _get_user_answer_id(index_found=maximum_index)
                if only_adjustment and best_index < 0: best_index = 0
                if not user_answer and best_index >= 0: user_answer, id = _get_user_answer_id(index_found=best_index)
                if user_answer and self.__generalization_direction >= 0: user_answer = self.__sapiens_generalization.generalization(prompt=user_prompt, original_input=original_input, original_output=user_answer, direction=self.__generalization_direction)
            if self.__hurnet_parameters and not user_answer:
                self.__HurNetTorch.setParameters(state=self.__hurnet_parameters)
                prompt_embedding = [self.__sapiens_embedding.text_to_embedding(text_data=self.__SCN.normalization(input_text=user_prompt), length=self.HURNET_EMBEDDING_LENGTH, pattern=self.__tokenizer, method='average')]
                output_index = self.__HurNetTorch.predict(input_layer=prompt_embedding, decimal_places=0)[0][0]
                output_index = min((len(self.__output_indexing)-1, max((0, output_index))))
                output_embedding = self.__output_indexing[output_index]
                hurnet_fit_configuration = self.__hurnet_fit_configuration[output_index]
                relationship_id = int(hurnet_fit_configuration.get('relationship_id', 0))
                precision = float(hurnet_fit_configuration.get('precision', 0.5))
                id = int(hurnet_fit_configuration.get('id', 0))
                last_id = self.__get_last_user_id()
                if (relationship_id <= 0) or (relationship_id > 0 and relationship_id == last_id):
                    user_answer = self.__sapiens_embedding.embedding_to_text(embedding=output_embedding, pattern=self.__tokenizer)
                    if self.__fine_tuning:
                        def _hurnet_probability(user_prompt='', embedding2=[]):
                            embedding1 = self.__sapiens_embedding.text_to_embedding(text_data=user_prompt, length=len(embedding2), pattern=self.__tokenizer, method='average')
                            return min(1.0, max(0.0, self.__HurNetTorch.predict(input_layer=[[min(x, y) for x, y in zip(embedding1, embedding2)]])[0])) if self.__HurNetTorch.train(input_layer=[embedding1], output_layer=[1.0]) else 0.0
                        probability = _hurnet_probability(user_prompt=user_prompt, embedding2=output_embedding)
                    else: probability = self.__SCN.textualComparison(text1=user_prompt, text2=user_answer, consider_length=False)
                    if probability < precision and self.__model: user_answer = ''
            if user_answer:
                self.__set_last_user_id(id=id)
                user_answer = user_answer[0].upper() + user_answer[1:]
                for token in user_answer:
                    if self.__interval > 0: self.__sleep(self.__interval)
                    yield token
                return ''
            if not self.__model: return prompt
            self.__model.eval()
            def _get_last_n_tokens(text='', n=0):
                tokens = self.__sapiens_tokenizer.to_encode(text_data=text, pattern=self.__tokenizer)
                truncated_text = self.__sapiens_tokenizer.to_decode(embedding=tokens[-n:], pattern=self.__tokenizer)
                return truncated_text
            abandonment, tokens_generated = False, 0
            encoded_prompt = self.__encode(_get_last_n_tokens(text=prompt, n=self.BLOCK_SIZE))
            input_tensor = self.__tensor(encoded_prompt, dtype=self.__int64).unsqueeze(0).to(self.DEVICE)
            log_probabilities_sum, total_tokens = 0.0, 0
            start = self.__time() if self.__interval < 1 else 0
            generated_tokens_list, united_tokens = [], ''
            near_the_limit = max(1, max_tokens-int(max_tokens*0.2))
            def _get_sentence(sentence_separators=[], united_tokens=''):
                for sentence_separator in sentence_separators:
                    if sentence_separator in united_tokens:
                        united_tokens = united_tokens[:united_tokens.rfind(sentence_separator)+1].rstrip()
                        return united_tokens
                return united_tokens
            first_iteration, sentence_separators = True, ('.', ';', '!', '?', '\n')
            END_TAG, SYSTEM_TAG, USER_TAG, ASSISTANT_TAG = self.END_TAG, self.SYSTEM_TAG, self.USER_TAG, self.ASSISTANT_TAG
            maximum_length, first_return = max((len(END_TAG), len(SYSTEM_TAG), len(USER_TAG), len(ASSISTANT_TAG))), True
            with self.__no_grad():
                while True:
                    if not abandonment and tokens_generated < max_tokens and self.__tokens_count < max_tokens:
                        conditioned_input = input_tensor[:, -self.BLOCK_SIZE:] if input_tensor.size(1) > self.BLOCK_SIZE else input_tensor
                        logistics = self.__model(conditioned_input)
                        logistics = logistics[:, -1, :] / temperature
                        sorted_logistics, sorted_indexes = logistics.sort(descending=True)
                        vocabulary_size = logistics.size(-1)
                        if top_k is None or top_k <= 0 or top_k > vocabulary_size: top_k = vocabulary_size
                        top_k_logistics, top_k_indexes = sorted_logistics[:top_k], sorted_indexes[:top_k]
                        cumulative_probabilities = self.__Function.softmax(top_k_logistics, dim=-1).cumsum(dim=-1)
                        mask = cumulative_probabilities <= top_p
                        if mask.sum() == 0: mask[0] = True
                        filtered_logistics, filtered_indexes = top_k_logistics[mask], top_k_indexes[mask]
                        output_probabilities = self.__Function.softmax(filtered_logistics, dim=-1)
                        next_token_index = self.__multinomial(output_probabilities, num_samples=1)
                        next_token = filtered_indexes[next_token_index].unsqueeze(0)
                        token_log_probabilities = self.__Function.log_softmax(filtered_logistics, dim=-1)[next_token_index].item()
                        log_probabilities_sum += token_log_probabilities
                        total_tokens += 1
                        input_tensor = self.__cat((input_tensor, next_token), dim=1)
                        shifted_right = next_token.item()
                        decoded_token = self.__decode([shifted_right])
                        if self.__interval < 1: self.__interval = abs(start-self.__time())/max(1, maximum_length*10)
                        first_iteration, starts_return = tokens_generated == 0 or self.__tokens_count == 0, True
                        if first_iteration:
                            decoded_token = decoded_token.lstrip()
                            if decoded_token.strip():
                                if decoded_token[0] in sentence_separators: decoded_token = decoded_token[1:].lstrip()
                                if decoded_token.strip(): decoded_token = decoded_token[0].upper()+decoded_token[1:]
                                else: continue
                            else: continue
                        if maximum_length > 0:
                            if decoded_token: generated_tokens_list.append(decoded_token)
                            if generated_tokens_list:
                                united_tokens = ''.join(generated_tokens_list)
                                if united_tokens and tokens_generated >= near_the_limit:
                                    _united_tokens = _get_sentence(sentence_separators=sentence_separators, united_tokens=united_tokens)
                                    if united_tokens != _united_tokens: united_tokens, abandonment = _united_tokens, True
                                if len(united_tokens) >= maximum_length:
                                    if starts_return and ASSISTANT_TAG and ASSISTANT_TAG in united_tokens:
                                        tokens_list, text_index = united_tokens.split(ASSISTANT_TAG), 1
                                        if len(tokens_list) > 1 and len(tokens_list[text_index].strip()) < 1: text_index = 0
                                        united_tokens = tokens_list[text_index]
                                        if END_TAG and END_TAG in united_tokens: united_tokens, abandonment = united_tokens.split(END_TAG)[0], True
                                        starts_return, abandonment, first_return = False, False if first_return else True, False
                                        for token in united_tokens.lstrip() if first_iteration else united_tokens: yield token
                                    if starts_return and END_TAG and END_TAG in united_tokens:
                                        tokens_list, text_index = united_tokens.split(END_TAG), 0
                                        if len(tokens_list) > 1 and len(tokens_list[text_index].strip()) < 1: text_index = 1
                                        united_tokens = tokens_list[text_index].rstrip()
                                        starts_return, abandonment, first_return = False, True, False
                                        for token in united_tokens.lstrip() if first_iteration else united_tokens: yield token
                                    if starts_return and SYSTEM_TAG and SYSTEM_TAG in united_tokens:
                                        tokens_list, text_index = united_tokens.split(SYSTEM_TAG), 0
                                        if len(tokens_list) > 1 and len(tokens_list[text_index].strip()) < 1: text_index = 1
                                        united_tokens = tokens_list[text_index]
                                        starts_return, abandonment, first_return = False, True, False
                                        for token in united_tokens.lstrip() if first_iteration else united_tokens: yield token
                                    if starts_return and USER_TAG and USER_TAG in united_tokens:
                                        tokens_list, text_index = united_tokens.split(USER_TAG), 0
                                        if len(tokens_list) > 1 and len(tokens_list[text_index].strip()) < 1: text_index = 1
                                        united_tokens = tokens_list[text_index]
                                        starts_return, abandonment, first_return = False, True, False
                                        for token in united_tokens.lstrip() if first_iteration else united_tokens: yield token
                                    if not starts_return: united_tokens = ''
                        else:
                            if tokens_generated >= near_the_limit:
                                _decoded_token = _get_sentence(sentence_separators=sentence_separators, united_tokens=decoded_token)
                                if decoded_token != _decoded_token: decoded_token, abandonment = _decoded_token, True
                            first_return = False
                            for token in decoded_token.lstrip() if first_iteration else decoded_token: yield token
                        tokens_generated += 1
                    else: break
                    self.__tokens_count += 1
                if total_tokens > 0:
                    average_log_probability = log_probabilities_sum / total_tokens
                    try: self.PERPLEXITY = self.__exp(-average_log_probability)
                    except: self.PERPLEXITY = 100.0
                else: self.PERPLEXITY = 100.0
                if united_tokens:
                    united_tokens = _get_sentence(sentence_separators=sentence_separators, united_tokens=united_tokens)
                    if END_TAG and END_TAG[0] in united_tokens:
                        matching_index = united_tokens.find(END_TAG[0])
                        matching_string = united_tokens[matching_index:]
                        if END_TAG.startswith(matching_string): united_tokens = united_tokens[:matching_index]
                    for token in united_tokens.lstrip() if first_iteration else united_tokens.rstrip(): yield token
            self.__cuda.empty_cache()
            return ''
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in __generate_tokens_x:' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return ''
    def __training_with_fine_tuning(self, precision=0.5, validate=0.0, progress=True):
        try:
            training_metrics = {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
            total_samples, has_validation = len(self.__inputs_targets), validate > 0
            epochs, adjustment_count = self.EPOCHS if self.EPOCHS is not None else 10, 0
            total_iterations = total_samples*epochs
            if progress:
                progress_bar = self.__tqdm(total=total_iterations, desc='Training with fine-tuning')
                real_loss, current_loss, current_precision = 0.0, 0.0, 0.0
                progress_bar.set_postfix({'real-loss': f'{real_loss:.4f}', 'loss': f'{current_loss:.4f}', 'precision': f'{current_precision:.4f}'})
            validation_epochs = epochs-int(epochs*validate) if has_validation else epochs
            for epoch in range(1, epochs+1):
                self.__inputs_targets = self.__sample(self.__inputs_targets, total_samples)
                real_loss_x, current_loss_x, current_precision_x = [], [], []
                for input_tensor_target_tensor in self.__inputs_targets:
                    input_tensor, target_tensor = input_tensor_target_tensor
                    self.__model.train()
                    logits = self.__model(input_tensor)
                    loss = self.__Function.cross_entropy(logits.view(-1, logits.size(-1)), target_tensor.view(-1))
                    self.__optimizer.zero_grad()
                    loss.backward()
                    self.__utils.clip_grad_norm_(self.__model.parameters(), 1.0)
                    self.__optimizer.step()
                    if self.USE_SCHEDULER and self.__scheduler: self.__scheduler.step()
                    real_loss = loss.item()
                    current_loss = min((1.0, max((0.0, real_loss))))
                    current_precision = 1.0-current_loss
                    real_loss_x.append(real_loss), current_loss_x.append(current_loss), current_precision_x.append(current_precision)
                    adjustment_count += 1
                    if progress:
                        progress_bar.n = adjustment_count
                        progress_bar.set_postfix({'real-loss': f'{real_loss:.4f}', 'loss': f'{current_loss:.4f}', 'precision': f'{current_precision:.4f}'})
                    training_metrics['loss'], training_metrics['precision'] = current_loss, current_precision
                real_loss_y, current_loss_y, current_precision_y = self.__mean(real_loss_x), self.__mean(current_loss_x), self.__mean(current_precision_x)
                if progress: progress_bar.set_postfix({'real-loss': f'{real_loss_y:.4f}', 'loss': f'{current_loss_y:.4f}', 'precision': f'{current_precision_y:.4f}'})
                training_metrics['loss'], training_metrics['precision'] = current_loss_y, current_precision_y
                if has_validation and epoch > validation_epochs:
                    prompts_length, probability = len(self.__prompts), 0.0
                    if progress:
                        progress_bar_x = self.__tqdm(total=prompts_length, desc='Validating fine-tuning')
                        progress_bar_x.set_postfix({'probability': f'{probability:.8f}'})
                    current_loss_z, current_precision_z = [], []
                    for index, (prompt, answer) in enumerate(zip(self.__prompts, self.__answers)):
                        inference = self.predict(prompt=prompt, max_tokens=self.__encoding_length, temperature=0.5, top_k=0, top_p=1.0, stream=False)
                        probability = self.__SCN.textualComparison(text1=inference, text2=answer, consider_length=True)
                        current_loss, current_precision = 1.0-probability, probability
                        if progress: progress_bar.set_postfix({'real-loss': f'{real_loss_y:.4f}', 'loss': f'{current_loss:.4f}', 'precision': f'{current_precision:.4f}'})
                        training_metrics['val_loss'], training_metrics['precision'] = current_loss, current_precision
                        current_loss_z.append(current_loss), current_precision_z.append(current_precision)
                        if progress:
                            progress_bar_x.n = index+1
                            progress_bar_x.set_postfix({'probability': f'{probability:.8f}'})
                    final_current_loss, final_current_precision = self.__mean(current_loss_z), self.__mean(current_precision_z)
                    if progress: progress_bar.set_postfix({'real-loss': f'{real_loss_y:.4f}', 'loss': f'{final_current_loss:.4f}', 'precision': f'{final_current_precision:.4f}'})
                    training_metrics['val_loss'], training_metrics['generalization_rate'], training_metrics['precision'] = final_current_loss, current_precision_y, final_current_precision
                    if progress: 
                        progress_bar_x.n = prompts_length
                        progress_bar_x.refresh()
                        progress_bar_x.close()   
                    if final_current_precision >= precision: break
                if current_precision_y >= precision: break
            if progress: 
                progress_bar.n = total_iterations
                progress_bar.refresh()
                progress_bar.close()
            return training_metrics
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in __training_with_fine_tuning: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return training_metrics if 'training_metrics' in locals() else {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
    def __read_remote_file(self, url_path=''):
        with self.__urlopen(url_path) as response: return rf"{response.read().decode('utf-8', errors='replace')}".replace('\r\n', '\n').replace('\r', '\n').strip()
    def __load_json(self, string_content=''):
        json_content = {}
        string_content = str(string_content)
        try: json_content = self.__loads(string_content)
        except:
            from ast import literal_eval
            json_content = literal_eval(string_content)
        return json_content    
    def __prepare_json(self, json_data={}):
        if type(json_data) == dict: pairs = json_data[list(json_data.keys())[0]]
        else: pairs = json_data
        if not self.END_TAG: self.END_TAG = '<|end|>'
        return '\n\n'.join([str(rf'{pair[list(pair.keys())[0]]}'+'\n'+rf'{pair[list(pair.keys())[1]]}').replace(self.END_TAG, '').strip()+self.END_TAG for pair in pairs])
    def __json_to_string(self, url_path=''):
        result_string = ''
        if not url_path: return result_string
        if self.__is_web_address(url_path=url_path): json_stream = self.__urlopen(url_path)
        else: json_stream = open(url_path, 'rb')
        for item in self.__items(json_stream, 'data.item'):
            if not isinstance(item, dict) or len(item) < 1: continue
            keys = list(item.keys())
            input_text = rf"{item.get('input', item[keys[0]] if len(keys) >= 1 else '')}"
            output_text = rf"{item.get('output', item[keys[1]] if len(keys) >= 2 else '')}"
            input_text, output_text = rf'{input_text}'.strip(), rf'{output_text}'.strip()
            if input_text and output_text: result_string += input_text+'\n'+output_text+'\n\n'
        return result_string.strip()
    def __adjust_hyperparameters(self, dataset_size=0, context_window=None, tokenizer='gpt-4'):
        if tokenizer.startswith('sapi'): self.__adjust_hyperparameters_sapi(dataset_size=dataset_size, context_window=context_window)
        else: self.__adjust_hyperparameters_gpt(dataset_size=dataset_size, context_window=context_window)
    def __install_quantitative_hooks(self):
        def pre_forward(module, input=[]):
            weights = module.weight
            quantized_weights = self.__AbsoluteMeanQuantizationFunction.apply(weights, self.__quantization_epsilon)
            module.weight.data = quantized_weights
        for modulation in self.__model.modules():
            if isinstance(modulation, self.__Linear): modulation.register_forward_pre_hook(pre_forward)
    def __set_scheduler(self, step_size=30, gamma=0.1):
        if self.__optimizer:
            class_name = self.SCHEDULED.__name__
            args = self.__signature(self.SCHEDULED).parameters
            kwargs = {'optimizer': self.__optimizer}
            if 'ReduceLROnPlateau' in class_name or 'metrics' in args:
                from torch.optim.lr_scheduler import StepLR
                self.SCHEDULED = StepLR
                args = self.__signature(self.SCHEDULED).parameters
                kwargs = {'optimizer': self.__optimizer}
            elif 'OneCycleLR' in class_name:
                from torch.optim.lr_scheduler import CyclicLR
                self.SCHEDULED = CyclicLR
                args = self.__signature(self.SCHEDULED).parameters
                kwargs = {'optimizer': self.__optimizer}
            if 'milestones' in args: kwargs['milestones'] = (30, 60, 90)
            if 'step_size' in args: kwargs['step_size'] = step_size
            if 'gamma' in args: kwargs['gamma'] = gamma
            if 'factor' in args: kwargs['factor'] = gamma
            if 'patience' in args: kwargs['patience'] = 10
            if 'mode' in args: kwargs['mode'] = 'min'
            if 'threshold' in args: kwargs['threshold'] = 1e-4
            if 'threshold_mode' in args: kwargs['threshold_mode'] = 'rel'
            if 'cooldown' in args: kwargs['cooldown'] = 0
            if 'min_lr' in args: kwargs['min_lr'] = 0
            if 'verbose' in args: kwargs['verbose'] = False
            if 'T_max' in args: kwargs['T_max'] = 100
            if 'eta_min' in args: kwargs['eta_min'] = 0
            if 'base_lr' in args: kwargs['base_lr'] = 1e-3
            if 'max_lr' in args: kwargs['max_lr'] = 1e-2
            if 'step_size_up' in args: kwargs['step_size_up'] = 2000
            if 'cycle_mode' in args: kwargs['cycle_mode'] = 'triangular'
            if 'mode' in args: kwargs['mode'] = 'triangular2'
            if 'total_steps' in args: kwargs['total_steps'] = 100
            if 'pct_start' in args: kwargs['pct_start'] = 0.3
            if 'div_factor' in args: kwargs['div_factor'] = 25.0
            if 'final_div_factor' in args: kwargs['final_div_factor'] = 1e4
            if 'power' in args: kwargs['power'] = 1.0
            if 'total_iters' in args: kwargs['total_iters'] = 100
            if 'T_0' in args: kwargs['T_0'] = 10
            if 'lr_lambda' in args: kwargs['lr_lambda'] = lambda epoch: gamma ** epoch
            self.__scheduler = self.SCHEDULED(**kwargs)
    def __identify_best_activation_function(self, x=[], y=[], interaction=True, candidate_activations=None, quantization=None, method='division', hidden_layers=None):
        if candidate_activations is None: candidate_activations = ('linear', 'sigmoid', 'tanh', 'relu')
        input_features = x.size(-1)
        output_features = y.size(-1)
        best_loss = float('inf')
        best_activation = candidate_activations[0]
        for activation in candidate_activations:
            temporary_layer = self.__HurNetTransformer(input_dim=input_features, output_dim=output_features, activation_function=activation, interaction=interaction, device=self.DEVICE)
            x_flat, y_flat = x.reshape(-1, input_features), y.reshape(-1, output_features)
            temporary_layer.train_layer(x=x_flat, y=y_flat, quantization=quantization, method=method, hidden_layers=hidden_layers)
            predictions = temporary_layer(x)
            loss = self.__Function.mse_loss(predictions, y)
            if loss.item() < best_loss: best_loss, best_activation = loss.item(), activation
        return best_activation
    def __identify_best_bias(self, x=[], y=[], best_activation='linear', interaction=True, quantization=None, method='division', hidden_layers=None):
        input_features, output_features = x.size(-1), y.size(-1)
        x_flat, y_flat = x.reshape(-1, input_features), y.reshape(-1, output_features)
        current_bias = 0.0
        temporary_layer = self.__HurNetTransformer(input_dim=input_features, output_dim=output_features, activation_function=best_activation, interaction=interaction, bias=current_bias, device=self.DEVICE)
        temporary_layer.train_layer(x=x_flat, y=y_flat, quantization=quantization, method=method, hidden_layers=hidden_layers)
        predictions, step = temporary_layer(x), 0.1
        best_loss = self.__Function.mse_loss(predictions, y).item()
        for _ in range(30):
            improved = False
            for direction in (-1, 1):
                candidate_bias = current_bias + direction * step
                temporary_layer = self.__HurNetTransformer(input_dim=input_features, output_dim=output_features, activation_function=best_activation, interaction=interaction, bias=candidate_bias, device=self.DEVICE)
                temporary_layer.train_layer(x=x_flat, y=y_flat, quantization=quantization, method=method, hidden_layers=hidden_layers)
                predictions = temporary_layer(x)
                loss = self.__Function.mse_loss(predictions, y).item()
                if loss < best_loss: best_loss, improved, current_bias = loss, True, candidate_bias
            if not improved:
                step /= 2
                if step < 1e-4: break
        return current_bias
    def __identify_best_interaction(self, x=[], y=[], best_activation='linear', best_bias=0.0, quantization=None, method='division', hidden_layers=None):
        input_features, output_features = x.size(-1), y.size(-1)
        x_flat, y_flat = x.reshape(-1, input_features), y.reshape(-1, output_features)
        best_loss, best_interaction = float('inf'), False
        for candidate in (True, False):
            temporary_layer = self.__HurNetTransformer(input_dim=input_features, output_dim=output_features, activation_function=best_activation, interaction=candidate, bias=best_bias, device=self.DEVICE)
            temporary_layer.train_layer(x=x_flat, y=y_flat, quantization=quantization, method=method, hidden_layers=hidden_layers)
            predictions = temporary_layer(x)
            loss = self.__Function.mse_loss(predictions, y).item()
            if loss < best_loss: best_loss, best_interaction = loss, candidate
        return best_interaction
    def __get_date_and_time(self): return self.__datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def __get_division(self, index=0):
        if type(index) == str: return 'division' if index.lower().strip() == 'explicit' else 'pseudo-inverse'
        return 'division' if type(index) == int and index > 0 else 'pseudo-inverse'
    def __format_numbers(self, data_number=0, is_tokens=False):
        if data_number < 1_000: return data_number if is_tokens else f'{data_number}U'
        elif data_number < 1_000_000: return f'{data_number // 1_000}K'
        elif data_number < 1_000_000_000: return f'{data_number // 1_000_000}M'
        elif data_number < 1_000_000_000_000: return f'{data_number // 1_000_000_000}B'
        else: return f'{data_number // 1_000_000_000_000}T'
    def __compute_loss(self, loader=[]):
        if len(loader) == 0: return float('inf')
        self.__model.eval()
        total_loss = 0
        with self.__no_grad():
            for input_batch, target_batch in loader:
                input_batch, target_batch = input_batch.to(self.DEVICE), target_batch.to(self.DEVICE)
                logistics = self.__model(input_batch)
                loss = self.__Function.cross_entropy(logistics.reshape(-1, logistics.size(-1)), target_batch.reshape(-1))
                total_loss += loss.item()
        self.__cuda.empty_cache()
        return total_loss / len(loader)
    def __get_file_size(self, url_path='', _is_web_address=None):
        if _is_web_address is None: _is_web_address = self.__is_web_address(url_path=url_path)
        if _is_web_address:
            response = self.__head(url_path, allow_redirects=True)
            if 'Content-Length' in response.headers: return int(response.headers['Content-Length'])
            else:
                response, size = self.__get(url_path, stream=True), 0
                for chunk in response.iter_content(chunk_size=8192): size += len(chunk)
                return size
        elif self.__exists(url_path): return self.__getsize(url_path)
        else: raise ValueError(error_message1)
    def __unique_training(self, dataset_path='', string='', precision=1.0, tokenizer='gpt-4', context_window=None, hurnet_initializer=True, hurnet_layer=False, hurnet_fit=False, end_tag=None, stream_dataset=False, validate=0.0, quantization=None, progress=True):
        try:
            training_metrics = {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
            original_hurtnet_layer, original_hurnet_fit = hurnet_layer, hurnet_fit
            if self.__adjustment_data: return self.__training_with_fine_tuning(precision=precision, validate=validate, progress=progress)
            if stream_dataset: validate = 0.0
            self.__string = str(self.__string+'\n\n'+string).strip()
            if hurnet_fit and not hurnet_layer: hurnet_layer, hurnet_fit = True, False
            is_txt, is_json, text_data = dataset_path.endswith('.txt'), dataset_path.endswith('.json'), ''
            sapi_tokenizer, _is_web_address = tokenizer.startswith('sapi'), self.__is_web_address(url_path=dataset_path)
            if not stream_dataset or sapi_tokenizer:
                if _is_web_address:
                    is_json = True if '.json' in dataset_path.lower() else False
                    text_data = self.__read_remote_file(url_path=dataset_path)
                    if is_json:
                        json_data = self.__load_json(string_content=text_data)
                        text_data = rf'{self.__prepare_json(json_data=json_data)}'.strip()
                elif self.__exists(dataset_path):
                    if not is_txt and not is_json and len(self.__string) < 1: raise ValueError('Unsupported file format. Use .txt or .json.')
                    if is_txt:
                        with open(dataset_path, 'r', encoding='utf-8') as file: text_data = rf'{file.read()}'.strip()
                    elif is_json:
                        with open(dataset_path, 'r', encoding='utf-8') as file: json_data = self.__json_load(file)
                        text_data = rf'{self.__prepare_json(json_data=json_data)}'.strip()
                if len(self.__string) > 0: text_data += '\n\n'+self.__string
                text_data = rf'{text_data}'.strip()
                def _resume_string(string='', maximum_words=1):
                    word_list = string.split()
                    list_length = len(word_list)
                    if not string or list_length <= maximum_words: return string
                    words_per_part = max((1, maximum_words//3))
                    opening_words = word_list[:words_per_part]
                    middle_index = (list_length//2)-words_per_part//2
                    middle_words = word_list[middle_index:middle_index+words_per_part]
                    final_words = word_list[-words_per_part:]
                    words_joined_together = opening_words+middle_words+final_words
                    temporary_list = []
                    for word in words_joined_together:
                        if word not in temporary_list: temporary_list.append(word)
                    words_joined_together = temporary_list
                    return ' '.join(words_joined_together).strip()
                resume_string = _resume_string(string=text_data, maximum_words=500000)
                attention_words = self.__SapiensAttention().get_attention_words(text=resume_string, maximum_length=100)
                for attention_word in attention_words:
                    if attention_word not in self.__attention_words: self.__attention_words.append(attention_word)
            if self.__encode is None and self.__decode is None:
                if sapi_tokenizer and not self.__loaded_vocabulary:
                    self.__sapiens_tokenizer.pattern = tokenizer
                    if is_json and not text_data: text_data = self.__json_to_string(url_path=dataset_path)+'\n\n'+text_data
                    self.__sapiens_tokenizer.sapi_structure_processing(file_path=dataset_path if is_txt else '', text_data=text_data.strip(), pattern=tokenizer)
                elif self.__loaded_vocabulary: self.__tokenizer = tokenizer = self.__sapiens_tokenizer.pattern
                self.__vocabulary_size = self.__sapiens_tokenizer.get_vocabulary_size(pattern=tokenizer)
                self.__token_to_index = self.__sapiens_tokenizer.get_token_to_index() if sapi_tokenizer else {}
                self.__index_to_token = self.__sapiens_tokenizer.get_index_to_token() if sapi_tokenizer else {}
                self.__encode = self.__sapiens_tokenizer.get_encode(pattern=tokenizer)
                self.__decode = self.__sapiens_tokenizer.get_decode(pattern=tokenizer)
                self.__pad_token_id, self.__loaded_vocabulary = self.__sapiens_tokenizer.to_encode(text_data=chr(32), pattern=tokenizer), True
            if stream_dataset and not sapi_tokenizer:
                tokens_number = 0
                if is_json:
                    result_string = ''
                    if self.__is_web_address(url_path=dataset_path): json_stream = self.__urlopen(dataset_path)
                    else: json_stream = open(dataset_path, 'rb')
                    for item in self.__items(json_stream, 'data.item'):
                        if not isinstance(item, dict) or len(item) < 1: continue
                        keys = list(item.keys())
                        input_text = rf"{item.get('input', item[keys[0]] if len(keys) >= 1 else '')}"
                        output_text = rf"{item.get('output', item[keys[1]] if len(keys) >= 2 else '')}"
                        input_text, output_text = rf'{input_text}'.strip(), rf'{output_text}'.strip()
                        if input_text and output_text: result_string += input_text+'\n'+output_text+'\n\n'
                        tokens_number += len(self.__encode(result_string))
                    tokens_number -= len(self.__encode('\n\n'))
                else:
                    def _open_stream(dataset_path=''):
                        if self.__is_web_address(url_path=dataset_path):
                            response = self.__get(dataset_path, stream=True)
                            response.raise_for_status()
                            return response.iter_lines(decode_unicode=True)
                        else: return open(dataset_path, 'r', encoding='utf-8')
                    file = _open_stream(dataset_path)
                    if hasattr(file, '__enter__'):
                        with file as open_file:
                            for chunk in open_file: tokens_number += len(self.__encode(rf'{chunk}'))
                    else:
                        for chunk in file: tokens_number += len(self.__encode(rf'{chunk}'))
                    if len(self.__string) > 0: tokens_number += len(self.__encode('\n\n'+self.__string))
                dataset_size = tokens_number
            else:
                encoder = self.__encode(text_data)
                data = self.__tensor(encoder, dtype=self.__int64)
                dataset_size = len(data)
                tokens_number = len(encoder)
            self.TOKENS_NUMBER = tokens_number
            if dataset_size < 10: raise ValueError('Dataset too small for training. Add more data.')
            self.__tokenizer = tokenizer
            self.__adjust_hyperparameters(dataset_size, context_window=context_window, tokenizer=tokenizer)
            if stream_dataset and not sapi_tokenizer:
                if is_json: train_dataset = self.__JSONIterableDataset(dataset_path=dataset_path, string=self.__string, coding_function=self.__encode, tensor_function=self.__tensor, int_dtype=self.__int64, block_size=self.BLOCK_SIZE, end_tag=self.END_TAG)
                else: train_dataset = self.__TextIterableDataset(dataset_path=dataset_path, string=self.__string, coding_function=self.__encode, tensor_function=self.__tensor, int_dtype=self.__int64, block_size=self.BLOCK_SIZE, end_tag=self.END_TAG)
                self.__attention_words = train_dataset.get_attention_words()
                train_loader = self.__DataLoader(train_dataset, batch_size=self.BATCH_SIZE)
                steps_per_epoch = max((1, (dataset_size - self.BLOCK_SIZE) // self.BATCH_SIZE))
                total_steps = steps_per_epoch * self.EPOCHS
            else:
                if validate > 0:
                    split_point = int((1-validate) * dataset_size)
                    train_data, data_values = data[:split_point], data[split_point:]
                else: train_data = data
                if len(train_data) < self.BLOCK_SIZE: self.BLOCK_SIZE = len(train_data) - 1
                train_dataset = self.__TextDataset(train_data, self.BLOCK_SIZE)
                if validate > 0: dataset_values = self.__TextDataset(data_values, self.BLOCK_SIZE)
                train_loader = self.__DataLoader(train_dataset, batch_size=self.BATCH_SIZE, shuffle=True)
                if validate > 0 and len(dataset_values) <= 0: loader_values = train_loader
                elif validate > 0: loader_values = self.__DataLoader(dataset_values, batch_size=self.BATCH_SIZE, shuffle=False)
                total_steps = len(train_loader) * self.EPOCHS
            if self.__model is None:
                if hurnet_layer: self.__model = self.__TransformerHurNet(embedding_dim=self.EMBEDDING_DIM, block_size=self.BLOCK_SIZE, number_heads=self.NUMBER_HEADS, number_layers=self.NUMBER_LAYERS, dropout=self.DROPOUT, vocab_size=self.__vocabulary_size, device=self.DEVICE, outer=self).to(self.DEVICE)
                else: self.__model = self.__Transformer(embedding_dim=self.EMBEDDING_DIM, block_size=self.BLOCK_SIZE, number_heads=self.NUMBER_HEADS, number_layers=self.NUMBER_LAYERS, dropout=self.DROPOUT, vocab_size=self.__vocabulary_size, outer=self).to(self.DEVICE)
            if self.USE_BIT_NET_QUANTIZATION: self.__install_quantitative_hooks()
            if not hurnet_fit and self.__optimizer is None:
                if type(self.WEIGHT_DECAY) == float: self.__optimizer = self.__optim.Adam(self.__model.parameters(), lr=self.LEARNING_RATE, weight_decay=self.WEIGHT_DECAY)
                else: self.__optimizer = self.__optim.Adam(self.__model.parameters(), lr=self.LEARNING_RATE)
                if self.USE_SCHEDULER:
                    scheduler_fraction, decay_target_ratio = 0.1, 0.1
                    if hasattr(train_loader, '__len__'):
                        steps_per_epoch = len(train_loader)
                        step_size = max(1, int(steps_per_epoch * scheduler_fraction))
                        total_scheduler_steps = max(1, int((steps_per_epoch * self.EPOCHS) / step_size))
                    else: step_size, total_scheduler_steps = 100, 10
                    gamma = decay_target_ratio ** (1 / total_scheduler_steps)
                    self.__set_scheduler(step_size=step_size, gamma=gamma)
            if hurnet_initializer and not self.__loaded_model:
                self.__model.eval()
                with self.__no_grad():
                    sample_input, sample_target = next(iter(train_loader))
                    sample_input, sample_target = sample_input.to(self.DEVICE), sample_target.to(self.DEVICE)
                    embedded = self.__model.embedding(sample_input)
                    positions = self.__model.positional_encoding[:, :sample_input.size(1), :].to(self.DEVICE)
                    embedded = self.__model.dropout(embedded + positions) if hurnet_layer else self.__model.DROPOUT(embedded + positions)
                    mask = self.__triu(self.__ones(sample_input.size(1), sample_input.size(1), device=self.DEVICE) * float('-inf'), diagonal=1)
                    output = self.__model.multi_head_attention(embedded, memory=embedded, tgt_mask=mask)
                    x, y = output.reshape(-1, output.size(-1)), sample_target.reshape(-1)
                    y_onehot, interaction = self.__zeros(y.size(0), self.__vocabulary_size, device=self.DEVICE).scatter_(1, y.unsqueeze(1), 1), True
                    best_activation = self.__identify_best_activation_function(x=x, y=y_onehot, interaction=interaction)
                    best_bias = self.__identify_best_bias(x=x, y=y_onehot, best_activation=best_activation, interaction=interaction)
                    hook_data, hooks, best_interaction = {}, [], self.__identify_best_interaction(x=x, y=y_onehot, best_activation=best_activation, best_bias=best_bias)
                    def _hook_function(module=0, input=[], output=[]): hook_data[module] = (input[0], output)
                    for transformer in self.__model.multi_head_attention.modules():
                        if isinstance(transformer, self.__Linear):
                            hook = transformer.register_forward_hook(_hook_function)
                            hooks.append(hook)
                    _ = self.__model(sample_input)
                    for hook in hooks: hook.remove()
                    DIVISION = self.__get_division(index=self.HURNET_DIVISION_METHOD)
                    if DIVISION != 'division' and self.__hidden_layers: self.addHiddenLayer(num_neurons=1, activation_function='linear')
                    for module, (X, Y) in hook_data.items():
                        try:
                            in_features, out_features = X.size(-1), Y.size(-1)
                            temporary_hurnet = self.__HurNetTransformer(input_dim=in_features, output_dim=out_features, activation_function=best_activation, interaction=best_interaction, bias=best_bias, device=self.DEVICE)
                            X_flat, Y_flat = X.reshape(-1, in_features), Y.reshape(-1, out_features)
                            temporary_hurnet.train_layer(x=X_flat, y=Y_flat, quantization=quantization, method=DIVISION, hidden_layers=self.__hidden_layers)
                            module.weight.data.copy_(temporary_hurnet.weights_data)
                            if module.bias is not None: module.bias.data.zero_()
                        except: continue
                    if hurnet_layer:
                        self.__model.hurnet_layer.activation = best_activation
                        self.__model.hurnet_layer.train_layer(x=x, y=y_onehot)
                    else:
                        initializer_hurnet_layer = self.__HurNetTransformer(input_dim=self.EMBEDDING_DIM, output_dim=self.__vocabulary_size, activation_function=best_activation, interaction=best_interaction, bias=best_bias, device=self.DEVICE)
                        initializer_hurnet_layer.train_layer(x=x, y=y_onehot, quantization=quantization, method=DIVISION, hidden_layers=self.__hidden_layers)
                        with self.__no_grad():
                            if initializer_hurnet_layer.weights.data.shape[0] >= 2: self.__model.output_layer.weight.data.copy_(initializer_hurnet_layer.weights.data[:-2, :].T)
                            elif self.EMBEDDING_DIM <= initializer_hurnet_layer.weights.data.shape[0]: self.__model.output_layer.weight.data.copy_(initializer_hurnet_layer.weights.data[:self.EMBEDDING_DIM, :].T)
                            else: self.__model.output_layer.weight.data.copy_(initializer_hurnet_layer.weights.data[:1, :].T)
                            self.__model.output_layer.bias.data.zero_()
            feed_forward, Nx, abandon, current_precision, last_val_loss, best_val_loss = True, 0, False, 0.0, 1.0, 1.0
            if progress:
                params_number = sum(parameter.numel() for parameter in self.__model.parameters())
                formatted_tokens, formatted_params = self.__format_numbers(data_number=tokens_number, is_tokens=True), self.__format_numbers(data_number=params_number, is_tokens=False)
                self.PARAMETERS_NUMBER = params_number
                if self.__loaded_model: description = f"Continuous pre-training [{formatted_tokens}/tokens, {formatted_params}/params]"
                else: description = f"Training [{formatted_tokens}/tokens, {formatted_params}/params] - HurNet: [Init: {'ON' if hurnet_initializer else 'OFF'}, Layer: {'ON' if original_hurtnet_layer else 'OFF'}, Fit: {'ON' if original_hurnet_fit else 'OFF'}]"
                progress_bar = self.__tqdm(total=total_steps, desc=description, leave=not self.__experts_training)
            while feed_forward:
                Nx += 1
                self.__model.train()
                for input_batch, target_batch in train_loader:
                    input_batch, target_batch = input_batch.to(self.DEVICE), target_batch.to(self.DEVICE)
                    if quantization is not None:
                        with self.__no_grad():
                            for parameter in self.__model.parameters():
                                if parameter.requires_grad: parameter.data = self.__tensor(parameter.data.cpu().numpy().round(quantization)).to(self.DEVICE)
                            self.__quantization = True
                    if hurnet_fit and hurnet_layer and not abandon:
                        with self.__no_grad():
                            embedded = self.__model.embedding(input_batch)
                            positions = self.__model.positional_encoding[:, :input_batch.size(1), :].to(self.DEVICE)
                            embedded = self.__model.dropout(embedded + positions) if hurnet_layer else self.__model.DROPOUT(embedded + positions)
                            mask = self.__triu(self.__ones(input_batch.size(1), input_batch.size(1), device=self.DEVICE) * float('-inf'), diagonal=1)
                            output = self.__model.multi_head_attention(embedded, memory=embedded, tgt_mask=mask)
                            x, y = output.reshape(-1, output.size(-1)), target_batch.reshape(-1)
                            y_onehot = self.__zeros(y.size(0), self.__vocabulary_size, device=self.DEVICE).scatter_(1, y.unsqueeze(1), 1)
                            self.__model.hurnet_layer.train_layer(x=x, y=y_onehot)
                            logistics = self.__model(input_batch)
                            loss = self.__Function.cross_entropy(logistics.reshape(-1, logistics.size(-1)), target_batch.reshape(-1))
                            if Nx > self.EPOCHS/4 and current_precision < 0.5:
                                abandon = True
                                if self.__optimizer is None:
                                    if type(self.WEIGHT_DECAY) == float: self.__optimizer = self.__optim.Adam(self.__model.parameters(), lr=self.LEARNING_RATE, weight_decay=self.WEIGHT_DECAY)
                                    else: self.__optimizer = self.__optim.Adam(self.__model.parameters(), lr=self.LEARNING_RATE)
                                    if self.USE_SCHEDULER:
                                        decay_target_ratio, scheduler_fraction = 0.1, 0.1
                                        if self.EPOCHS > 0:
                                            estimated_batches_per_epoch = int(self.EPOCHS * scheduler_fraction)
                                            step_size = max(1, int(estimated_batches_per_epoch))
                                            total_steps = max(1, int(self.EPOCHS / scheduler_fraction))
                                        else: step_size, total_steps = 10, 20
                                        gamma = decay_target_ratio ** (1 / total_steps)
                                        self.__set_scheduler(step_size=step_size, gamma=gamma)
                    else:
                        self.__optimizer.zero_grad()
                        logistics = self.__model(input_batch)
                        loss = self.__Function.cross_entropy(logistics.reshape(-1, logistics.size(-1)), target_batch.reshape(-1))
                        loss.backward()
                        self.__optimizer.step()
                        if self.USE_SCHEDULER and self.__scheduler: self.__scheduler.step()
                        if self.USE_BIT_NET_QUANTIZATION and Nx % len(train_loader) == 0: self.__install_quantitative_hooks()
                    loss_item = min((1.0, max((0.0, loss.item()))))
                    current_precision = 1.0-loss_item
                    if progress:
                        progress_bar.set_postfix({'loss': f'{loss_item:.4f}', 'precision': f'{current_precision:.4f}'})
                        progress_bar.update(1)
                    self.__cuda.empty_cache()
                try: last_val_loss = self.__compute_loss(loader_values) if validate > 0 else best_val_loss
                except: last_val_loss = best_val_loss
                if (self.EVAL_INTERVAL is not None and Nx > 0 and Nx % self.EVAL_INTERVAL == 0) and (last_val_loss < best_val_loss): best_val_loss = last_val_loss
                if progress: progress_bar.set_postfix({'loss': f'{loss_item:.4f}', 'precision': f'{current_precision:.4f}'})
                if current_precision >= precision or Nx >= self.EPOCHS:
                    training_metrics['loss'], training_metrics['precision'] = float(loss_item), float(current_precision)
                    break
            if progress: 
                progress_bar.n = total_steps
                progress_bar.refresh()
                progress_bar.close()
            self.__train = True
            val_loss = min((1.0, max((0.0, last_val_loss))))
            generalization_rate = min((1.0, max((0.0, 1-last_val_loss))))
            training_metrics['val_loss'], training_metrics['generalization_rate'] = float(val_loss), float(generalization_rate)
            return training_metrics
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in __unique_training: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return training_metrics if 'training_metrics' in locals() else {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
    def __get_data_dictionary(self):
        try:
            data_dictionary = {
                'attention_words': list(self.__attention_words) if type(self.__attention_words) in (tuple, list) else [],
                'tokenizer': str(self.__tokenizer).lower().strip(),
                'embedding_dim': max((1, int(self.EMBEDDING_DIM))) if type(self.EMBEDDING_DIM) in (bool, int, float) else -1,
                'vocabulary_size': max((0, int(self.__vocabulary_size))) if type(self.__vocabulary_size) in (bool, int, float) else 0,
                'block_size': max((1, int(self.BLOCK_SIZE))) if type(self.BLOCK_SIZE) in (bool, int, float) else -1,
                'infinite_context_window': max((0, int(self.__infinite_context_window))) if type(self.__infinite_context_window) in (bool, int, float) else 0,
                'end_tag': str(self.END_TAG) if self.END_TAG else '',
                'system_tag': str(self.SYSTEM_TAG) if self.SYSTEM_TAG else 'System:',
                'user_tag': str(self.USER_TAG) if self.USER_TAG else 'User:',
                'assistant_tag': str(self.ASSISTANT_TAG) if self.ASSISTANT_TAG else 'Assistant:',
                'number_heads': max((1, int(self.NUMBER_HEADS))) if type(self.NUMBER_HEADS) in (bool, int, float) else -1,
                'number_layers': max((1, int(self.NUMBER_LAYERS))) if type(self.NUMBER_LAYERS) in (bool, int, float) else -1,
                'dropout': max((0, int(self.DROPOUT))) if type(self.DROPOUT) in (bool, int, float) else 0.1,
                'tokens_number': max((0, int(self.TOKENS_NUMBER))) if type(self.TOKENS_NUMBER) in (bool, int, float) else 0,
                'parameters_number': max((0, int(self.PARAMETERS_NUMBER))) if type(self.PARAMETERS_NUMBER) in (bool, int, float) else 0,
                'architecture_type': 'hur-model',
                'model_state_dict': self.__model.state_dict() if self.__model is not None else {},
                'fine_tuning': list(self.__fine_tuning) if type(self.__fine_tuning) in (tuple, list) else [],
                'hurnet_parameters': dict(self.__hurnet_parameters) if self.__hurnet_parameters else {},
                'output_indexing': list(self.__output_indexing) if type(self.__output_indexing) in (tuple, list) else [],
                'hurnet_embedding_length': max((1, int(self.HURNET_EMBEDDING_LENGTH))) if type(self.HURNET_EMBEDDING_LENGTH) in (bool, int, float) else 25,
                'hurnet_fit_configuration': list(self.__hurnet_fit_configuration) if type(self.__hurnet_fit_configuration) in (tuple, list) else [],
                'generalization_direction': max((-1, int(self.__generalization_direction))) if type(self.__generalization_direction) in (bool, int, float) else -1,
                'quantization': int(self.__quantization) if type(self.__quantization) in (bool, int, float) else 0,
                'quantization_type': str(self.__quantization_type).upper().strip(),
                'experts': list(self.__experts) if type(self.__experts) in (tuple, list) else [],
                'date_and_time_of_creation': str(self.__date_and_time_of_creation).strip(),
                'date_and_time_of_the_last_update': str(self.__date_and_time_of_the_last_update).strip()
            }
            if self.__tokenizer.startswith('sapi'):
                data_dictionary['token_to_index'] = self.__token_to_index if type(self.__token_to_index) == dict and self.INCLUDE_VOCABULARY_IN_MODEL else {}
                data_dictionary['index_to_token'] = self.__index_to_token if type(self.__index_to_token) == dict and self.INCLUDE_VOCABULARY_IN_MODEL else {}
            return data_dictionary
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in __get_data_dictionary: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return {}
    def __train_experts(self, dataset_path='', string='', precision=1.0, tokenizer='gpt-4', context_window=None, hurnet_initializer=True, hurnet_layer=False, hurnet_fit=False, end_tag=None, stream_dataset=False, validate=0.0, quantization=None, experts=1, progress=True):
        try:
            training_metrics = {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
            if progress: progress_bar = self.__tqdm(total=experts, desc='Training with Mixture of Experts (MoE)')
            __embedding_dim = self.EMBEDDING_DIM
            __block_size = self.BLOCK_SIZE
            __batch_size = self.BATCH_SIZE
            __number_heads = self.NUMBER_HEADS
            __number_layers = self.NUMBER_LAYERS
            __epochs = self.EPOCHS
            def _split_txt_file(dataset_path='', files_number=1):
                current_file_index = 0
                current_file_path = self.__join(self.__gettempdir(), f'split_part_{current_file_index}.txt')
                total_size, buffer = self.__get_file_size(url_path=dataset_path), ''
                current_file, current_size = open(current_file_path, 'w', encoding='utf-8'), 0
                target_size, result_paths = total_size // files_number, [current_file_path]
                if progress: progress_bar_x = self.__tqdm(total=total_size, desc='Splitting data', leave=False)
                if self.__is_web_address(url_path=dataset_path):
                    response = self.__get(dataset_path, stream=True)
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=4096, decode_unicode=True):
                        buffer += chunk
                        last_split_position = 0
                        for index in range(len(buffer)):
                            if buffer[index] in '.;!?':
                                end_position = index + 1
                                segment = buffer[last_split_position:end_position]
                                if current_size + len(segment.encode('utf-8')) >= target_size and current_file_index < files_number - 1:
                                    current_file.write(segment)
                                    current_file.close()
                                    current_file_index += 1
                                    current_file_path = self.__join(self.__gettempdir(), f'split_part_{current_file_index}.txt')
                                    result_paths.append(current_file_path)
                                    current_file = open(current_file_path, 'w', encoding='utf-8')
                                    current_size = 0
                                    last_split_position = end_position
                                else:
                                    current_file.write(segment)
                                    current_size += len(segment.encode('utf-8'))
                                    last_split_position = end_position
                        buffer = buffer[last_split_position:]
                        if progress: progress_bar_x.n = len(buffer)
                else:
                    with open(dataset_path, 'r', encoding='utf-8') as input_file:
                        while True:
                            chunk = input_file.read(4096)
                            if not chunk:
                                if buffer: current_file.write(buffer)
                                break
                            buffer += chunk
                            last_split_position = 0
                            for index in range(len(buffer)):
                                if buffer[index] in '.;!?':
                                    end_position = index + 1
                                    segment = buffer[last_split_position:end_position]
                                    if current_size + len(segment.encode('utf-8')) >= target_size and current_file_index < files_number - 1:
                                        current_file.write(segment)
                                        current_file.close()
                                        current_file_index += 1
                                        current_file_path = self.__join(self.__gettempdir(), f'split_part_{current_file_index}.txt')
                                        result_paths.append(current_file_path)
                                        current_file = open(current_file_path, 'w', encoding='utf-8')
                                        current_size, last_split_position = 0, end_position
                                    else:
                                        current_file.write(segment)
                                        current_size += len(segment.encode('utf-8'))
                                        last_split_position = end_position
                            buffer = buffer[last_split_position:]
                            if progress: progress_bar_x.n = len(buffer)
                if buffer and buffer.strip():
                    if buffer[-1] not in '.;!?':
                        for index in range(len(buffer) - 1, -1, -1):
                            if buffer[index] == ' ':
                                buffer = buffer[:index]
                                break
                    current_file.write(buffer)
                current_file.close()
                if progress: 
                    progress_bar_x.n = total_size
                    progress_bar_x.refresh()
                    progress_bar_x.close()
                return result_paths
            def _split_json_file(dataset_path='', files_number=1):
                if self.__is_web_address(url_path=dataset_path): input_stream = self.__TextIOWrapper(response=self.__urlopen(dataset_path), encoding='utf-8')
                else: input_stream = open(dataset_path, 'r', encoding='utf-8')
                data = self.__json_load(input_stream)
                input_stream.close()
                key = next(iter(data))
                dictionaries = data[key]
                total_dictionaries = len(dictionaries)
                size_per_file, result_paths = total_dictionaries // files_number, []
                if progress: progress_bar_x = self.__tqdm(total=files_number, desc='Splitting data', leave=False)
                for index in range(files_number):
                    start_index = index * size_per_file
                    if index == files_number - 1: end_index = total_dictionaries
                    else: end_index = start_index + size_per_file
                    chunk = dictionaries[start_index:end_index]
                    output_data = {key: chunk}
                    file_path = self.__join(self.__gettempdir(), f'split_part_{index}.json')
                    with open(file_path, 'w', encoding='utf-8') as output_file: self.__dump(output_data, output_file, ensure_ascii=False)
                    result_paths.append(file_path)
                    if progress: progress_bar_x.n = index+1
                if progress: 
                    progress_bar_x.n = files_number
                    progress_bar_x.refresh()
                    progress_bar_x.close()
                return result_paths
            def _split_string_parts(string='', parts=1):
                total_size = len(string.encode('utf-8'))
                position, buffer, current_size = 0, '', 0
                target_size = total_size // parts
                result_parts, current_part = [], ''
                if progress: progress_bar_x = self.__tqdm(total=total_size, desc='Splitting data', leave=False)
                while position < len(string):
                    buffer += string[position:position + 4096]
                    position += 4096
                    last_split_position = 0
                    for index in range(len(buffer)):
                        if buffer[index] in '.;!?,\n':
                            end_position = index + 1
                            segment = buffer[last_split_position:end_position]
                            segment_size = len(segment.encode('utf-8'))
                            if current_size + segment_size >= target_size and len(result_parts) < parts - 1:
                                current_part += segment
                                result_parts.append(current_part.strip())
                                last_split_position = end_position
                                current_size, current_part = 0, ''
                            else:
                                last_split_position = end_position
                                current_size += segment_size
                                current_part += segment
                    buffer = buffer[last_split_position:]
                    if progress: progress_bar_x.n = len(buffer)
                if buffer.strip(): current_part += buffer
                result_parts.append(current_part.strip())
                if progress: 
                    progress_bar_x.n = total_size
                    progress_bar_x.refresh()
                    progress_bar_x.close()
                return result_parts
            def _reset_hyperparameters():
                self.EMBEDDING_DIM = __embedding_dim
                self.BLOCK_SIZE = __block_size
                self.BATCH_SIZE = __batch_size
                self.NUMBER_HEADS = __number_heads
                self.NUMBER_LAYERS = __number_layers
                self.EPOCHS = __epochs
            result_paths = _split_json_file(dataset_path=dataset_path, files_number=experts) if dataset_path.endswith('.json') else _split_txt_file(dataset_path=dataset_path, files_number=experts)
            if string: result_parts = _split_string_parts(string=string, parts=experts)
            else: result_parts = []
            attention_words, tokens_number, parameters_number = [], 0, 0
            for index, temporary_path in enumerate(result_paths):
                expert = index+1
                if progress:
                    formatted_tokens = self.__format_numbers(data_number=tokens_number, is_tokens=True)
                    formatted_params = self.__format_numbers(data_number=parameters_number, is_tokens=False)
                    progress_bar.set_postfix({'total-tokens': formatted_tokens, 'total-parameters': formatted_params, 'expert': f'{expert}/{experts}'})
                if self.__exists(temporary_path):
                    self.__experts_training = True
                    training_result = self.__unique_training(dataset_path=temporary_path, string=result_parts[index] if result_parts else string, precision=precision, tokenizer=tokenizer, context_window=context_window, hurnet_initializer=hurnet_initializer, hurnet_layer=hurnet_layer, hurnet_fit=hurnet_fit, end_tag=end_tag, stream_dataset=stream_dataset, validate=validate, quantization=quantization, progress=progress)
                    if training_result:
                        for attention_word in self.__attention_words:
                            if attention_word not in attention_words: attention_words.append(attention_word)
                        if self.__quantization: self.__model = self.__model.to(dtype=self.__float16)
                        tokens_number += self.TOKENS_NUMBER
                        parameters_number += self.PARAMETERS_NUMBER
                        if progress:
                            formatted_tokens = self.__format_numbers(data_number=tokens_number, is_tokens=True)
                            formatted_params = self.__format_numbers(data_number=parameters_number, is_tokens=False)
                            progress_bar.set_postfix({'total-tokens': formatted_tokens, 'total-parameters': formatted_params, 'expert': expert})
                        save_dict = self.__get_data_dictionary()
                        self.__experts.append(save_dict)
                        self.__string = ''
                        self.__attention_words = []
                        _reset_hyperparameters()
                        self.__token_to_index = {}
                        self.__index_to_token = {}
                        self.__encode = None
                        self.__decode = None
                        self.__model = None
                        self.__optimizer = None
                    self.__remove(temporary_path)
                    self.__experts_training = False
                if progress: progress_bar.update(1)
            self.__attention_words = attention_words
            self.TOKENS_NUMBER = tokens_number
            self.PARAMETERS_NUMBER = parameters_number
            self.EMBEDDING_DIM = -1
            self.__vocabulary_size = 0
            self.BLOCK_SIZE = -1
            self.END_TAG = ''
            self.NUMBER_HEADS = -1
            self.NUMBER_LAYERS = -1
            self.DROPOUT = 0.1
            self.__model = None
            self.__fine_tuning = []
            self.__quantization = 0
            if progress: 
                progress_bar.n = experts
                progress_bar.refresh()
                progress_bar.close()
            return training_metrics
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in __train_experts: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return training_metrics if 'training_metrics' in locals() else {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
    def __reset_model(self):
        self.__checkpoint = {}
        self.__attention_words = []
        self.__tokenizer = 'gpt-4'
        self.EMBEDDING_DIM = None
        self.__vocabulary_size = 0
        self.BLOCK_SIZE = None
        self.END_TAG = ''
        self.NUMBER_HEADS = None
        self.NUMBER_LAYERS = None
        self.DROPOUT = 0.1
        self.TOKENS_NUMBER = 0
        self.PARAMETERS_NUMBER = 0
        self.__model = None
        self.__fine_tuning = 0.5
        self.__quantization = False
        self.__experts = []
        self.__token_to_index = {}
        self.__index_to_token = {}
        self.__encode = None
        self.__decode = None
        self.__optimizer = None
        self.__train = False
        self.__loaded_model = False
    def __expert_selection(self, prompt=''):
        try:
            attention_words = self.__SapiensAttention().get_attention_words(text=prompt, maximum_length=100)
            if not attention_words: attention_words = self.__SapiensAttention().get_textual_elements(text=prompt, maximum_length=100)
            attention_list_length, maximum_occurrence, maximum_index = len(attention_words), 0, 0
            def _random_selection(index1=0, index2=1): return self.__randint(min(index1, index2), max(index1, index2)) if index1 != index2 else index1
            if self.__attention_list:
                for index, (_, expert_attention) in enumerate(self.__attention_list):
                    search, target, occurrences = (attention_words, expert_attention, 0) if attention_list_length < len(expert_attention) else (expert_attention, attention_words, 0)
                    for attention in search: occurrences += target.count(attention)
                    if occurrences > maximum_occurrence: maximum_occurrence, maximum_index = occurrences, index
                    elif occurrences == maximum_occurrence: maximum_index = _random_selection(index1=index, index2=maximum_index)
                model_path = self.__attention_list[maximum_index][0]
                self.loadModel(model_path=model_path, progress=False)
            else:
                for index, expert in enumerate(self.__experts):
                    expert_attention = list(expert.get('attention_words', []))
                    search, target, occurrences = (attention_words, expert_attention, 0) if attention_list_length < len(expert_attention) else (expert_attention, attention_words, 0)
                    for attention in search: occurrences += target.count(attention)
                    if occurrences > maximum_occurrence: maximum_occurrence, maximum_index = occurrences, index
                    elif occurrences == maximum_occurrence: maximum_index = _random_selection(index1=index, index2=maximum_index)
                most_capable_expert = self.__experts[maximum_index]
                self.__checkpoint = most_capable_expert
                self.loadModel(progress=False)
            return True
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in __expert_selection: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def __generate_tokens(self, prompt='', max_tokens=500, temperature=0.5, top_k=50, top_p=0.9, end_tag=None):
        if self.__infinite_context_window:
            tokens_number = self.__sapiens_infinite_context_window.count_tokens(text=prompt, pattern=self.__tokenizer)
            if tokens_number > self.BLOCK_SIZE: prompt = self.__sapiens_infinite_context_window.synthesize_tokens(text=prompt, maximum_tokens=self.BLOCK_SIZE, pattern=self.__tokenizer)
        return self.__generate_tokens_x(prompt=prompt if prompt else '?', max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, end_tag=end_tag)
    def train(self, dataset_path='', string='', precision=1.0, tokenizer='gpt-4', context_window=None, hurnet_initializer=True, hurnet_layer=False, hurnet_fit=False, end_tag=None, stream_dataset=False, validate=0.0, quantization=None, experts=1, progress=True):
        try:
            training_metrics = {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
            dataset_path = str(dataset_path).strip()
            string = rf'{string}'.strip()
            precision = min((1.0, max((0.0, float(precision))))) if type(precision) in (bool, int, float) else 1.0
            tokenizer = self.__sapiens_tokenizer.pattern if self.__loaded_vocabulary else str(tokenizer).lower().strip()
            if context_window is not None and context_window != float('inf'): context_window = max((8, int(context_window))) if type(context_window) in (bool, int, float) else None
            if context_window == float('inf'): self.__infinite_context_window = 1
            hurnet_initializer = bool(hurnet_initializer) if type(hurnet_initializer) in (bool, int, float) else True
            hurnet_layer = bool(hurnet_layer) if type(hurnet_layer) in (bool, int, float) else False
            hurnet_fit = bool(hurnet_fit) if type(hurnet_fit) in (bool, int, float) else False
            if end_tag and not self.END_TAG: self.END_TAG = str(end_tag)
            elif not end_tag: end_tag = self.END_TAG
            stream_dataset = bool(stream_dataset) if type(stream_dataset) in (bool, int, float) else False
            validate = min((1.0, max((0.0, float(validate))))) if type(validate) in (bool, int, float) else 0.0
            quantization = max((0, int(quantization))) if type(quantization) in (bool, int, float) else None
            self.__quantization_type = f'FP16 P{quantization}' if quantization and quantization > 0 else 'FP32'
            experts = max((1, int(experts))) if type(experts) in (bool, int, float) else 1
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if not self.__date_and_time_of_creation: self.__date_and_time_of_creation = self.__date_and_time_of_the_last_update = self.__get_date_and_time()
            else: self.__date_and_time_of_the_last_update = self.__get_date_and_time()
            if bool(quantization) and self.DEVICE.type == 'mps':
                self.DEVICE = self.__DeviceDetection().getDevice(device='cpu')
                self.__HurNetTorch = self.__HurNet(device=self.DEVICE, show_errors=False)
            if self.__add_semantic_fit:
                if self.__fine_tuning:
                    if progress:
                        progress_bar = self.__tqdm(total=3, desc='Training with semantic-fit')
                        progress_bar.update(1)
                    if self.TOKENS_NUMBER <= 0:
                        for fine_tuning in self.__fine_tuning: self.TOKENS_NUMBER += len(fine_tuning.get('prompt_embedding', []))+len(fine_tuning.get('answer_embedding', []))
                    if self.PARAMETERS_NUMBER <= 0: self.PARAMETERS_NUMBER = max(1, self.TOKENS_NUMBER//2)
                    if progress: progress_bar.update(1)
                    if self.__hidden_layers:
                        hidden_layers_length = len(self.__hidden_layers)
                        if hidden_layers_length == 1: self.__generalization_direction = 1
                        elif hidden_layers_length == 2: self.__generalization_direction = 2
                        else: self.__generalization_direction = 0
                        training_metrics['generalization_rate'] = 1.0
                    else: self.__generalization_direction = -1
                    training_metrics['precision'] = 1.0
                    if progress: progress_bar.update(1)
                if progress: 
                    progress_bar.n = 3
                    progress_bar.refresh()
                    progress_bar.close()
                self.__add_semantic_fit = False
                if not self.__add_hur_net_fit: return training_metrics
            if self.__add_hur_net_fit:
                if self.__input_layer and self.__output_layer:
                    if progress:
                        progress_bar = self.__tqdm(total=4, desc='Training with HurNet-fit')
                        progress_bar.update(1)
                    input_layer, output_layer = self.__input_layer, self.__output_layer
                    DIVISION = self.__get_division(index=self.HURNET_DIVISION_METHOD)
                    hur_net_torch_train = self.__HurNetTorch.train(input_layer=input_layer, output_layer=output_layer, quantization=quantization, method=DIVISION)
                    if hur_net_torch_train:
                        self.__hurnet_parameters = self.__HurNetTorch.getParameters()
                        training_metrics['generalization_rate'], training_metrics['precision'] = 0.0, 1.0
                    if progress: progress_bar.update(1)
                    if self.TOKENS_NUMBER <= 0:
                        for output_indexing in self.__output_indexing: self.TOKENS_NUMBER += len(output_indexing)
                    if progress: progress_bar.update(1)
                    if self.PARAMETERS_NUMBER <= 0:
                        weights_list, PARAMETERS_NUMBER = self.__hurnet_parameters.get('weights_list', []), 0
                        if weights_list:
                            PARAMETERS_NUMBER = len(weights_list)
                            if weights_list[0] and type(weights_list[0]) == list: PARAMETERS_NUMBER = PARAMETERS_NUMBER*len(weights_list[0])
                        if PARAMETERS_NUMBER <= 0: PARAMETERS_NUMBER = max(1, self.TOKENS_NUMBER//2)
                        self.PARAMETERS_NUMBER = PARAMETERS_NUMBER
                    if progress: progress_bar.update(1)
                if progress: 
                    progress_bar.n = 4
                    progress_bar.refresh()
                    progress_bar.close()
                self.__add_hur_net_fit = False
                self.__input_layer, self.__output_layer = [], []
                return training_metrics
            if experts > 1: return self.__train_experts(dataset_path=dataset_path, string=string, precision=precision, tokenizer=tokenizer, context_window=context_window, hurnet_initializer=hurnet_initializer, hurnet_layer=hurnet_layer, hurnet_fit=hurnet_fit, end_tag=end_tag, stream_dataset=stream_dataset, validate=validate, quantization=quantization, experts=experts, progress=progress)
            return self.__unique_training(dataset_path=dataset_path, string=string, precision=precision, tokenizer=tokenizer, context_window=context_window, hurnet_initializer=hurnet_initializer, hurnet_layer=hurnet_layer, hurnet_fit=hurnet_fit, end_tag=end_tag, stream_dataset=stream_dataset, validate=validate, quantization=quantization, progress=progress)
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in train: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return training_metrics if 'training_metrics' in locals() else {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
    def saveModel(self, model_path='', progress=True):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if self.__model is None and not self.__experts and not self.__fine_tuning and not self.__hurnet_parameters: raise ValueError('Model not initialized. Call train or loadModel first.')
            if len(model_path) > 0:
                directory, file_name = self.__os_path.split(model_path)
                if not file_name: file_name = 'model.hurlm'
                elif not file_name.endswith('.hurlm'): file_name += '.hurlm'
            else: directory, file_name = str(model_path), 'model.hurlm'
            if directory and not self.__os_path.exists(directory): self.__os_makedirs(directory)
            save_path = self.__os_path.join(directory, file_name)
            if self.__quantization and self.__model: self.__model = self.__model.to(dtype=self.__float16)
            save_dict = self.__get_data_dictionary()
            if progress:
                formatted_params = self.__format_numbers(data_number=self.PARAMETERS_NUMBER, is_tokens=False)
                for _ in self.__tqdm(range(10), desc=f'Saving model with {formatted_params} parameters', leave=False): self.__save(save_dict, save_path)
            else: self.__save(save_dict, save_path)
            self.__train = True
            return True
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in saveModel: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def loadVocabulary(self, vocabulary_path='', progress=True):
        try:
            load_vocabulary = False
            vocabulary_path = str(vocabulary_path).strip()
            if not vocabulary_path: return load_vocabulary
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if progress:
                progress_bar = self.__tqdm(total=3, desc='Loading vocabulary', leave=False)
                progress_bar.update(1)
            load_vocabulary = self.__sapiens_tokenizer.load_vocabulary(file_path=vocabulary_path)
            if progress: progress_bar.update(1)
            self.__tokenizer, self.__vocabulary_size = self.__sapiens_tokenizer.pattern, self.__sapiens_tokenizer.vocabulary_size
            self.__token_to_index, self.__index_to_token = self.__sapiens_tokenizer.token_to_index, self.__sapiens_tokenizer.index_to_token
            self.__loaded_vocabulary = True
            if progress: progress_bar.update(1)
            return load_vocabulary and self.__loaded_vocabulary
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in loadVocabulary: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def loadModel(self, model_path='', progress=True):
        try:
            directory, loading_error = '', False
            if self.__checkpoint: checkpoint = self.__checkpoint
            else:
                model_path = str(model_path).strip()
                progress = bool(progress) if type(progress) in (bool, int, float) else True
                if len(model_path) > 0:
                    directory, file_name = self.__os_path.split(model_path)
                    if not file_name: file_name = 'model.hurlm'
                    elif not file_name.endswith('.hurlm'): file_name += '.hurlm'
                else: directory, file_name = '', 'model.hurlm'
                model_file = self.__os_path.join(directory, file_name)
                if self.__checkpoint: checkpoint = self.__checkpoint
                try:
                    if progress:
                        for _ in self.__tqdm(range(10), desc='Loading model', leave=False): checkpoint = self.__load(model_file, map_location=self.DEVICE)
                    else: checkpoint = self.__load(model_file, map_location=self.DEVICE)
                except:
                    if progress:
                        for _ in self.__tqdm(range(10), desc='Loading model', leave=False): checkpoint = self.__load(model_file, map_location='cpu')
                    else: checkpoint = self.__load(model_file, map_location='cpu')
                    loading_error = True
            self.__attention_words = list(checkpoint.get('attention_words', []))
            self.__tokenizer = checkpoint.get('tokenizer', 'gpt-4').lower().strip()
            self.EMBEDDING_DIM = max((1, int(checkpoint.get('embedding_dim'))))
            if self.EMBEDDING_DIM == -1: self.EMBEDDING_DIM = None
            self.__vocabulary_size = max((0, int(checkpoint.get('vocabulary_size', 0))))
            self.BLOCK_SIZE = max((1, int(checkpoint.get('block_size'))))
            if self.BLOCK_SIZE == -1: self.BLOCK_SIZE = None
            self.__infinite_context_window = max((0, int(checkpoint.get('infinite_context_window', 0))))
            self.END_TAG = str(checkpoint.get('end_tag', ''))
            self.SYSTEM_TAG = str(checkpoint.get('system_tag', 'System:'))
            self.USER_TAG = str(checkpoint.get('user_tag', 'User:'))
            self.ASSISTANT_TAG = str(checkpoint.get('assistant_tag', 'Assistant:'))
            self.NUMBER_HEADS = max((1, int(checkpoint.get('number_heads', 0))))
            if self.NUMBER_HEADS == -1: self.NUMBER_HEADS = None
            self.NUMBER_LAYERS = max((1, int(checkpoint.get('number_layers', 0))))
            if self.NUMBER_LAYERS == -1: self.NUMBER_LAYERS = None
            self.DROPOUT = max((0, float(checkpoint.get('dropout', 0.1))))
            self.TOKENS_NUMBER = max((0, int(checkpoint.get('tokens_number', 0))))
            self.PARAMETERS_NUMBER = max((0, int(checkpoint.get('parameters_number', 0))))
            self.__fine_tuning = list(checkpoint.get('fine_tuning', []))
            self.__hurnet_parameters = dict(checkpoint.get('hurnet_parameters', {}))
            self.__output_indexing = list(checkpoint.get('output_indexing', []))
            self.HURNET_EMBEDDING_LENGTH = max((1, int(checkpoint.get('hurnet_embedding_length', 25))))
            self.__hurnet_fit_configuration = list(checkpoint.get('hurnet_fit_configuration', []))
            self.__generalization_direction = max((-1, int(checkpoint.get('generalization_direction', -1))))
            self.__quantization = bool(int(checkpoint.get('quantization', False)))
            self.__quantization_type = str(checkpoint.get('quantization_type', 'FP32')).upper().strip()
            self.__date_and_time_of_creation = str(checkpoint.get('date_and_time_of_creation', '')).strip()
            self.__date_and_time_of_the_last_update = str(checkpoint.get('date_and_time_of_the_last_update', '')).strip()
            if not self.__checkpoint: self.__experts = list(checkpoint.get('experts', []))
            self.__token_to_index = dict(checkpoint.get('token_to_index', {}))
            self.__index_to_token = dict(checkpoint.get('index_to_token', {}))
            self.__sapiens_tokenizer.pattern = self.__tokenizer
            self.__sapiens_tokenizer.vocabulary_size = self.__vocabulary_size
            if self.__token_to_index: self.__sapiens_tokenizer.token_to_index = self.__token_to_index
            if self.__index_to_token: self.__sapiens_tokenizer.index_to_token = self.__index_to_token
            if not self.__token_to_index and not self.__index_to_token: self.__token_to_index, self.__index_to_token = self.__sapiens_tokenizer.get_token_to_index(), self.__sapiens_tokenizer.get_index_to_token()
            elif not self.__token_to_index and self.__index_to_token: self.__token_to_index = self.__sapiens_tokenizer.key_to_value(dictionary=self.__index_to_token)
            elif not self.__index_to_token and self.__token_to_index: self.__index_to_token = self.__sapiens_tokenizer.key_to_value(dictionary=self.__token_to_index)
            vocabulary_path = self.__os_path.join(directory, 'vocabulary.json')
            if self.__exists(vocabulary_path):
                self.__sapiens_tokenizer.load_vocabulary(file_path=vocabulary_path)
                self.__tokenizer, self.__vocabulary_size = self.__sapiens_tokenizer.pattern, self.__sapiens_tokenizer.vocabulary_size
                self.__token_to_index, self.__index_to_token = self.__sapiens_tokenizer.token_to_index, self.__sapiens_tokenizer.index_to_token
                self.__loaded_vocabulary = True
            if self.__tokenizer.startswith('sapi'):
                if self.__tokenizer != 'sapi-0':
                    if self.__tokenizer == 'sapi-1': tokens_length = 2
                    elif self.__tokenizer == 'sapi-2': tokens_length = 3
                    elif self.__tokenizer == 'sapi-3': tokens_length = 4
                    elif self.__tokenizer == 'sapi-4': tokens_length = 5
                    else: tokens_length = 0
                    if tokens_length >= 2: text_to_list = self.__sapiens_tokenizer._SapiensTokenizer__text_to_list
                    else: text_to_list = self.__sapiens_tokenizer._SapiensTokenizer__text_to_list_sapi5
                    self.__encode = lambda strings: [self.__token_to_index[token] for token in text_to_list(text=strings, tokens_length=tokens_length, is_sorted=False)]
                else: self.__encode = lambda strings: [self.__token_to_index[token] for token in strings]
                self.__decode = lambda indexes: ''.join([self.__index_to_token[str(index)] for index in indexes])
                self.__sapiens_tokenizer.encode, self.__sapiens_tokenizer.decode = self.__encode, self.__decode
            else:
                self.__encode = self.__sapiens_tokenizer.get_encode(pattern=self.__tokenizer)
                self.__decode = self.__sapiens_tokenizer.get_decode(pattern=self.__tokenizer)
            self.__pad_token_id = self.__sapiens_tokenizer.to_encode(text_data=chr(32), pattern=self.__tokenizer)
            state_dict = dict(checkpoint.get('model_state_dict', {}))
            if state_dict:
                has_hurnet = 'hurnet_layer.weights' in state_dict
                if has_hurnet: self.__model = self.__TransformerHurNet(embedding_dim=self.EMBEDDING_DIM, block_size=self.BLOCK_SIZE, number_heads=self.NUMBER_HEADS, number_layers=self.NUMBER_LAYERS, dropout=self.DROPOUT, vocab_size=self.__vocabulary_size, device=self.DEVICE, outer=self).to(self.DEVICE)
                else: self.__model = self.__Transformer(embedding_dim=self.EMBEDDING_DIM, block_size=self.BLOCK_SIZE, number_heads=self.NUMBER_HEADS, number_layers=self.NUMBER_LAYERS, dropout=self.DROPOUT, vocab_size=self.__vocabulary_size, outer=self).to(self.DEVICE)
                if loading_error: self.__model.to(device=self.DEVICE)
                if self.__quantization: self.__model.to(device=self.DEVICE, dtype=self.__float16)
                self.__model.load_state_dict(state_dict)
            self.__set_last_user_id(id=0)
            self.__optimizer, self.__train, self.__loaded_model = None, True, True
            return True
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in loadModel: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def describeModel(self, model_path='', show=True, progress=True):
        try:
            descriptive_dictionary = {
                'TOKENIZER': '',
                'EMBEDDING_DIM': 0,
                'VOCABULARY_SIZE': 0,
                'BLOCK_SIZE': 0,
                'CONTEXT_WINDOW': 0,
                'END_TAG': '',
                'SYSTEM_TAG': '',
                'USER_TAG': '',
                'ASSISTANT_TAG': '',
                'NUMBER_HEADS': 0,
                'NUMBER_LAYERS': 0,
                'DROPOUT': 0,
                'TOKENS_NUMBER': 0,
                'PARAMETERS_NUMBER': 0,
                'SEMANTIC_FINE_TUNING': '',
                'HURNET_FINE_TUNING': '',
                'HURNET_EMBEDDING_LENGTH': 0,
                'QUANTIZATION_TYPE': '',
                'EXPERTS': 0,
                'DATE_AND_TIME_OF_CREATION': '',
                'DATE_AND_TIME_OF_THE_LAST_UPDATE': ''
            }
            show = bool(show) if type(show) in (bool, int, float) else True
            self.loadModel(model_path=model_path, progress=progress)
            descriptive_dictionary['EXPERTS'] = EXPERTS = len(self.__experts)
            if EXPERTS > 0:
                checkpoint = self.__experts[0]
                descriptive_dictionary['TOKENIZER'] = TOKENIZER = checkpoint.get('tokenizer', '').upper().strip()
                descriptive_dictionary['EMBEDDING_DIM'] = EMBEDDING_DIM = checkpoint.get('embedding_dim', 0)
                vocabulary_size = checkpoint.get('vocabulary_size', 0)
                descriptive_dictionary['VOCABULARY_SIZE'] = VOCABULARY_SIZE = vocabulary_size if vocabulary_size > 0 else 'INDEFINITE'
                descriptive_dictionary['BLOCK_SIZE'] = BLOCK_SIZE = checkpoint.get('block_size', 0)
                infinite_context_window = checkpoint.get('infinite_context_window', 0)
                descriptive_dictionary['CONTEXT_WINDOW'] = CONTEXT_WINDOW = 'INFINITE' if infinite_context_window > 0 else BLOCK_SIZE
                descriptive_dictionary['END_TAG'] = END_TAG = checkpoint.get('end_tag', '').strip()
                descriptive_dictionary['SYSTEM_TAG'] = SYSTEM_TAG = checkpoint.get('system_tag', 'System:')
                descriptive_dictionary['USER_TAG'] = USER_TAG = checkpoint.get('user_tag', 'User:')
                descriptive_dictionary['ASSISTANT_TAG'] = ASSISTANT_TAG = checkpoint.get('assistant_tag', 'Assistant:')
                descriptive_dictionary['NUMBER_HEADS'] = NUMBER_HEADS = checkpoint.get('number_heads', 0)
                descriptive_dictionary['NUMBER_LAYERS'] = NUMBER_LAYERS = checkpoint.get('number_layers', 0)
                descriptive_dictionary['DROPOUT'] = DROPOUT = checkpoint.get('dropout', 0)
            else:
                descriptive_dictionary['TOKENIZER'] = TOKENIZER = self.__tokenizer.upper().strip()
                descriptive_dictionary['EMBEDDING_DIM'] = EMBEDDING_DIM = self.EMBEDDING_DIM
                descriptive_dictionary['VOCABULARY_SIZE'] = VOCABULARY_SIZE = self.__vocabulary_size if self.__vocabulary_size > 0 else 'INDEFINITE'
                descriptive_dictionary['BLOCK_SIZE'] = BLOCK_SIZE = self.BLOCK_SIZE
                descriptive_dictionary['CONTEXT_WINDOW'] = CONTEXT_WINDOW = 'INFINITE' if self.__infinite_context_window > 0 else BLOCK_SIZE
                descriptive_dictionary['END_TAG'] = END_TAG = self.END_TAG
                descriptive_dictionary['SYSTEM_TAG'] = SYSTEM_TAG = self.SYSTEM_TAG
                descriptive_dictionary['USER_TAG'] = USER_TAG = self.USER_TAG
                descriptive_dictionary['ASSISTANT_TAG'] = ASSISTANT_TAG = self.ASSISTANT_TAG
                descriptive_dictionary['NUMBER_HEADS'] = NUMBER_HEADS = self.NUMBER_HEADS
                descriptive_dictionary['NUMBER_LAYERS'] = NUMBER_LAYERS = self.NUMBER_LAYERS
                descriptive_dictionary['DROPOUT'] = DROPOUT = self.DROPOUT
            descriptive_dictionary['TOKENS_NUMBER'] = TOKENS_NUMBER = f'{self.TOKENS_NUMBER}/{self.getTokensNumber(formatted=True)}'
            descriptive_dictionary['PARAMETERS_NUMBER'] = PARAMETERS_NUMBER = f'{self.PARAMETERS_NUMBER}/{self.getParametersNumber(formatted=True)}'
            descriptive_dictionary['SEMANTIC_FINE_TUNING'] = FINE_TUNING = 'YES' if self.__fine_tuning else 'NO'
            descriptive_dictionary['HURNET_FINE_TUNING'] = HURNET_FINE_TUNING = 'YES' if self.__hurnet_parameters else 'NO'
            descriptive_dictionary['HURNET_EMBEDDING_LENGTH'] = HURNET_EMBEDDING_LENGTH = self.HURNET_EMBEDDING_LENGTH
            descriptive_dictionary['QUANTIZATION_TYPE'] = QUANTIZATION_TYPE = self.__quantization_type.upper().strip()
            date_and_time_of_creation = self.__date_and_time_of_creation
            if not date_and_time_of_creation: date_and_time_of_creation = self.__get_date_and_time()
            descriptive_dictionary['DATE_AND_TIME_OF_CREATION'] = DATE_AND_TIME_OF_CREATION = date_and_time_of_creation.strip()
            date_and_time_of_the_last_update = self.__date_and_time_of_the_last_update
            if not date_and_time_of_the_last_update: date_and_time_of_the_last_update = self.__get_date_and_time()
            descriptive_dictionary['DATE_AND_TIME_OF_THE_LAST_UPDATE'] = DATE_AND_TIME_OF_THE_LAST_UPDATE = date_and_time_of_the_last_update.strip()
            if show:
                print(f'TOKENIZER: "{TOKENIZER}"')
                print('EMBEDDING_DIM:', EMBEDDING_DIM)
                print('VOCABULARY_SIZE:', VOCABULARY_SIZE)
                print('BLOCK_SIZE:', BLOCK_SIZE)
                print('CONTEXT_WINDOW:', CONTEXT_WINDOW)
                print(f'END_TAG: "{END_TAG}"')
                print(f'SYSTEM_TAG: "{SYSTEM_TAG}"')
                print(f'USER_TAG: "{USER_TAG}"')
                print(f'ASSISTANT_TAG: "{ASSISTANT_TAG}"')
                print('NUMBER_HEADS:', NUMBER_HEADS)
                print('NUMBER_LAYERS:', NUMBER_LAYERS)
                print('DROPOUT:', DROPOUT)
                print(f'TOKENS_NUMBER: "{TOKENS_NUMBER}"')
                print(f'PARAMETERS_NUMBER: "{PARAMETERS_NUMBER}"')
                print(f'SEMANTIC_FINE_TUNING: "{FINE_TUNING}"')
                print(f'HURNET_FINE_TUNING: "{HURNET_FINE_TUNING}"')
                print('HURNET_EMBEDDING_LENGTH:', HURNET_EMBEDDING_LENGTH)
                print(f'QUANTIZATION_TYPE: "{QUANTIZATION_TYPE}"')
                print('EXPERTS:', EXPERTS)
                print(f'DATE_AND_TIME_OF_CREATION: "{DATE_AND_TIME_OF_CREATION}"')
                print(f'DATE_AND_TIME_OF_THE_LAST_UPDATE: "{DATE_AND_TIME_OF_THE_LAST_UPDATE}"')
            return descriptive_dictionary
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in describeModel: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return descriptive_dictionary if 'descriptive_dictionary' in locals() else {}
    def loadExperts(self, model_paths=[], progress=True):
        try:
            experts_loaded = False
            model_paths = list(model_paths) if type(model_paths) in (tuple, list) else str(model_paths).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if progress:
                progress_bar = self.__tqdm(total=3, desc='Loading experts', leave=False)
                progress_bar.update(1)
            if type(model_paths) == str and self.__isdir(model_paths):
                def _get_hurlm_files(model_paths=''):
                    models_directory = self.__Path(model_paths)
                    return [str(file) for file in models_directory.rglob('*.hurlm') if file.is_file()]
                model_paths = _get_hurlm_files(model_paths=model_paths)
            if progress: progress_bar.update(1)
            if type(model_paths) == list:
                def _extract_attention_words(model_path=''):
                    checkpoint = self.__load(model_path, map_location=self.DEVICE)
                    attention_words = list(checkpoint.get('attention_words', []))
                    del checkpoint
                    self.__collect()
                    return attention_words
                self.__attention_list = []
                for model_path in model_paths:
                    if self.__exists(model_path):
                        attention_words = _extract_attention_words(model_path=model_path)
                        self.__attention_list.append((model_path, attention_words))
                experts_loaded = True
            if progress: progress_bar.update(1)
            if progress:
                progress_bar.n = 3
                progress_bar.refresh()
                progress_bar.close()
            return experts_loaded
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in loadExperts: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def transferLearning(self, transmitter_path='', receiver_path='', progress=True):
        try:
            save_model = False
            transmitter_path, receiver_path = str(transmitter_path).strip(), str(receiver_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if not self.__exists(transmitter_path) or not self.__exists(receiver_path): return False
            if progress:
                transmitter, receiver = self.__basename(transmitter_path), self.__basename(receiver_path)
                progress_bar = self.__tqdm(total=7, desc=f'Transferring learning from {transmitter} to {receiver}')
            if progress: progress_bar.update(1)
            load_model = self.loadModel(model_path=transmitter_path, progress=progress)
            if progress: progress_bar.update(1)
            if load_model:
                transmission_model, attention_words = self.__get_data_dictionary(), []
                if transmission_model:
                    self.__reset_model()
                    for attention_word in list(transmission_model.get('attention_words', [])):
                        if attention_word not in attention_words: attention_words.append(attention_word)
                    tokens_number = max((0, int(transmission_model.get('tokens_number', 0))))
                    parameters_number = max((0, int(transmission_model.get('parameters_number', 0))))
                    experts = list(transmission_model.get('experts', []))
                    transmission_structure = experts if experts else [transmission_model]
                    if progress: progress_bar.update(1)
                    if transmission_structure:
                        load_model = self.loadModel(model_path=receiver_path, progress=progress)
                        if progress: progress_bar.update(1)
                        if load_model:
                            receiving_model = self.__get_data_dictionary()
                            if receiving_model:
                                self.__reset_model()
                                for attention_word in list(receiving_model.get('attention_words', [])):
                                    if attention_word not in attention_words: attention_words.append(attention_word)
                            tokens_number += max((0, int(receiving_model.get('tokens_number', 0))))
                            parameters_number += max((0, int(receiving_model.get('parameters_number', 0))))
                            experts = list(receiving_model.get('experts', []))
                            receiving_structure = experts if experts else [receiving_model]
                            if receiving_structure:
                                if progress: progress_bar.update(1)
                                union_structure = transmission_structure+receiving_structure
                                self.__attention_words = attention_words
                                self.TOKENS_NUMBER = tokens_number
                                self.PARAMETERS_NUMBER = parameters_number
                                self.__experts = union_structure
                                if progress: progress_bar.update(1)
                                if union_structure: save_model = self.saveModel(model_path=receiver_path, progress=progress)
                                if progress: progress_bar.update(1)
            if progress:
                progress_bar.n = 7
                progress_bar.refresh()
                progress_bar.close()
            return save_model
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in transferLearning: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def modelsUnion(self, model_paths=[], result_path='', progress=True):
        try:
            result_model = False
            if type(model_paths) == str:
                model_paths = model_paths.strip()
                if self.__isdir(model_paths):
                    models_directory = self.__Path(model_paths)
                    model_paths = [str(file) for file in models_directory.rglob('*.hurlm') if file.is_file()]
            model_paths = list(model_paths) if type(model_paths) in (tuple, list) else []
            if not model_paths: return False
            result_path = str(result_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            model_count = len(model_paths)
            if progress: progress_bar = self.__tqdm(total=model_count, desc=f'Uniting models')
            attention_words, loading_structure = [], []
            tokens_number, parameters_number = 0, 0
            for model_path in model_paths:
                load_model = self.loadModel(model_path=model_path, progress=progress)
                if load_model:
                    loaded_model = self.__get_data_dictionary()
                    if loaded_model:
                        self.__reset_model()
                        for attention_word in list(loaded_model.get('attention_words', [])):
                            if attention_word not in attention_words: attention_words.append(attention_word)
                        tokens_number += max((0, int(loaded_model.get('tokens_number', 0))))
                        parameters_number += max((0, int(loaded_model.get('parameters_number', 0))))
                        experts = list(loaded_model.get('experts', []))
                        loading_structure += experts if experts else [loaded_model]
                if progress: progress_bar.update(1)
            self.__attention_words = attention_words
            self.TOKENS_NUMBER = tokens_number
            self.PARAMETERS_NUMBER = parameters_number
            self.__experts = loading_structure
            if loading_structure: result_model = self.saveModel(model_path=result_path, progress=progress)
            if progress:
                progress_bar.n = model_count
                progress_bar.refresh()
                progress_bar.close()
            return result_model
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in modelsUnion: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def getTokensNumber(self, formatted=True):
        try:
            formatted = bool(formatted) if type(formatted) in (bool, int, float) else True
            return self.__format_numbers(data_number=self.TOKENS_NUMBER, is_tokens=True) if formatted else self.TOKENS_NUMBER
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in getTokensNumber: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return 0
    def getParametersNumber(self, formatted=True):
        try:
            formatted = bool(formatted) if type(formatted) in (bool, int, float) else True
            return self.__format_numbers(data_number=self.PARAMETERS_NUMBER, is_tokens=False) if formatted else self.PARAMETERS_NUMBER
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in getParametersNumber: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return 0
    def addHiddenLayer(self, num_neurons=1, activation_function='linear'):
        try:
            num_neurons = max((1, int(num_neurons))) if type(num_neurons) in (bool, int, float) else 1
            activation_function = str(activation_function).lower().strip()
            self.__hidden_layers.append((num_neurons, activation_function))
            return self.__HurNetTorch.addHiddenLayer(num_neurons=num_neurons, activation_function=activation_function)
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in addHiddenLayer: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def addFit(self, prompt='', answer=''):
        try:
            prompt, answer = rf'{prompt}'.strip(), rf'{answer}'.strip()
            if not prompt or not answer: return False
            if not self.END_TAG: self.END_TAG = '<|end|>'
            answer += self.END_TAG+'\n\n'
            if not self.__train: self.__string += rf'{prompt}'+'\n'+rf'{answer}'
            else:
                if self.__model is None: raise ValueError('Model is not initialized. Call train or loadModel first.')
                if self.__optimizer is None:
                    if type(self.WEIGHT_DECAY) == float: self.__optimizer = self.__optim.AdamW(self.__model.parameters(), lr=self.LEARNING_RATE, weight_decay=self.WEIGHT_DECAY)
                    else: self.__optimizer = self.__optim.AdamW(self.__model.parameters(), lr=self.LEARNING_RATE)
                    if self.USE_SCHEDULER:
                        estimated_total_calls, desired_lr_drop_ratio, scheduler_reductions = self.EPOCHS if self.EPOCHS is not None else 10, 0.1, 10
                        step_size = max(1, int(estimated_total_calls / scheduler_reductions))
                        gamma = desired_lr_drop_ratio ** (1 / scheduler_reductions)
                        self.__set_scheduler(step_size=step_size, gamma=gamma)
                formatted = prompt+'\n'+answer+self.END_TAG+'\n\n'
                coded_pairs = self.__encode(formatted)
                encoding_length = len(coded_pairs)
                if encoding_length > self.BLOCK_SIZE: coded_pairs = coded_pairs[:self.BLOCK_SIZE]
                elif encoding_length < self.BLOCK_SIZE: coded_pairs += self.__pad_token_id * (self.BLOCK_SIZE - encoding_length)
                input_tensor = self.__tensor(coded_pairs[:-1], dtype=self.__int64).unsqueeze(0).to(self.DEVICE)
                target_tensor = self.__tensor(coded_pairs[1:], dtype=self.__int64).unsqueeze(0).to(self.DEVICE)
                self.__inputs_targets.append([input_tensor, target_tensor])
                self.__prompts.append(prompt), self.__answers.append(answer)
                self.__encoding_length, self.__adjustment_data = encoding_length, True
            full_content = prompt+' '+answer
            attention_words = self.__SapiensAttention().get_attention_words(text=full_content, maximum_length=10)
            for attention_word in attention_words:
                if attention_word not in self.__attention_words: self.__attention_words.append(attention_word)
            return True
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in addFit: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def addSemanticFit(self, prompt='', answer='', precision=0.5, id=0, relationship_id=0):
        try:
            prompt, answer = rf'{prompt}'.strip(), rf'{answer}'.strip()
            if not prompt or not answer: return False
            precision = min((1.0, max((0.0, float(precision))))) if type(precision) in (bool, int, float) else 0.5
            id = int(id) if type(id) in (bool, int, float) else 0
            relationship_id = int(relationship_id) if type(relationship_id) in (bool, int, float) else 0
            prompt_embedding, answer_embedding = self.__sapiens_embedding.text_to_embedding(text_data=prompt, pattern=self.__tokenizer), self.__sapiens_embedding.text_to_embedding(text_data=answer, pattern=self.__tokenizer)
            self.__fine_tuning.append({'prompt_embedding': prompt_embedding, 'answer_embedding': answer_embedding, 'precision': precision, 'id': id, 'relationship_id': relationship_id})
            self.__add_semantic_fit = True
            full_content = prompt+' '+answer
            attention_words = self.__SapiensAttention().get_attention_words(text=full_content, maximum_length=10)
            for attention_word in attention_words:
                if attention_word not in self.__attention_words: self.__attention_words.append(attention_word)
            return True
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in addSemanticFit: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def addHurNetFit(self, prompt='', answer='', precision=0.5, id=0, relationship_id=0):
        try:
            prompt, answer = rf'{prompt}'.strip(), rf'{answer}'.strip()
            if not prompt or not answer: return False
            precision = min((1.0, max((0.0, float(precision))))) if type(precision) in (bool, int, float) else 0.5
            id = int(id) if type(id) in (bool, int, float) else 0
            relationship_id = int(relationship_id) if type(relationship_id) in (bool, int, float) else 0
            if relationship_id > 0 and not self.__hidden_layers: return self.addSemanticFit(prompt=prompt, answer=answer, precision=precision, id=id, relationship_id=relationship_id)
            embedding_length = max((1, int(self.HURNET_EMBEDDING_LENGTH))) if type(self.HURNET_EMBEDDING_LENGTH) in (bool, int, float) else 1
            prompt_embedding = self.__sapiens_embedding.text_to_embedding(text_data=self.__SCN.normalization(input_text=prompt), length=embedding_length, pattern=self.__tokenizer, method='average')
            answer_embedding = self.__sapiens_embedding.text_to_embedding(text_data=answer, length=None, pattern=self.__tokenizer)
            self.__input_layer.append(prompt_embedding)
            self.__output_layer.append([len(self.__output_layer)])
            self.__output_indexing.append(answer_embedding)
            self.__hurnet_fit_configuration.append({'precision': precision, 'id': id, 'relationship_id': relationship_id})
            self.__add_hur_net_fit = True
            full_content = prompt+' '+answer
            attention_words = self.__SapiensAttention().get_attention_words(text=full_content, maximum_length=10)
            for attention_word in attention_words:
                if attention_word not in self.__attention_words: self.__attention_words.append(attention_word)
            return True
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in addHurNetFit: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return False
    def predict(self, prompt='', max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            prompt = rf'{prompt}'.strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, float(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream, expert_selection = bool(stream) if type(stream) in (bool, int, float) else False, False
            if len(self.__experts) > 0 or len(self.__attention_list) > 0: expert_selection = self.__expert_selection(prompt=prompt)
            if self.__model is None and not expert_selection and not self.__fine_tuning and not self.__hurnet_parameters: raise ValueError('Model not initialized. Call train or loadModel first.')
            self.END_TAG = rf'{self.END_TAG}'
            self.SYSTEM_TAG = rf'{self.SYSTEM_TAG}'
            self.USER_TAG = rf'{self.USER_TAG}'
            self.ASSISTANT_TAG = rf'{self.ASSISTANT_TAG}'
            generated_tokens = self.__generate_tokens(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, end_tag=self.END_TAG)
            if stream: return generated_tokens
            else:
                tokens = []
                for token in generated_tokens: tokens.append(token) if token else tokens.append('')
                decoded_tokens = ''.join(tokens)
                end_tag, system_tag = self.END_TAG, self.SYSTEM_TAG
                user_tag, assistant_tag = self.USER_TAG, self.ASSISTANT_TAG
                if end_tag and end_tag in decoded_tokens: decoded_tokens = decoded_tokens.split(end_tag)[0].strip()
                if user_tag and user_tag in decoded_tokens: decoded_tokens = decoded_tokens.split(user_tag)[0].strip()
                if assistant_tag and assistant_tag in decoded_tokens: decoded_tokens = decoded_tokens.split(assistant_tag)[-1].strip()
                if system_tag and system_tag in decoded_tokens: decoded_tokens = decoded_tokens.split(system_tag)[-1].strip()
                return decoded_tokens.strip()
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in predict: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return ''
    def predictMessages(self, prompt='', messages=[], max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            result_dictionary = {'answer': '', 'messages': []}
            prompt = rf'{prompt}'.strip()
            messages = list(messages) if type(messages) in (tuple, list) else []
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, float(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            last_message, user_message = messages[-1] if messages else {}, {'role': 'user', 'content': prompt}
            last_message_values = list(last_message.values())
            last_message_values_0 = last_message_values[0] if last_message_values else '-'
            system_tag = str(self.SYSTEM_TAG).lower().strip()
            user_tag = str(self.USER_TAG).lower().strip()
            assistant_tag = str(self.ASSISTANT_TAG).lower().strip()
            if 'user' not in last_message_values and last_message_values_0 not in user_tag: messages.append(user_message)
            if self.__infinite_context_window: messages = self.__sapiens_infinite_context_window.synthesize_messages(prompt=prompt, messages=messages, maximum_tokens=self.BLOCK_SIZE, pattern=self.__tokenizer, keys=('content',))['synthesis']
            result_dictionary['messages'] = messages
            entity_key, content_key = 'role', 'content'
            entity_vale, content_value = 'user', ''
            original_assistant_entity, prompt = 'assistant', ''
            for message in messages:
                if message:
                    keys = list(message.keys())
                    entity_key, content_key = keys[0], keys[-1]
                    entity_vale, content_value = str(message[entity_key]).lower().strip(), rf'{message[content_key]}'.strip()
                    if entity_vale and content_value:
                        if entity_vale in system_tag or entity_vale == 'system': prompt += f'{self.SYSTEM_TAG}\n{content_value}\n'
                        elif entity_vale in user_tag or entity_vale == 'user': prompt += f'{self.USER_TAG}\n{content_value}\n'
                        elif entity_vale in assistant_tag or entity_vale == 'assistant':
                            original_assistant_entity = entity_vale
                            prompt += f'{self.ASSISTANT_TAG}\n{content_value}\n'
            prompt += self.ASSISTANT_TAG
            def _predict():
                generated_tokens = self.predict(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, stream=stream)
                if stream: return generated_tokens
                else:
                    tokens = []
                    for token in generated_tokens: tokens.append(token) if token else tokens.append('')
                    decoded_tokens = ''.join(tokens)
                    return decoded_tokens
            def _get_generator():
                response = _predict()
                model_answer = ''
                result_dictionary['messages'].append({entity_key: original_assistant_entity, content_key: model_answer})
                for token in response:
                    model_answer += token
                    result_dictionary['answer'] = model_answer
                    assistant_message = {entity_key: original_assistant_entity, content_key: model_answer}
                    result_dictionary['messages'][-1] = assistant_message
                    yield result_dictionary
                return
            if stream: return _get_generator()
            response = _predict()
            result_dictionary['answer'] = response
            result_dictionary['messages'].append({entity_key: original_assistant_entity, content_key: response})
            return result_dictionary
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in predictMessages: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
            return result_dictionary if 'result_dictionary' in locals() else {'answer': '', 'messages': []}
    def print_predict(self, prompt='', max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            prompt = rf'{prompt}'.strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, float(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            generated_tokens = self.predict(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, stream=stream)
            if stream:
                first_token = True
                for token in generated_tokens:
                    if not token: continue
                    if first_token:
                        print(token.lstrip(), end='', flush=True)
                        first_token = False
                    else: print(token, end='', flush=True)
                print()
            else: print(generated_tokens)
        except Exception as error:
            if self.SHOW_ERROR: print('ERROR in print_predict: ' + str(error))
            if self.SHOW_ERROR_DETAILS: self.__SHOW_ERROR_DETAILS()
"""
This algorithm proposes a new paradigm in language model architecture, aiming to revolutionize natural language processing through direct weights adjustment and automatic parameter configuration.
The Hur-Model is a development module that implements this concept, enabling the training, retraining, tuning, and inference of language models in a groundbreaking way.
It reduces dependence on backpropagation through an initial weight adjustment using a HurNet network and accelerates model parameterization through optimization calculations and self-configuration.
This code was architected, developed, and programmed by Ben-Hur Varriano for Sapiens Technology®️.
Any use, modification, disclosure, or public commentary without prior authorization from Sapiens Technology®️ will be subject to legal action by our legal team.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
