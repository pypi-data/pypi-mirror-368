# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
# class to apply generalization to language models responses based on the comparison between the original input and the user input
class SapiensGeneralization:
	def __init__(self):
	    from unicodedata import normalize, combining
	    from string import punctuation
	    self.__normalize = normalize
	    self.__combining = combining
	    self.__punctuation = punctuation
	def __replace(self, all_strings='', old_string='', new_string=''):
		try:
			if not all_strings or not old_string: return all_strings
			def _remove_punctuation_end(text=''):
			    while text and text[-1] in self.__punctuation: text = text[:-1]
			    return text
			tokens = all_strings.split()
			for index, token in  enumerate(tokens):
				if token and old_string == _remove_punctuation_end(text=token): tokens[index] = tokens[index].replace(old_string, new_string)
			all_strings = chr(32).join(tokens)
		except Exception as error: print('ERROR in SapiensGeneralization.__replace: ' + str(error))
		finally: return all_strings
	def generalization(self, prompt='', original_input='', original_output='', direction=0):
		try:
		    prompt = str(prompt).strip()
		    original_input = str(original_input).strip()
		    original_output = str(original_output).strip()
		    adapted_output = original_output
		    if direction not in (0, 1, 2, 'left', 'right', 'bidirectional'): direction = 0
		    if type(direction) == str:
		        direction = direction.lower()
		        if direction == 'left': direction = 0
		        elif direction == 'right': direction = 2
		        elif direction == 'bidirectional': direction = 1
		    entry_tokens = prompt.split()
		    input_tokens = original_input.split()
		    output_tokens = original_output.split()
		    def _normalize_string(string='', only_punctuation=False):
		        def __normalize_token(token='', only_punctuation=False):
		            from unicodedata import normalize, combining
		            from string import punctuation
		            if not only_punctuation:
		                if len(token) > 1: token = ''.join(character for character in normalize('NFKD', token) if not combining(character))
		            return ''.join(character for character in token if character not in punctuation)
		        if not only_punctuation: string = string.lower()
		        return ' '.join([__normalize_token(token=token, only_punctuation=only_punctuation).strip() for token in string.strip().split()])
		    def _find_in_list(vector=[], value=''):
		        try: return vector.index(value)
		        except: return -1
		    def _get_values(tokens=[], index=0, direction=1):
		        if direction == 1: index_1, index_2 = index-1, index+1
		        elif direction == 0: index_1, index_2 = index-1, index
		        else: index_1, index_2 = index, index+1
		        index_1 = min((len(tokens)-1, max((0, index_1))))
		        index_2 = min((len(tokens)-1, max((0, index_2))))
		        return tokens[index_1], tokens[index_2]
		    prompt = _normalize_string(string=prompt, only_punctuation=False)
		    original_input = _normalize_string(string=original_input, only_punctuation=False)
		    original_output = _normalize_string(string=original_output, only_punctuation=False)
		    prompt_tokens = prompt.split()
		    original_input_tokens = original_input.split()
		    original_output_tokens = original_output.split()
		    original_input_length = len(original_input_tokens)
		    entry_tokens_length = len(entry_tokens)
		    input_tokens_length = len(input_tokens)
		    for index_1, token_1 in enumerate(prompt_tokens):
		        if direction == 1:
		            value_x1, value_x2 = _get_values(tokens=prompt_tokens, index=index_1, direction=direction)
		            if value_x1 in original_input_tokens and value_x2 in original_input_tokens:
		                index_2 = _find_in_list(vector=original_input_tokens, value=value_x1)
		                index_3 = _find_in_list(vector=original_input_tokens, value=value_x2)
		                if index_2 >= 0 and index_3 >= 0:
		                    index_2x = min((original_input_length-1, index_2+2))
		                    index_3x = max((0, index_3-2))
		                    if original_input_tokens[index_2x] == value_x2 and original_input_tokens[index_3x] == value_x1:
		                        index_2y = min((original_input_length-1, index_2+1))
		                        token_2 = original_input_tokens[index_2y]
		                        if token_2.lower() in adapted_output: adapted_output = self.__replace(all_strings=adapted_output, old_string=token_2.lower(), new_string=token_1.lower())
		                        elif token_2.upper() in adapted_output: adapted_output = self.__replace(all_strings=adapted_output, old_string=token_2.upper(), new_string=token_1.upper())
		                        elif token_2.title() in adapted_output: adapted_output = self.__replace(all_strings=adapted_output, old_string=token_2.title(), new_string=token_1.title())
		        elif token_1 in original_input_tokens:
		            index_2 = _find_in_list(vector=original_input_tokens, value=token_1)
		            if index_2 >= 0:
		                value_x1, value_x2 = _get_values(tokens=prompt_tokens, index=index_1, direction=direction)
		                value_y1, value_y2 = _get_values(tokens=original_input_tokens, index=index_2, direction=direction)
		                if value_x1 != value_x2 and value_y1 != value_y2 and value_x1 == value_y1 and value_x2 == value_y2:
		                    if direction == 0: index_x1, index_x2 = index_1+1, index_2+1
		                    else: index_x1, index_x2 = index_1-1, index_2-1
		                    if index_x1 >=0 and index_x2 >= 0:
		                        index_x1 = min((entry_tokens_length-1, index_x1))
		                        index_x2 = min((input_tokens_length-1, index_x2))
		                        token_2 = _normalize_string(string=entry_tokens[index_x1], only_punctuation=True)
		                        token_3 = _normalize_string(string=input_tokens[index_x2], only_punctuation=True)
		                        if token_2 != token_3:
		                            if token_3.lower() in adapted_output: adapted_output = self.__replace(all_strings=adapted_output, old_string=token_3.lower(), new_string=token_2.lower())
		                            elif token_3.upper() in adapted_output: adapted_output = self.__replace(all_strings=adapted_output, old_string=token_3.upper(), new_string=token_2.upper())
		                            elif token_3.title() in adapted_output: adapted_output = self.__replace(all_strings=adapted_output, old_string=token_3.title(), new_string=token_2.title())
		    return adapted_output
		except Exception as error:
			print('ERROR in SapiensGeneralization.generalization: ' + str(error))
			return original_output if 'original_output' in locals() else ''
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
