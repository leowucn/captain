import os

words_dir = '/Users/leo/work/captain/word/words'
def repair():
	files = [f for f in os.listdir(words_dir) if os.path.isfile(os.path.join(words_dir, f))]
	for file_name in files:
		extend_formt = os.path.splitext(file_name)[1]
		if extend_formt != '.txt':
			continue

		valid_lines_lst = []
		file_path = os.path.join(words_dir, file_name)
		with open(file_path) as f:
			lines = (line.rstrip() for line in f)  # All lines including the blank ones
			lines = (line for line in lines if line)  # Non-blank lines
			for line in lines:
				if is_word_line(line):
					word = line[line.find("(") + 1: line.find(")")]
					word_index = line[: line.find('.')]
					valid_lines_lst.append(word_index + '. ' + word + '\n')
				else:
					valid_lines_lst.append('usage: ' + line + '\n')
					valid_lines_lst.append('book: Harry_Potter_and_the_Sorcerer' + '\n')
					valid_lines_lst.append('date: ' + os.path.splitext(file_name)[0] + '\n')
					valid_lines_lst.append('\n')
		with open(file_path, "w") as f:
			for line in valid_lines_lst:
				f.write(line)


def is_word_line(line):
	is_number = False
	for i, c in enumerate(line):
		if c.isdigit():
			is_number = True
		elif is_number and c == '.':
			return True
		else:
			return False

repair()
